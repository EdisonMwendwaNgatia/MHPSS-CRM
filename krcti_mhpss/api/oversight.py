import json
import re

import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.utils import add_days, cint, getdate, now_datetime, nowdate

from krcti_mhpss.utils import ADMIN_ROLE, ADMIN_ROLES, COUNSELLOR, KRCTI_PM, MODES, WOC_PM, require_roles, roles_of


WOC_STREAM = "Scholarship/Education"
PM_NOTIFICATION_APP = "krcti_mhpss"
PM_NOTIFICATION_TITLES = ("Appointment booked", "Session completed")


def _range(date_from, date_to):
    end = getdate(date_to or nowdate())
    start = getdate(date_from or add_days(end, -30))
    if start > end or (end - start).days > 400:
        frappe.throw(_("Choose a date range of up to 400 days."))
    return start, end


def _scope():
    roles = roles_of()
    if WOC_PM in roles and not ({KRCTI_PM, *ADMIN_ROLES} & roles):
        return "WoC"
    return "KRCTI" if KRCTI_PM in roles else "Admin"


def _conditions(table, scope, client_field="client_id"):
    if scope != "WoC":
        return []
    Client = frappe.qb.DocType("Client")
    client_names = frappe.qb.from_(Client).select(Client.name).where(Client.programme_stream == WOC_STREAM)
    return [getattr(table, client_field).isin(client_names)]


def _programme_client(name):
    client = frappe.db.get_value("Client", name, ["name", "programme_stream"], as_dict=True)
    if not client or (_scope() == "WoC" and client.programme_stream != WOC_STREAM):
        frappe.throw(_("Client not found in your programme."), frappe.PermissionError)
    return client


def _counsellor_names():
    # Programme managers in either programme can oversee every counsellor.
    # Client and appointment data remain programme-scoped by their own queries.
    return set(frappe.get_all("Has Role", filters={"role": COUNSELLOR, "parenttype": "User"}, pluck="parent", limit=0))


def _programme_counsellor(user):
    if user not in _counsellor_names():
        frappe.throw(_("Counsellor not found in your programme."), frappe.PermissionError)
    return user


def _activity_scope_log(row, scope):
    if scope != "WoC":
        return True
    if row.module == "Authentication":
        return row.actor in _counsellor_names()
    if row.module in ("User management", "Role management"):
        return row.affected_record in _counsellor_names()
    record = row.affected_record
    if not record:
        return False
    if frappe.db.exists("Appointment", record):
        client_name = frappe.db.get_value("Appointment", record, "client_id")
    elif frappe.db.exists("Client", record):
        client_name = record
    else:
        return False
    return bool(client_name and frappe.db.get_value("Client", client_name, "programme_stream") == WOC_STREAM)


@frappe.whitelist()
def programme_clients(search=None, start=0, page_length=50):
    require_roles(KRCTI_PM, WOC_PM)
    start, page_length = max(0, cint(start)), max(1, min(cint(page_length) or 50, 100))
    filters = {}
    if _scope() == "WoC":
        filters["programme_stream"] = WOC_STREAM
    search = " ".join(str(search or "").split())[:80]
    or_filters = None
    if search:
        like = f"%{search}%"
        or_filters = [["Client", "scholar_code", "like", like], ["Client", "full_name", "like", like], ["Client", "phone_number", "like", like]]
    total = frappe.db.count("Client", filters=filters)
    rows = frappe.get_all("Client", filters=filters, or_filters=or_filters,
        fields=["name", "full_name", "scholar_code", "programme_stream", "case_status", "assigned_counsellor", "institution", "modified"],
        order_by="modified desc", start=start, page_length=page_length)
    names = _names({row.assigned_counsellor for row in rows if row.assigned_counsellor})
    for row in rows:
        row["counsellor_name"] = names.get(row.assigned_counsellor, "Unassigned")
    if search:
        total = len(frappe.get_all("Client", filters=filters, or_filters=or_filters, pluck="name", limit=0))
    return {"clients": rows, "total": total}


