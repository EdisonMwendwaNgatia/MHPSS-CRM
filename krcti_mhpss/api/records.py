import frappe
from frappe import _
from frappe.utils import get_datetime

from krcti_mhpss.api.counsellor import _client_for_user
from krcti_mhpss.utils import ADMIN_ROLE, COUNSELLOR, is_admin, is_counsellor, require_roles

CLIENT_TEXT = (
    "full_name", "phone_number", "gender", "sex", "disability_type", "institution", "course_programme",
    "county_location", "programme_stream", "referral_source", "referral_source_other",
)
CLIENT_NUMBERS = ("age", "year_of_study")
CLIENT_CHECKS = ("disability_status", "refugee_status")
CLIENT_EDIT = CLIENT_TEXT + CLIENT_NUMBERS + CLIENT_CHECKS
CLIENT_CREATE = ("scholar_code",) + CLIENT_EDIT
CASE_STATUSES = ("Active", "Follow-Up Pending", "Closed")

BASELINE_SHORT = (
    "stress_frequency", "support_availability", "coping_ability", "preferred_support_type",
    "marital_status", "conflict_exposure",
)
BASELINE_LONG = ("declined_reason", "main_concerns", "coping_behaviour", "domestic_situation", "exposure_details")
BASELINE_NUMBERS = ("wellbeing_self_rating", "dependants")
BASELINE_CHECKS = ("interest_in_support", "willingness_for_followup")
BASELINE_ALLOWED = ("consent",) + BASELINE_SHORT + BASELINE_LONG + BASELINE_NUMBERS + BASELINE_CHECKS

APPOINTMENT_FIELDS = ("date_time", "duration_minutes", "session_type", "mode_of_contact", "location", "notes")
APPOINTMENT_DETAIL = (
    "name", "client_id", "client_name", "scholar_code", "counsellor_id", "date_time", "end_time",
    "duration_minutes", "session_type", "mode_of_contact", "location", "notes", "status",
)


def _data(value):
    value = frappe.parse_json(value) if isinstance(value, str) else value
    if not isinstance(value, dict):
        frappe.throw(_("Invalid data."))
    return value


def _only(data, allowed):
    unknown = sorted(set(data) - set(allowed))
    if unknown:
        frappe.throw(_("These fields cannot be set: {0}").format(", ".join(unknown)))


def _short(value, what, limit=140):
    text = " ".join(str(value if value is not None else "").split())
    if len(text) > limit:
        frappe.throw(_("{0} is too long.").format(what))
    return text


def _long(value, what, limit=2000):
    text = str(value if value is not None else "").strip()
    if len(text) > limit:
        frappe.throw(_("{0} is too long.").format(what))
    return text


def _int(value, what):
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        frappe.throw(_("Enter a number for {0}.").format(what))


def _when(value):
    if not value:
        frappe.throw(_("Choose the date and time."))
    try:
        return str(get_datetime(value))
    except Exception:
        frappe.throw(_("Enter a valid date and time."))


# ------------------------------------------------------------- clients


