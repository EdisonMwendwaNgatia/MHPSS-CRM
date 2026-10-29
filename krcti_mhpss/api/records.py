import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime

from krcti_mhpss.api.counsellor import _client_for_user, _flag
from krcti_mhpss.utils import ADMIN_ROLE, COUNSELLOR, is_admin, is_counsellor, require_roles

CLIENT_TEXT = (
    "full_name", "phone_number", "gender", "disability_type", "institution", "institution_county", "course_programme",
    "county_location", "programme_stream", "referral_source", "referral_source_other",
)
CLIENT_NUMBERS = ("age", "year_of_study")
CLIENT_CHECKS = ("disability_status", "refugee_status")
CLIENT_EDIT = CLIENT_TEXT + CLIENT_NUMBERS + CLIENT_CHECKS
CLIENT_CREATE = CLIENT_EDIT
CASE_STATUSES = ("Active", "Follow-Up Pending", "Closed")

BASELINE_SHORT = (
	"stress_frequency", "support_availability", "coping_ability", "coping_behaviour", "preferred_support_type",
	"marital_status", "conflict_exposure",
)
BASELINE_LONG = ("declined_reason", "main_concerns", "main_concerns_other", "coping_behaviour_other", "domestic_situation", "exposure_details")
BASELINE_NUMBERS = ("wellbeing_self_rating", "dependants")
BASELINE_CHECKS = ("interest_in_support", "willingness_for_followup")
BASELINE_ALLOWED = ("consent",) + BASELINE_SHORT + BASELINE_LONG + BASELINE_NUMBERS + BASELINE_CHECKS

APPOINTMENT_FIELDS = ("date_time", "duration_minutes", "session_type", "mode_of_contact", "location", "notes")
APPOINTMENT_DETAIL = (
    "name", "client_id", "client_name", "scholar_code", "counsellor_id", "counsellor_name", "date_time", "end_time",
    "duration_minutes", "session_type", "mode_of_contact", "location", "notes", "status",
    "session_details", "presenting_issues", "issue_subclassifications", "interventions_applied",
    "referrals_made", "urgency_level", "risk_assessment", "follow_up_plan",
    "progress_previous_goals", "counsellor_observations", "next_session_focus", "audio_recording",
)


def _referral_rows(appointment_name):
    rows = frappe.get_all(
        "Appointment Referral",
        filters={"parent": appointment_name, "parenttype": "Appointment", "parentfield": "referral_history"},
        fields=["name", "from_counsellor", "to_counsellor", "reason", "referred_on"],
        order_by="idx asc",
    )
    for row in rows:
        row["from_name"] = frappe.db.get_value("User", row.from_counsellor, "full_name") or row.from_counsellor
        row["to_name"] = frappe.db.get_value("User", row.to_counsellor, "full_name") or row.to_counsellor
    return rows
SESSION_RECORD_TEXT = (
    "session_details", "presenting_issues", "issue_subclassifications", "interventions_applied",
    "referrals_made", "risk_assessment", "follow_up_plan", "progress_previous_goals",
    "counsellor_observations", "next_session_focus",
)
SESSION_RECORD_REQUIRED = (
    "session_details", "presenting_issues", "interventions_applied", "risk_assessment", "follow_up_plan",
)
SESSION_URGENCY_LEVELS = ("Low", "Moderate", "High", "Immediate")


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
    if owner.case_status == "Closed":
        frappe.throw(_("Closed cases are read-only."))
    data = _data(data)
    _only(data, BASELINE_ALLOWED)
    if data.get("consent") not in ("Consented", "Declined"):
        frappe.throw(_("Record whether the client consented."))
    if data.get("consent") == "Consented" and data.get("coping_behaviour") == "Other" and not _long(
        data.get("coping_behaviour_other"), _("The other coping mechanism")
    ):
        frappe.throw(_("Describe the other coping mechanism."))
    concerns = [item.strip() for item in str(data.get("main_concerns") or "").split(",")]
    if data.get("consent") == "Consented" and "Other" in concerns and not _long(
        data.get("main_concerns_other"), _("The other concern")
    ):
        frappe.throw(_("Describe the other concern."))

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
    result = {field: doc.get(field) for field in APPOINTMENT_DETAIL}
    result["referral_history"] = _referral_rows(doc.name)
    return result


@frappe.whitelist()
def session_record_detail(name=None):
    require_roles(COUNSELLOR, ADMIN_ROLE)
    doc = _appointment(name)
    client = _client_for_user(doc.client_id)
    appointment = {field: doc.get(field) for field in APPOINTMENT_DETAIL}
    appointment["referral_history"] = _referral_rows(doc.name)
    appointment["overdue"] = _flag([appointment])[0]["overdue"]
    history = frappe.get_list(
        "Appointment", filters={"client_id": client.name}, fields=list(APPOINTMENT_DETAIL),
        order_by="date_time asc", limit=0,
    )
    for row in history:
        row["referral_history"] = _referral_rows(row.name)
    return {
        "appointment": appointment,
        "case_status": client.case_status,
        "can_manage": doc.counsellor_id == frappe.session.user or is_admin(),
        "history": _flag(history),
    }


