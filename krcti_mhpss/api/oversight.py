import json
import re

import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.utils import add_days, getdate, now_datetime, nowdate

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

    if scope in ("KRCTI", "Admin"):
        counsellors = frappe.get_all(
            "Has Role", filters={"role": COUNSELLOR, "parenttype": "User"}, pluck="parent", parent_doctype="User"
        )
        names = _names(set(counsellors))
        open_cases = _group(Client, "assigned_counsellor", Client.case_status != "Closed")
        done = _group(Appointment, "counsellor_id", Appointment.status == "Completed", *in_range)
        upcoming = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time >= now)
        overdue = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time < now)
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
    query = (
        frappe.qb.from_(Appointment)
        .select(Appointment.client_id, Appointment.scholar_code, Appointment.counsellor_id, Appointment.date_time, Appointment.end_time,
                Appointment.session_type, Appointment.mode_of_contact, Appointment.status)
        .where(Appointment.date_time >= f"{start} 00:00:00")
        .where(Appointment.date_time <= f"{end} 23:59:59")
        .orderby(Appointment.date_time)
        .limit(500)
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
            "scholar_code": client_codes.get(row.client_id, "Code unavailable"),
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