@frappe.whitelist()
def programme_client_detail(name=None):
    require_roles(KRCTI_PM, WOC_PM)
    _programme_client(name)
    client = frappe.get_doc("Client", name).as_dict()
    appointments = frappe.get_all("Appointment", filters={"client_id": name}, fields=[
        "name", "scholar_code", "counsellor_id", "counsellor_name", "date_time", "session_type", "mode_of_contact", "status",
        "session_details", "presenting_issues", "issue_subclassifications", "interventions_applied", "referrals_made", "urgency_level", "risk_assessment",
        "needs_follow_up", "follow_up_plan", "followup_wellbeing_rating", "followup_stress_frequency", "followup_new_presenting_issues",
        "followup_new_issues_present", "followup_new_issues", "followup_evident_changes_present", "followup_evident_changes",
        "followup_goals_discussed", "progress_previous_goals", "followup_challenges", "followup_coping_support", "followup_support_effectiveness",
        "followup_additional_support", "followup_mood_affect", "followup_engagement_level", "followup_risk_concerns", "followup_recommendations",
        "followup_takeaways", "next_session_focus", "followup_action", "audio_recording"], order_by="date_time asc", limit=0)
    names = _names({row.counsellor_id for row in appointments if row.counsellor_id})
    appointment_names = [row.name for row in appointments]
    actions = frappe.get_all("Appointment Management Event", filters={"parent": ["in", appointment_names]} if appointment_names else {"parent": ""},
        fields=["parent", "event_type", "from_counsellor", "to_counsellor", "manager", "reason", "event_time"], order_by="event_time asc", limit=0)
    action_users = _names({user for row in actions for user in (row.from_counsellor, row.to_counsellor, row.manager) if user})
    actions_by_parent = {}
    for action in actions:
        action["from_name"] = action_users.get(action.from_counsellor, action.from_counsellor)
        action["to_name"] = action_users.get(action.to_counsellor, action.to_counsellor)
        action["manager_name"] = action_users.get(action.manager, action.manager)
        actions_by_parent.setdefault(action.parent, []).append(action)
    for row in appointments:
        row["counsellor_name"] = names.get(row.counsellor_id, row.counsellor_name or row.counsellor_id)
        row["management_history"] = actions_by_parent.get(row.name, [])
    referral_rows = frappe.get_all("Appointment Referral", filters={"parent": ["in", appointment_names], "parenttype": "Appointment", "parentfield": "referral_history"} if appointment_names else {"parent": ""},
        fields=["parent", "from_counsellor", "to_counsellor", "reason", "referred_on"], order_by="idx asc", limit=0)
    referral_users = _names({user for row in referral_rows for user in (row.from_counsellor, row.to_counsellor) if user})
    referrals_by_parent = {}
    for referral in referral_rows:
        referral["from_name"] = referral_users.get(referral.from_counsellor, referral.from_counsellor)
        referral["to_name"] = referral_users.get(referral.to_counsellor, referral.to_counsellor)
        referrals_by_parent.setdefault(referral.parent, []).append(referral)
    for row in appointments:
        row["referral_history"] = referrals_by_parent.get(row.name, [])
    client["case_history"] = appointments
    return client


@frappe.whitelist()
def programme_counsellors():
    require_roles(KRCTI_PM, WOC_PM)
    names = _counsellor_names()
    return frappe.get_all("User", filters={"name": ["in", sorted(names)]},
        fields=["name", "full_name", "enabled", "last_login", "creation", "krcti_programme_scope"],
        order_by="full_name asc", limit=0) if names else []


@frappe.whitelist(methods=["POST"])
def programme_save_counsellor(email=None, first_name=None, last_name=None, password=None, user=None, action="create"):
    require_roles(KRCTI_PM, WOC_PM)
    scope = _scope()
    if action == "create":
        email = " ".join(str(email or "").split()).lower()
        first_name = " ".join(str(first_name or "").split())
        if not email or "@" not in email or not first_name or len(str(password or "")) < 8:
            frappe.throw(_("Enter a valid email, first name and password of at least 8 characters."))
        if frappe.db.exists("User", email):
            frappe.throw(_("A user with this email already exists."))
        doc = frappe.new_doc("User")
        doc.update({"email": email, "first_name": first_name, "last_name": " ".join(str(last_name or "").split()),
                    "user_type": "System User", "enabled": 1, "send_welcome_email": 0,
                    "new_password": password, "krcti_programme_scope": scope})
        doc.set("roles", [])
        doc.append("roles", {"role": COUNSELLOR})
        doc.insert(ignore_permissions=True)
        return {"user": doc.name, "action": "created"}
    _programme_counsellor(user)
    if action not in ("deactivate", "remove"):
        frappe.throw(_("Choose create, deactivate or remove."))
    doc = frappe.get_doc("User", user)
    doc.enabled = 0
    doc.save(ignore_permissions=True)
    # Remove means retire the login while retaining links and historical attribution.
    return {"user": user, "action": "deactivated"}