@frappe.whitelist(methods=["POST"])
def save_client(name=None, data=None):
    """Register a client, or update one. Only the listed fields are accepted."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    data = _data(data)

    if name:
        doc = _client_for_user(name)
        _only(data, CLIENT_EDIT)  # the code, the counsellor and the case status are not editable here
    else:
        if is_admin() and not is_counsellor():
            frappe.throw(_("Register clients while logged in as a counsellor."))
        _only(data, CLIENT_CREATE)
        doc = frappe.new_doc("Client")
        doc.scholar_code = _short(data.get("scholar_code"), _("The code"), 40)

    for key in CLIENT_TEXT:
        if key in data:
            doc.set(key, _short(data[key], key.replace("_", " ")))
    for key in CLIENT_NUMBERS:
        if key in data:
            doc.set(key, _int(data[key], key.replace("_", " ")))
    for key in CLIENT_CHECKS:
        if key in data:
            doc.set(key, 1 if data[key] else 0)

    doc.save() if name else doc.insert()
    return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def set_case_status(name=None, status=None):
    require_roles(COUNSELLOR, ADMIN_ROLE)
    if status not in CASE_STATUSES:
        frappe.throw(_("Choose Active, Follow-Up Pending or Closed."))
    doc = _client_for_user(name)
    if doc.case_status == "Closed" and status != "Closed" and not is_admin():
        frappe.throw(_("Only the System Administrator can re-open a closed case."))
    doc.case_status = status
    doc.save()  # closing needs a completed Termination session, and the model checks it
    return {"case_status": doc.case_status}


# ---------------------------------------------------------- baseline


@frappe.whitelist(methods=["POST"])
def record_baseline(client=None, data=None):
    """The status and the who-and-when stamps are set here, never taken from the request."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    owner = _client_for_user(client)
    data = _data(data)
    _only(data, BASELINE_ALLOWED)
    if data.get("consent") not in ("Consented", "Declined"):
        frappe.throw(_("Record whether the client consented."))

    doc = frappe.new_doc("Baseline Survey")
    doc.client_id = owner.name
    doc.consent = data["consent"]
    if data["consent"] == "Declined":
        doc.declined_reason = _long(data.get("declined_reason"), _("The reason"))
    else:
        for key in BASELINE_SHORT:
            if key in data:
                doc.set(key, _short(data[key], key.replace("_", " ")))
        for key in BASELINE_LONG:
            if key in data:
                doc.set(key, _long(data[key], key.replace("_", " ")))
        for key in BASELINE_NUMBERS:
            if key in data:
                doc.set(key, _int(data[key], key.replace("_", " ")))
        for key in BASELINE_CHECKS:
            if key in data:
                doc.set(key, 1 if data[key] else 0)
        doc.status = "Completed"
    doc.insert()
    return {"name": doc.name}


# ------------------------------------------------------- appointments


def _appointment(name):
    if not name or not frappe.db.exists("Appointment", name):
        frappe.throw(_("Appointment not found."), frappe.DoesNotExistError)
    doc = frappe.get_doc("Appointment", name)
    if not doc.has_permission("read"):
        frappe.throw(_("Appointment not found."), frappe.DoesNotExistError)
    return doc


@frappe.whitelist()
def appointment_detail(name=None):
    require_roles(COUNSELLOR, ADMIN_ROLE)
    doc = _appointment(name)
    return {field: doc.get(field) for field in APPOINTMENT_DETAIL}


@frappe.whitelist(methods=["POST"])
def save_appointment(name=None, client=None, data=None):
    """Book an appointment, or change a scheduled one. The counsellor and status are never taken from the request."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    data = _data(data)
    _only(data, APPOINTMENT_FIELDS)

    if name:
        doc = _appointment(name)
        if doc.status != "Scheduled":
            frappe.throw(_("Only a scheduled appointment can be edited."))
    else:
        owner = _client_for_user(client)
        doc = frappe.new_doc("Appointment")
        doc.client_id = owner.name
        doc.counsellor_id = owner.assigned_counsellor

    if "date_time" in data or not name:
        doc.date_time = _when(data.get("date_time"))
    if "duration_minutes" in data:
        doc.duration_minutes = _int(data["duration_minutes"], _("the duration"))
    for key in ("session_type", "mode_of_contact"):
        if key in data:
            doc.set(key, _short(data[key], key.replace("_", " "), 40))
    if "location" in data:
        doc.location = _short(data["location"], _("The location"))
    if "notes" in data:
        doc.notes = _long(data["notes"], _("The notes"), 1000)

    doc.save() if name else doc.insert()
    return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def set_appointment_status(name=None, status=None):
    require_roles(COUNSELLOR, ADMIN_ROLE)
    if status not in ("Completed", "Cancelled"):
        frappe.throw(_("An appointment can be marked Completed or Cancelled."))
    doc = _appointment(name)
    if doc.status != "Scheduled":
        frappe.throw(_("Only a scheduled appointment can be completed or cancelled."))
    doc.status = status
    doc.save()
    return {"status": doc.status}