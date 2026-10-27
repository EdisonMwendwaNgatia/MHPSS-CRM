import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, nowdate

from krcti_mhpss.utils import ADMIN_ROLE, COUNSELLOR, is_overdue, normalize_phone, require_roles

CLIENT_FIELDS = (
    "name", "scholar_code", "full_name", "phone_number", "age", "gender", "sex", "disability_status",
    "disability_type", "institution", "course_programme", "year_of_study", "county_location",
    "refugee_status", "programme_stream", "referral_source", "referral_source_other",
    "assigned_counsellor", "case_status",
)
SURVEY_FIELDS = (
    "name", "status", "consent", "declined_reason", "wellbeing_self_rating", "stress_frequency",
    "main_concerns", "support_availability", "coping_ability", "interest_in_support",
    "preferred_support_type", "willingness_for_followup", "coping_behaviour", "marital_status",
    "dependants", "domestic_situation", "conflict_exposure", "exposure_details", "completed_by", "completed_on",
)
APPOINTMENT_FIELDS = [
    "name", "client_id", "client_name", "counsellor_id", "counsellor_name", "date_time", "end_time",
    "session_type", "mode_of_contact", "location", "status", "notes",
]


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
        row["overdue"] = is_overdue(row.status, row.date_time)
    return rows


@frappe.whitelist()
def search_clients(term=None, limit=20):
    """FR-CR-003: find a client by code, name, phone number or institution."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    term = " ".join(str(term or "").split())[:60]
    if len(term) < 2:
        return []
    like = f"%{term}%"
    or_filters = [[f, "like", like] for f in ("scholar_code", "full_name", "phone_number", "institution")]
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
    return {
        "client": {f: doc.get(f) for f in CLIENT_FIELDS},
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
        filters=[["date_time", ">=", f"{start} 00:00:00"], ["date_time", "<=", f"{end} 23:59:59"]],
        fields=APPOINTMENT_FIELDS,
        order_by="date_time asc",
        limit=0,
    )
    overdue = frappe.get_list(
        "Appointment",
        filters=[["status", "=", "Scheduled"], ["date_time", "<", now_datetime()]],
        pluck="name",
        limit=0,
    )
    return {"appointments": _flag(rows), "overdue_total": len(overdue)}


@frappe.whitelist()
def home():
    require_roles(COUNSELLOR)
    user = frappe.session.user
    open_cases = {"assigned_counsellor": user, "case_status": ["!=", "Closed"]}
    mine = frappe.get_all("Client", filters=open_cases, pluck="name")
    settled = (
        set(frappe.get_all("Baseline Survey", filters={"client_id": ["in", mine], "status": ["in", ["Completed", "Declined"]]}, pluck="client_id"))
        if mine
        else set()
    )
    today = nowdate()
    scheduled = {"counsellor_id": user, "status": "Scheduled"}
    return {
        "active_clients": len(mine),
        "baselines_outstanding": len([c for c in mine if c not in settled]),
        "today": frappe.get_all(
            "Appointment",
            filters={**scheduled, "date_time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
            fields=APPOINTMENT_FIELDS, order_by="date_time asc",
        ),
        "overdue": frappe.db.count("Appointment", {**scheduled, "date_time": ["<", now_datetime()]}),
        "upcoming": frappe.get_all(
            "Appointment", filters={**scheduled, "date_time": [">=", now_datetime()]},
            fields=APPOINTMENT_FIELDS, order_by="date_time asc", limit=5,
        ),
    }