@frappe.whitelist()
def programme_sessions():
    require_roles(KRCTI_PM, WOC_PM)
    filters = {"status": "Scheduled"}
    if _scope() == "WoC":
        client_names = frappe.get_all("Client", filters={"programme_stream": WOC_STREAM}, pluck="name", limit=0)
        if not client_names:
            return []
        filters["client_id"] = ["in", client_names]
    rows = frappe.get_all("Appointment", filters=filters, fields=["name", "client_id", "client_name", "scholar_code", "counsellor_id", "counsellor_name", "date_time", "session_type", "mode_of_contact"], order_by="date_time asc", limit=0)
    now = now_datetime()
    for row in rows:
        row["counsellor_name"] = frappe.db.get_value("User", row.counsellor_id, "full_name") or row.counsellor_id
        row["overdue"] = row.date_time < now
    return rows


@frappe.whitelist(methods=["POST"])
def programme_manage_session(name=None, action=None, counsellor=None, reason=None):
    require_roles(KRCTI_PM, WOC_PM)
    appointment = frappe.get_doc("Appointment", name)
    _programme_client(appointment.client_id)
    if appointment.status != "Scheduled":
        frappe.throw(_("Only scheduled sessions can be changed."))
    reason = " ".join(str(reason or "").split())
    if len(reason) < 3 or len(reason) > 2000:
        frappe.throw(_("Enter a reason of 3 to 2000 characters."))
    if action == "reassign":
        _programme_counsellor(counsellor)
        if not frappe.db.get_value("User", counsellor, "enabled"):
            frappe.throw(_("Choose an active counsellor."))
        if counsellor == appointment.counsellor_id:
            frappe.throw(_("Choose a different counsellor."))
        original = appointment.counsellor_id
        appointment.counsellor_id = counsellor
        event = {"event_type": "Reassigned", "from_counsellor": original, "to_counsellor": counsellor}
    elif action == "cancel":
        original = appointment.counsellor_id
        appointment.status = "Cancelled"
        event = {"event_type": "Cancelled", "from_counsellor": original, "to_counsellor": None}
    else:
        frappe.throw(_("Choose reassign or cancel."))
    appointment.append("management_history", {**event, "manager": frappe.session.user, "reason": reason, "event_time": now_datetime()})
    frappe.flags.allow_programme_session_management = True
    frappe.flags.programme_session_action = True
    appointment.save(ignore_permissions=True)
    frappe.flags.allow_programme_session_management = False
    frappe.flags.programme_session_action = False
    from krcti_mhpss.permissions import write_audit_log
    write_audit_log("Appointment reassigned" if action == "reassign" else "Appointment cancelled", appointment.name, "Session management", details=reason)
    return {"name": appointment.name, "status": appointment.status, "counsellor_id": appointment.counsellor_id}


