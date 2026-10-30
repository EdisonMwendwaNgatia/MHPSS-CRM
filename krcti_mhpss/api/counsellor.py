import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, nowdate

from krcti_mhpss.utils import ADMIN_ROLE, COUNSELLOR, is_overdue, normalize_phone, require_roles

CLIENT_FIELDS = (
    "name", "scholar_code", "full_name", "phone_number", "age", "gender", "disability_status",
    "disability_type", "institution", "course_programme", "year_of_study", "county_location",
    "refugee_status", "programme_stream", "referral_source", "referral_source_other",
    "assigned_counsellor", "case_status",
)
SURVEY_FIELDS = (
    "name", "status", "consent", "declined_reason", "wellbeing_self_rating", "stress_frequency",
    "main_concerns", "main_concerns_other", "support_availability", "coping_ability", "interest_in_support",
	"preferred_support_type", "willingness_for_followup", "coping_behaviour", "coping_behaviour_other", "marital_status",
    "dependants", "domestic_situation", "conflict_exposure", "exposure_details", "completed_by", "completed_on",
)
APPOINTMENT_FIELDS = [
    "name", "client_id", "client_name", "scholar_code", "counsellor_id", "counsellor_name", "date_time", "end_time",
    "session_type", "mode_of_contact", "location", "status", "notes", "overdue_notification_read",
]
SESSION_RECORD_FIELDS = [
    *APPOINTMENT_FIELDS, "session_details", "presenting_issues",
    "issue_subclassifications", "interventions_applied", "referrals_made", "urgency_level", "risk_assessment",
    "follow_up_plan", "progress_previous_goals", "followup_goals_discussed", "followup_challenges",
    "followup_new_issues", "followup_evident_changes", "followup_coping_support", "followup_support_effectiveness",
    "followup_additional_support", "followup_mood_affect", "followup_mood_other", "followup_engagement_level",
    "followup_risk_concerns", "counsellor_observations", "followup_recommendations", "followup_takeaways",
    "next_session_focus", "followup_action", "audio_recording",
]


def _attach_referrals(rows):
    names = [row.name for row in rows]
    by_parent = {name: [] for name in names}
    if names:
        referrals = frappe.get_all(
            "Appointment Referral",
            filters={"parent": ["in", names], "parenttype": "Appointment", "parentfield": "referral_history"},
            fields=["name", "parent", "from_counsellor", "to_counsellor", "reason", "referred_on"],
            order_by="idx asc",
        )
        users = {user for referral in referrals for user in (referral.from_counsellor, referral.to_counsellor)}
        user_names = {user: frappe.db.get_value("User", user, "full_name") or user for user in users}
        for referral in referrals:
            referral["from_name"] = user_names[referral.from_counsellor]
            referral["to_name"] = user_names[referral.to_counsellor]
            by_parent[referral.parent].append(referral)
    for row in rows:
        row["referral_history"] = by_parent[row.name]
    return rows


def _mine_open_cases():
    return frappe.get_list("Client", filters={"case_status": ["!=", "Closed"]}, pluck="name", limit=0)


def _client_for_user(name):
    """The client, if this user may read it. A client that is not yours looks like a missing one."""
    if not name or not frappe.db.exists("Client", name):
        frappe.throw(_("Client not found."), frappe.DoesNotExistError)
    doc = frappe.get_doc("Client", name)
    if not doc.has_permission("read"):
        frappe.throw(_("Client not found."), frappe.DoesNotExistError)
    return doc


def _flag(rows):
    for row in rows:
        # API detail responses may be plain dicts, while frappe.get_list returns
        # frappe._dict rows. Support both representations.
        get = row.get if hasattr(row, "get") else lambda key: getattr(row, key, None)
        row["overdue"] = is_overdue(get("status"), get("date_time"))
    return rows