@frappe.whitelist(methods=["POST"])
def record_session(name=None, data=None):
    """Save the clinical session record and complete its scheduled appointment atomically."""
    require_roles(COUNSELLOR, ADMIN_ROLE)
    doc = _appointment(name)
    if doc.counsellor_id != frappe.session.user and not is_admin():
        frappe.throw(_("Only the counsellor assigned to this appointment can record the session."), frappe.PermissionError)
    if doc.status != "Scheduled":
        frappe.throw(_("Only a scheduled appointment can be recorded."))
    client = _client_for_user(doc.client_id)
    if client.case_status == "Closed":
        frappe.throw(_("Closed cases are read-only."))
    data = _data(data)
    allowed = SESSION_RECORD_TEXT
    _only(data, allowed + ("urgency_level",))
    for key in SESSION_RECORD_REQUIRED:
        if not _long(data.get(key), _(key.replace("_", " ")), 4000):
            frappe.throw(_("Complete the {0} field before saving the session.").format(key.replace("_", " ")))
    urgency = data.get("urgency_level")
    if urgency not in SESSION_URGENCY_LEVELS:
        frappe.throw(_("Choose an urgency level."))
    if doc.session_type == "Follow-Up":
        for key in ("progress_previous_goals", "counsellor_observations", "next_session_focus"):
            if not _long(data.get(key), _(key.replace("_", " ")), 4000):
                frappe.throw(_("Complete the {0} field for a follow-up session.").format(key.replace("_", " ")))
    for key in SESSION_RECORD_TEXT:
        doc.set(key, _long(data.get(key), _(key.replace("_", " ")), 4000))
    doc.urgency_level = urgency
    doc.status = "Completed"
    doc.save()
    return {"name": doc.name, "status": doc.status}


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
        doc.counsellor_id = frappe.session.user if is_counsellor() else owner.assigned_counsellor

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


@frappe.whitelist()
def referral_counsellors():
    require_roles(COUNSELLOR)
    users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "full_name"], order_by="full_name asc")
    return [
        {"name": row.name, "full_name": row.full_name or row.name}
        for row in users
        if row.name != frappe.session.user and COUNSELLOR in frappe.get_roles(row.name)
    ]


@frappe.whitelist(methods=["POST"])
def refer_appointment(name=None, to_counsellor=None, reason=None):
    require_roles(COUNSELLOR)
    doc = _appointment(name)
    if doc.status != "Scheduled":
        frappe.throw(_("Only a scheduled appointment can be referred."))
    if doc.counsellor_id != frappe.session.user:
        frappe.throw(_("Only the counsellor currently responsible for this appointment can refer it."), frappe.PermissionError)
    if not to_counsellor or to_counsellor == frappe.session.user:
        frappe.throw(_("Choose a different counsellor to receive this appointment."))
    if not frappe.db.get_value("User", to_counsellor, "enabled") or COUNSELLOR not in frappe.get_roles(to_counsellor):
        frappe.throw(_("Choose an active MHPSS counsellor."))
    client = _client_for_user(doc.client_id)
    if client.case_status == "Closed":
        frappe.throw(_("Closed cases cannot be referred."))
    reason = _long(reason, _("The referral reason"), 2000)
    if not reason:
        frappe.throw(_("Enter a reason for this referral."))

    doc.append("referral_history", {
        "from_counsellor": frappe.session.user,
        "to_counsellor": to_counsellor,
        "reason": reason,
        "referred_on": now_datetime(),
    })
    doc.counsellor_id = to_counsellor
    frappe.flags.allow_appointment_referral = True
    try:
        doc.flags.ignore_permissions = True
        doc.save()
    finally:
        frappe.flags.allow_appointment_referral = False
    return {"name": doc.name, "counsellor_id": doc.counsellor_id}


@frappe.whitelist()
def referral_notifications():
    require_roles(COUNSELLOR)
    user = frappe.session.user
    rows = frappe.get_all(
        "Appointment Referral",
        or_filters={"from_counsellor": user, "to_counsellor": user},
        fields=["name", "parent", "from_counsellor", "to_counsellor", "reason", "referred_on", "source_seen", "target_seen"],
        order_by="referred_on desc",
        limit=20,
    )
    result = []
    for row in rows:
        appt = frappe.db.get_value("Appointment", row.parent, ["client_id", "client_name", "date_time"], as_dict=True)
        if not appt:
            continue
        client = frappe.db.get_value("Client", appt.client_id, ["scholar_code"], as_dict=True)
        result.append({
            "id": row.name,
            "appointment": row.parent,
            "client_id": appt.client_id,
            "client_name": appt.client_name,
            "scholar_code": client.scholar_code if client else "",
            "date_time": appt.date_time,
            "from_counsellor": row.from_counsellor,
            "from_name": frappe.db.get_value("User", row.from_counsellor, "full_name") or row.from_counsellor,
            "to_counsellor": row.to_counsellor,
            "to_name": frappe.db.get_value("User", row.to_counsellor, "full_name") or row.to_counsellor,
            "reason": row.reason,
            "referred_on": row.referred_on,
            "direction": "sent" if source else "received",
        })
    unread = frappe.db.count("Appointment Referral", {"from_counsellor": user, "source_seen": 0})
    unread += frappe.db.count("Appointment Referral", {"to_counsellor": user, "target_seen": 0})
    return {"notifications": result, "unread_count": unread}


@frappe.whitelist(methods=["POST"])
def mark_referral_notifications_read():
    require_roles(COUNSELLOR)
    user = frappe.session.user
    for field, party_field in (("source_seen", "from_counsellor"), ("target_seen", "to_counsellor")):
        names = frappe.get_all("Appointment Referral", filters={party_field: user, field: 0}, pluck="name", limit=0)
        for name in names:
            frappe.db.set_value("Appointment Referral", name, field, 1, update_modified=False)
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
def set_appointment_status(name=None, status=None):
    require_roles(COUNSELLOR, ADMIN_ROLE)
    if status == "Completed":
        frappe.throw(_("Use In-session to complete the session record."))
    if status != "Cancelled":
        frappe.throw(_("An appointment can only be cancelled here."))
    doc = _appointment(name)
    if doc.status != "Scheduled":
        frappe.throw(_("Only a scheduled appointment can be cancelled."))
    doc.status = status
    doc.save()
    return {"status": doc.status}