@frappe.whitelist()
def programme_counsellor_activity(user=None, start=0, page_length=100):
    require_roles(KRCTI_PM, WOC_PM)
    _programme_counsellor(user)
    start, page_length = max(0, cint(start)), max(1, min(cint(page_length) or 100, 200))
    allowed = {"User logged in", "User logged out", "User account created", "User account updated", "User account activated", "User account deactivated", "User role changed", "Client registered", "Client updated", "Appointment booked", "Appointment updated", "Session completed", "Appointment cancelled", "Appointment reassigned"}
    rows = frappe.get_all("KRCTI Audit Log", filters={"action": ["in", sorted(allowed)]}, or_filters=[["actor", "=", user], ["affected_record", "=", user]], fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"], order_by="creation desc", limit=0)
    rows = [row for row in rows if row.action in allowed and _activity_scope_log(row, _scope())]
    actor_names = _names({row.actor for row in rows if row.actor})
    for row in rows:
        row["actor_name"] = actor_names.get(row.actor, row.actor)
    return {"logs": rows[start:start + page_length], "total": len(rows)}


def _group(table, column, *conditions):
    field = getattr(table, column)
    query = frappe.qb.from_(table).select(field, Count("*").as_("n")).groupby(field)
    for condition in conditions:
        query = query.where(condition)
    return {row[column] or "Unspecified": row["n"] for row in query.run(as_dict=True)}


def _names(users):
    rows = frappe.get_all("User", filters={"name": ["in", sorted(users)]}, fields=["name", "full_name"]) if users else []
    return {row.name: row.full_name for row in rows}


def notify_programme_managers(appointment, event):
    """Create personal Frappe notifications for PMs whose programme includes this client."""
    if event not in PM_NOTIFICATION_TITLES:
        return
    client = frappe.db.get_value(
        "Client", appointment.client_id, ["programme_stream", "scholar_code"], as_dict=True
    )
    if not client:
        return
    manager_roles = [KRCTI_PM]
    if client.programme_stream == WOC_STREAM:
        manager_roles.append(WOC_PM)
    recipients = frappe.get_all(
        "Has Role", filters={"role": ["in", manager_roles], "parenttype": "User"}, pluck="parent",
        parent_doctype="User",
    )
    code = client.scholar_code or appointment.scholar_code or "Scholar code unavailable"
    when = str(appointment.date_time or now_datetime())
    description = f"{code} · {appointment.session_type} · {when}"
    for user in set(recipients):
        if not frappe.db.get_value("User", user, "enabled"):
            continue
        notification = frappe.new_doc("Notification Log")
        notification.update({
            "for_user": user,
            "from_user": frappe.session.user,
            "app": PM_NOTIFICATION_APP,
            "title": event,
            "subject": event,
            "description": description,
            "email_content": description,
            "document_type": "Appointment",
            "document_name": appointment.name,
        })
        notification.insert(ignore_permissions=True)


@frappe.whitelist()
def programme_notifications():
    """Unread appointment and session activity for the logged-in programme manager."""
    require_roles(KRCTI_PM, WOC_PM)
    rows = frappe.get_all(
        "Notification Log",
        filters={
            "for_user": frappe.session.user,
            "read": 0,
            "app": PM_NOTIFICATION_APP,
            "title": ["in", PM_NOTIFICATION_TITLES],
            "document_type": "Appointment",
        },
        fields=["name", "title", "description", "document_name", "creation"],
        order_by="creation desc",
        limit=100,
    )
    scope = _scope()
    if scope == "WoC":
        rows = [
            row for row in rows
            if frappe.db.get_value(
                "Appointment", row.document_name, ["client_id"], as_dict=True
            )
            and frappe.db.get_value(
                "Client", frappe.db.get_value("Appointment", row.document_name, "client_id"), "programme_stream"
            ) == WOC_STREAM
        ]
    return {"notifications": rows, "unread_count": len(rows)}


@frappe.whitelist(methods=["POST"])
def mark_programme_notifications_read(name=None):
    """Mark one or all programme notifications read for the current manager."""
    require_roles(KRCTI_PM, WOC_PM)
    filters = {
        "for_user": frappe.session.user,
        "read": 0,
        "app": PM_NOTIFICATION_APP,
        "title": ["in", PM_NOTIFICATION_TITLES],
    }
    names = [name] if name else frappe.get_all("Notification Log", filters=filters, pluck="name")
    changed = 0
    for notification_name in names:
        log = frappe.db.get_value("Notification Log", notification_name, ["for_user", "app", "title", "read"], as_dict=True)
        if not log or log.for_user != frappe.session.user or log.app != PM_NOTIFICATION_APP or log.title not in PM_NOTIFICATION_TITLES:
            continue
        frappe.db.set_value("Notification Log", notification_name, "read", 1, update_modified=False)
        changed += 1
    return {"marked_read": changed}


def _referral_counts(Appointment, scope, first, last):
    query = frappe.qb.from_(Appointment).select(Appointment.referrals_made)
    for condition in [Appointment.status == "Completed", Appointment.date_time >= first, Appointment.date_time <= last, *_conditions(Appointment, scope)]:
        query = query.where(condition)
    counts = {}
    for row in query.run(as_dict=True):
        raw = row.referrals_made
        if not raw:
            continue
        try:
            values = json.loads(raw)
        except (TypeError, ValueError):
            values = [part.strip() for part in re.split(r"[,;\n]+", str(raw))]
        if not isinstance(values, list):
            values = [values]
        for value in values:
            label = str(value).strip()
            if label:
                counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].lower())))


def _appointment_trends(scope, first, last):
    params = [first, last]
    client_filter = ""
    if scope == "WoC":
        client_filter = " AND client_id IN (SELECT name FROM `tabClient` WHERE programme_stream = %s)"
        params.append(WOC_STREAM)
    rows = frappe.db.sql(
        """SELECT DATE(date_time) AS day, status, COUNT(*) AS n
           FROM `tabAppointment`
           WHERE date_time >= %s AND date_time <= %s""" + client_filter +
        " GROUP BY DATE(date_time), status ORDER BY day",
        params,
        as_dict=True,
    )
    by_day = {}
    for row in rows:
        day = str(row.day)
        by_day.setdefault(day, {})[row.status or "Unspecified"] = row.n
    return [{"date": day, "statuses": statuses, "total": sum(statuses.values())} for day, statuses in sorted(by_day.items())]