@frappe.whitelist()
def search_clients(term=None, limit=20):
    """FR-CR-003: find a client by code, name, phone number or institution."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    term = " ".join(str(term or "").split())[:60]
    if len(term) < 2:
        return []
    like = f"%{term}%"
    or_filters = [[f, "like", like] for f in ("name", "scholar_code", "full_name", "phone_number", "institution")]
    digits = normalize_phone(term)
    if len(digits) >= 6:
        or_filters.append(["phone_number", "like", f"%{digits[-9:]}%"])
    return frappe.get_list(
        "Client",
        or_filters=or_filters,
        fields=["name", "scholar_code", "full_name", "phone_number", "institution", "case_status"],
        order_by="full_name asc",
        limit=min(int(limit or 20), 50),
    )

@frappe.whitelist()
def list_clients(status=None, start=0, page_length=20):
    """The counsellor's own clients. The total is counted from what they may see, never the whole table."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    filters = {}
    if status in ("Active", "Follow-Up Pending", "Closed"):
        filters["case_status"] = status
    rows = frappe.get_list(
        "Client",
        filters=filters,
        fields=["name", "scholar_code", "full_name", "phone_number", "institution", "case_status", "programme_stream"],
        order_by="modified desc",
        start=int(start or 0),
        limit=min(int(page_length or 20), 50),
    )
    total = len(frappe.get_list("Client", filters=filters, pluck="name", limit=0))
    return {"data": rows, "total": total}


@frappe.whitelist()
def client_profile(name=None):
    """The client record with the baseline survey (read-only) and the session history."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    doc = _client_for_user(name)
    survey_name = frappe.db.get_value("Baseline Survey", {"client_id": doc.name}, "name")
    survey = frappe.get_doc("Baseline Survey", survey_name) if survey_name else None
    appointments = frappe.get_list(
        "Appointment", filters={"client_id": doc.name}, fields=APPOINTMENT_FIELDS,
        order_by="date_time desc", limit=100,
    )
    appointments = _attach_referrals(appointments)
    client_data = {f: doc.get(f) for f in CLIENT_FIELDS}
    client_data["registered_by"] = doc.owner
    client_data["registered_by_name"] = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    client_data["assigned_counsellor_name"] = (
        frappe.db.get_value("User", doc.assigned_counsellor, "full_name") or doc.assigned_counsellor
        if doc.assigned_counsellor else ""
    )
    return {
        "client": client_data,
        "survey": {f: survey.get(f) for f in SURVEY_FIELDS} if survey else None,
        "appointments": _flag(appointments),
    }


@frappe.whitelist()
def my_appointments(date_from=None, date_to=None):
    """FR-AS-003: the list behind the calendar. A counsellor sees only their own."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    start = getdate(date_from or nowdate())
    end = getdate(date_to or add_days(start, 14))
    if end < start or (end - start).days > 120:
        frappe.throw(_("Choose a date range of up to 120 days."))
    rows = frappe.get_list(
        "Appointment",
        filters=[["counsellor_id", "=", frappe.session.user], ["date_time", ">=", f"{start} 00:00:00"], ["date_time", "<=", f"{end} 23:59:59"]],
        fields=APPOINTMENT_FIELDS,
        order_by="date_time asc",
        limit=0,
    )
    overdue = frappe.get_list(
        "Appointment",
        filters=[["counsellor_id", "=", frappe.session.user], ["status", "=", "Scheduled"], ["date_time", "<", now_datetime()]],
        pluck="name",
        limit=0,
    )
    return {"appointments": _attach_referrals(_flag(rows)), "overdue_total": len(overdue)}


@frappe.whitelist()
def my_followups():
    """Scheduled follow-up appointments, with overdue status derived from their set appointment date."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    filters = {"counsellor_id": frappe.session.user, "session_type": "Follow-Up", "status": "Scheduled"}
    rows = frappe.get_list(
        "Appointment", filters=filters, fields=APPOINTMENT_FIELDS, order_by="date_time asc", limit=0,
    )
    flagged = _attach_referrals(_flag(rows))
    return {"followups": flagged, "overdue_total": sum(bool(row.overdue) for row in flagged)}


@frappe.whitelist()
def my_session_records():
    """Completed appointment records in chronological order for the signed-in counsellor."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    rows = frappe.get_list(
        "Appointment", filters={"counsellor_id": frappe.session.user, "status": "Completed"}, fields=SESSION_RECORD_FIELDS,
        order_by="date_time desc", limit=500,
    )
    return _attach_referrals(rows)


@frappe.whitelist()
def home():
    require_roles(COUNSELLOR)
    user = frappe.session.user
    mine = _mine_open_cases()
    settled = (
        set(frappe.get_all("Baseline Survey", filters={"client_id": ["in", mine], "status": ["in", ["Completed", "Declined"]]}, pluck="client_id"))
        if mine
        else set()
    )
    today = nowdate()
    now = now_datetime()
    scheduled = {"counsellor_id": user, "status": "Scheduled"}
    upcoming_filters = {**scheduled, "date_time": [">=", now]}
    followup_filters = {**scheduled, "session_type": "Follow-Up"}
    recent_sessions = frappe.get_all(
        "Appointment",
        filters={"counsellor_id": user, "status": "Completed"},
        fields=APPOINTMENT_FIELDS,
        order_by="date_time desc",
        limit=5,
    )
    followups = frappe.get_all(
        "Appointment",
        filters=followup_filters,
        fields=APPOINTMENT_FIELDS,
        order_by="date_time asc",
        limit=5,
    )
    overdue_notifications = frappe.get_all(
        "Appointment",
        filters={
            **followup_filters,
            "date_time": ["<", now],
            "overdue_notification_read": 0,
        },
        fields=APPOINTMENT_FIELDS,
        order_by="date_time asc",
        limit=0,
    )
    today_rows = frappe.get_all(
        "Appointment",
        filters={**scheduled, "date_time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
        fields=APPOINTMENT_FIELDS, order_by="date_time asc",
    )
    upcoming = frappe.get_all(
        "Appointment", filters=upcoming_filters,
        fields=APPOINTMENT_FIELDS, order_by="date_time asc", limit=5,
    )
    return {
        "active_clients": len(mine),
        "baselines_outstanding": len([c for c in mine if c not in settled]),
        "today": _attach_referrals(today_rows),
        "overdue": frappe.db.count("Appointment", {**scheduled, "date_time": ["<", now]}),
        "upcoming_count": frappe.db.count("Appointment", upcoming_filters),
        "upcoming": _attach_referrals(upcoming),
        "sessions_conducted": frappe.db.count("Appointment", {"counsellor_id": user, "status": "Completed"}),
        "followups_pending": frappe.db.count("Appointment", followup_filters),
        "overdue_followups": frappe.db.count("Appointment", {**followup_filters, "date_time": ["<", now], "overdue_notification_read": 0}),
        "recent_sessions": _attach_referrals(recent_sessions),
        "followups": _attach_referrals(_flag(followups)),
        "overdue_notifications": _flag(overdue_notifications),
    }


@frappe.whitelist(methods=["POST"])
def mark_overdue_followup_notifications_read(name=None):
    require_roles(COUNSELLOR)
    user = frappe.session.user
    filters = {
        "counsellor_id": user,
        "session_type": "Follow-Up",
        "status": "Scheduled",
        "date_time": ["<", now_datetime()],
        "overdue_notification_read": 0,
    }
    if name:
        filters["name"] = name
        if not frappe.db.exists("Appointment", filters):
            frappe.throw(_("Overdue follow-up notification not found."), frappe.PermissionError)
        frappe.db.set_value("Appointment", name, "overdue_notification_read", 1, update_modified=False)
        return {"ok": True}

    names = frappe.get_all("Appointment", filters=filters, pluck="name", limit=0)
    for appointment in names:
        frappe.db.set_value("Appointment", appointment, "overdue_notification_read", 1, update_modified=False)
    return {"ok": True, "count": len(names)}


def notify_overdue_followups():
    """Email each counsellor once when one of their scheduled follow-ups becomes overdue."""
    now = now_datetime()
    rows = frappe.get_all(
        "Appointment",
        filters={
            "session_type": "Follow-Up",
            "status": "Scheduled",
            "date_time": ["<", now],
            "overdue_notification_emailed": 0,
        },
        fields=["name", "counsellor_id", "date_time"],
        limit=0,
    )
    for row in rows:
        email = frappe.db.get_value("User", row.counsellor_id, "email")
        if not email:
            continue
        try:
            frappe.sendmail(
                recipients=email,
                subject=_("Overdue follow-up appointment"),
                message=_("A follow-up appointment ({0}) is overdue. Sign in to the MHPSS case management system to review it.").format(row.name),
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), _("Could not email an overdue follow-up notification"))
            continue
        frappe.db.set_value("Appointment", row.name, "overdue_notification_emailed", 1, update_modified=False)