@frappe.whitelist()
def programme_summary(date_from=None, date_to=None):
    """Return aggregate-only monitoring data for programme managers."""
    require_roles(KRCTI_PM, WOC_PM, ADMIN_ROLE)
    scope = _scope()
    start, end = _range(date_from, date_to)
    first, last = f"{start} 00:00:00", f"{end} 23:59:59"
    Client, Appointment, Survey = (frappe.qb.DocType(n) for n in ("Client", "Appointment", "Baseline Survey"))
    client_scope = _conditions(Client, scope, "name")
    appointment_scope = _conditions(Appointment, scope)
    survey_scope = _conditions(Survey, scope)
    in_range = (Appointment.date_time >= first, Appointment.date_time <= last)
    baseline_range = (Survey.creation >= first, Survey.creation <= last)
    now = now_datetime()

    caseload = _group(Client, "case_status", *client_scope)
    sessions = _group(Appointment, "mode_of_contact", Appointment.status == "Completed", *in_range, *appointment_scope)
    pending_followups = _group(
        Appointment, "status", Appointment.session_type == "Follow-Up", Appointment.status == "Scheduled",
        Appointment.date_time >= now, *appointment_scope,
    ).get("Scheduled", 0)

    result = {
        "scope": scope,
        "range": {"from": str(start), "to": str(end)},
        "caseload": {s: caseload.get(s, 0) for s in ("Active", "Follow-Up Pending", "Closed")},
        "pending_followups": pending_followups,
        "sessions_by_mode": {mode: sessions.get(mode, 0) for mode in MODES},
        "appointments_by_status": _group(Appointment, "status", *in_range, *appointment_scope),
        "appointment_trends": _appointment_trends(scope, first, last),
        "baseline": _group(Survey, "status", *baseline_range, *survey_scope),
        "referrals": _referral_counts(Appointment, scope, first, last),
        "by_counsellor": None,
    }

    names = _names(_counsellor_names())
    open_cases = _group(Client, "assigned_counsellor", Client.case_status != "Closed", *client_scope)
    done = _group(Appointment, "counsellor_id", Appointment.status == "Completed", *in_range, *appointment_scope)
    upcoming = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time >= now, *appointment_scope)
    overdue = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time < now, *appointment_scope)
    result["by_counsellor"] = sorted(
        ({
            "counsellor": names[user],
            "active_caseload": open_cases.get(user, 0),
            "completed_in_range": done.get(user, 0),
            "upcoming": upcoming.get(user, 0),
            "overdue": overdue.get(user, 0),
        } for user in names),
        key=lambda row: row["counsellor"],
    )
    return result


@frappe.whitelist()
def programme_calendar(date_from=None, date_to=None):
    """Calendar feed with participant codes but no names or notes, programme-scoped."""
    require_roles(KRCTI_PM, WOC_PM, ADMIN_ROLE)
    scope = _scope()
    start, end = _range(date_from, date_to)
    Appointment = frappe.qb.DocType("Appointment")
    date_condition = (
        ((Appointment.date_time >= f"{start} 00:00:00") & (Appointment.date_time <= f"{end} 23:59:59"))
        | ((Appointment.status == "Scheduled") & (Appointment.date_time < f"{start} 00:00:00"))
    )
    query = (
        frappe.qb.from_(Appointment)
        .select(Appointment.name, Appointment.client_id, Appointment.scholar_code, Appointment.counsellor_id, Appointment.date_time, Appointment.end_time,
                Appointment.session_type, Appointment.mode_of_contact, Appointment.status)
        .where(date_condition)
        .orderby(Appointment.date_time)
    )
    for condition in _conditions(Appointment, scope):
        query = query.where(condition)
    rows = query.run(as_dict=True)
    names = _names({row.counsellor_id for row in rows})
    now = now_datetime()
    client_codes = {}
    for row in rows:
        if row.client_id not in client_codes:
            client_codes[row.client_id] = row.scholar_code or frappe.db.get_value("Client", row.client_id, "scholar_code") or "Code unavailable"
    return [
        {
            "name": row.name,
            "client_id": row.client_id,
            "scholar_code": client_codes.get(row.client_id, "Code unavailable"),
            "counsellor_id": row.counsellor_id,
            "counsellor": names.get(row.counsellor_id, ""),
            "start": row.date_time,
            "end": row.end_time,
            "session_type": row.session_type,
            "mode": row.mode_of_contact,
            "status": row.status,
            "overdue": row.status == "Scheduled" and row.date_time < now,
        }
        for row in rows
    ]
