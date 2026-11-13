"""Programme-managed baseline collection, review and counsellor assignment."""
import hashlib
import html
import re
import secrets

import frappe
from frappe import _
from frappe.utils import add_days, get_url, now_datetime

from krcti_mhpss.api.oversight import _programme_client
from krcti_mhpss.permissions import write_audit_log
from krcti_mhpss.utils import COUNSELLOR, KRCTI_PM, WOC_PM, require_roles


SHORT_FIELDS = (
    "stress_frequency", "support_availability", "coping_ability", "coping_behaviour",
    "preferred_support_type", "marital_status", "conflict_exposure",
)
LONG_FIELDS = (
    "declined_reason", "main_concerns", "main_concerns_other", "coping_behaviour_other",
    "domestic_situation", "exposure_details",
)
NUMBER_FIELDS = ("wellbeing_self_rating", "dependants")
CHECK_FIELDS = ("interest_in_support", "willingness_for_followup")
ALLOWED_FIELDS = {"consent", *SHORT_FIELDS, *LONG_FIELDS, *NUMBER_FIELDS, *CHECK_FIELDS}
REQUIRED_FIELDS = {
    "wellbeing_self_rating": "Wellbeing self-rating",
    "stress_frequency": "Recent stress frequency",
    "main_concerns": "Main concerns",
    "support_availability": "Support availability",
    "coping_ability": "Coping ability",
    "preferred_support_type": "Preferred support type",
    "coping_behaviour": "Coping behaviour",
    "marital_status": "Marital status",
    "domestic_situation": "Domestic situation",
    "conflict_exposure": "Conflict or disaster exposure",
}
SELECTS = {
    "stress_frequency": {"Daily", "Weekly", "Monthly", "Rarely"},
    "support_availability": {"Yes", "No", "Partial"},
    "coping_ability": {"Strong", "Moderate", "Weak"},
    "coping_behaviour": {"Talk to friend or family", "Keep it to myself", "Pray/spiritual practice", "Other"},
    "preferred_support_type": {"Individual counselling", "Group session", "Stress management", "Peer support", "Referral services", "Psychoeducation"},
    "marital_status": {"Single", "Married", "Separated", "Divorced", "Widowed", "Other"},
    "conflict_exposure": {"Yes", "No", "Prefer not to say"},
}


def _audit(action, client, survey=None, details="", outcome="Success"):
    request_ip = getattr(frappe.local, "request_ip", None)
    source = f"{details}; source_ip={request_ip}" if request_ip else details
    if survey:
        source = f"survey={survey}; {source}"
    write_audit_log(action, client, "Baseline workflow", outcome=outcome, details=source)


def _get_client(name):
    client = _programme_client(name)
    return frappe.get_doc("Client", name)


def _surveys(client):
    return frappe.get_all(
        "Baseline Survey", filters={"client_id": client},
        fields=["name", "cycle", "status", "consent", "review_status", "submitted_via", "email_sent_to", "completed_by", "completed_on", "verified_by", "verified_on", "review_notes"],
        order_by="cycle desc, creation desc", limit=0,
    )


def _latest(client):
    rows = _surveys(client)
    return rows[0] if rows else None


def _new_cycle(client, source):
    latest = _latest(client.name)
    if latest and latest.review_status == "Verified":
        frappe.throw(_("This baseline has been verified and the workflow is complete."))
    if latest and latest.review_status == "Awaiting Review":
        frappe.throw(_("Review or reject the submitted baseline before creating another form cycle."))
    cycle = (int(latest.cycle or 0) + 1) if latest else 1
    survey = frappe.get_doc({
        "doctype": "Baseline Survey", "client_id": client.name,
        "cycle": cycle, "status": "Pending", "review_status": "Pending Client",
        "submitted_via": source,
    })
    frappe.flags.allow_baseline_workflow = True
    try:
        survey.insert(ignore_permissions=True)
    finally:
        frappe.flags.allow_baseline_workflow = False
    _audit("Baseline cycle created", client.name, survey.name, f"cycle={cycle}; path={source}")
    return survey


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _survey_for_token(token):
    token = str(token or "").strip()
    if len(token) < 32 or len(token) > 200:
        frappe.throw(_("This baseline link is invalid or expired."), frappe.PermissionError)
    digest = _token_hash(token)
    name = frappe.db.get_value("Baseline Survey", {"token_hash": digest}, "name")
    if not name:
        frappe.throw(_("This baseline link is invalid or expired."), frappe.PermissionError)
    survey = frappe.get_doc("Baseline Survey", name)
    if survey.status != "Pending" or survey.review_status != "Pending Client" or not survey.token_expires_on or survey.token_expires_on < now_datetime():
        frappe.throw(_("This form has already been submitted or the link has expired."), frappe.PermissionError)
    return survey


def _client_summary(client):
    return {key: client.get(key) for key in ("name", "full_name", "scholar_code", "institution", "course_programme", "year_of_study", "programme_stream")}


def _validate_answers(data):
    if isinstance(data, str):
        data = frappe.parse_json(data)
    if not isinstance(data, dict) or set(data) - ALLOWED_FIELDS:
        frappe.throw(_("The baseline form contains unsupported fields."))
    consent = data.get("consent")
    if consent not in ("Consented", "Declined"):
        frappe.throw(_("Record whether the client consented."))
    cleaned = {"consent": consent}
    if consent == "Declined":
        reason = str(data.get("declined_reason") or "").strip()
        if len(reason) > 2000:
            frappe.throw(_("The decline reason cannot exceed 2000 characters."))
        cleaned["declined_reason"] = reason
        return cleaned
    missing = [label for key, label in REQUIRED_FIELDS.items() if data.get(key) in (None, "")]
    if missing:
        frappe.throw(_("Complete all required baseline answers: {0}.").format(", ".join(missing)))
    for key, options in SELECTS.items():
        value = str(data.get(key) or "").strip()
        if value not in options:
            frappe.throw(_("Choose a valid option for {0}.").format(key.replace("_", " ")))
        cleaned[key] = value
    rating = data.get("wellbeing_self_rating")
    dependants = data.get("dependants") or 0
    try:
        rating, dependants = int(rating), int(dependants or 0)
    except (TypeError, ValueError):
        frappe.throw(_("Wellbeing rating and dependants must be whole numbers."))
    if not 1 <= rating <= 10:
        frappe.throw(_("Wellbeing self-rating must be between 1 and 10."))
    if dependants < 0:
        frappe.throw(_("Dependants cannot be negative."))
    cleaned["wellbeing_self_rating"], cleaned["dependants"] = rating, dependants
    for key in LONG_FIELDS:
        value = str(data.get(key) or "").strip()
        if len(value) > 2000:
            frappe.throw(_("{0} cannot exceed 2000 characters.").format(key.replace("_", " ")))
        cleaned[key] = value
    if cleaned["coping_behaviour"] == "Other" and not cleaned["coping_behaviour_other"]:
        frappe.throw(_("Describe the other coping mechanism."))
    concerns = [part.strip() for part in cleaned["main_concerns"].split(",") if part.strip()]
    allowed_concerns = {"Academic pressure", "Financial challenges", "Family issues", "Relationships", "Loneliness", "Health Concerns", "Substance/Gambling", "Other"}
    if not concerns or any(item not in allowed_concerns for item in concerns):
        frappe.throw(_("Select one or more valid presenting concerns."))
    if "Other" in concerns and not cleaned["main_concerns_other"]:
        frappe.throw(_("Describe the other concern."))
    for key in CHECK_FIELDS:
        value = data.get(key, False)
        if value not in (True, False, 0, 1, "0", "1"):
            frappe.throw(_("Choose a valid answer for {0}.").format(key.replace("_", " ")))
        cleaned[key] = 1 if value in (True, 1, "1") else 0
    return cleaned


def _save_submission(survey, data, submitted_via):
    if survey.status != "Pending" or survey.review_status != "Pending Client":
        frappe.throw(_("This form has already been submitted and can no longer be edited."))
    answers = _validate_answers(data)
    for key, value in answers.items():
        survey.set(key, value)
    survey.status = "Declined" if answers["consent"] == "Declined" else "Completed"
    survey.review_status = "Awaiting Review"
    survey.submitted_via = submitted_via
    survey.token_hash = ""
    survey.token_expires_on = None
    frappe.flags.allow_baseline_workflow = True
    try:
        survey.save(ignore_permissions=True)
    finally:
        frappe.flags.allow_baseline_workflow = False
    _audit("Baseline submitted", survey.client_id, survey.name, f"cycle={survey.cycle}; via={submitted_via}")
    return {"name": survey.name, "review_status": survey.review_status}


@frappe.whitelist(methods=["POST"])
def programme_baseline_start(client=None, path="staff"):
    require_roles(KRCTI_PM, WOC_PM)
    owner = _get_client(client)
    latest = _latest(owner.name)
    if latest and latest.review_status == "Verified":
        frappe.throw(_("This baseline is verified and locked."))
    if latest and latest.review_status == "Awaiting Review":
        frappe.throw(_("This baseline is submitted and awaiting your review."))
    if path not in ("staff", "email"):
        frappe.throw(_("Choose email or complete on behalf of the client."))
    if path == "email" and not owner.email:
        frappe.throw(_("Add a client email before sending the baseline form."))
    if latest and latest.review_status == "Pending Client":
        survey = frappe.get_doc("Baseline Survey", latest.name)
    else:
        survey = _new_cycle(owner, "Programme Manager" if path == "staff" else "Client email")
    if path == "staff":
        survey.submitted_via = "Programme Manager"
        survey.token_hash = ""
        survey.token_expires_on = None
        frappe.flags.allow_baseline_workflow = True
        try:
            survey.save(ignore_permissions=True)
        finally:
            frappe.flags.allow_baseline_workflow = False
        _audit("Baseline fill opened for client", owner.name, survey.name, f"cycle={survey.cycle}")
        return {"survey": survey.name, "cycle": survey.cycle}

    token = secrets.token_urlsafe(40)
    survey.token_hash = _token_hash(token)
    survey.token_expires_on = add_days(now_datetime(), 30)
    survey.email_sent_to = owner.email
    survey.submitted_via = "Client email"
    frappe.flags.allow_baseline_workflow = True
    try:
        survey.save(ignore_permissions=True)
    finally:
        frappe.flags.allow_baseline_workflow = False
    configured_frontend = (frappe.conf.get("krcti_frontend_url") or "").rstrip("/")
    form_url = f"{configured_frontend}/baseline/{token}" if configured_frontend else get_url(f"/frontend/baseline/{token}")
    frappe.sendmail(
        recipients=[owner.email],
        subject=_("Please complete your MHPSS baseline survey"),
        message=_("<p>Hello {0},</p><p>Please complete your baseline survey using the secure link below. This link can be submitted once and expires in 30 days.</p><p><a href=\"{1}\">Open baseline survey</a></p>").format(html.escape(owner.full_name or ""), html.escape(form_url, quote=True)),
        reference_doctype="Baseline Survey", reference_name=survey.name,
    )
    _audit("Baseline form sent", owner.name, survey.name, f"cycle={survey.cycle}; email={owner.email}")
    return {"survey": survey.name, "cycle": survey.cycle, "email": owner.email}


@frappe.whitelist()
def programme_baseline_context(client=None, survey=None):
    require_roles(KRCTI_PM, WOC_PM)
    owner = _get_client(client)
    if survey:
        doc = frappe.get_doc("Baseline Survey", survey)
        if doc.client_id != owner.name or doc.status != "Pending" or doc.review_status != "Pending Client":
            frappe.throw(_("This baseline form is no longer available."), frappe.PermissionError)
    else:
        latest = _latest(owner.name)
        if not latest or latest.review_status != "Pending Client":
            frappe.throw(_("Start a new baseline form cycle from the client record."))
        doc = frappe.get_doc("Baseline Survey", latest.name)
    return {"client": _client_summary(owner), "survey_id": doc.name, "cycle": doc.cycle}


@frappe.whitelist(allow_guest=True)
def public_baseline_context(token=None):
    survey = _survey_for_token(token)
    owner = frappe.get_doc("Client", survey.client_id)
    return {"client": _client_summary(owner), "survey_id": survey.name, "cycle": survey.cycle}


@frappe.whitelist(methods=["POST"])
def programme_baseline_submit(survey=None, data=None):
    require_roles(KRCTI_PM, WOC_PM)
    doc = frappe.get_doc("Baseline Survey", survey)
    _get_client(doc.client_id)
    result = _save_submission(doc, data, "Programme Manager")
    result["client"] = doc.client_id
    return result


@frappe.whitelist(methods=["POST"], allow_guest=True)
def public_baseline_submit(token=None, data=None):
    survey = _survey_for_token(token)
    return _save_submission(survey, data, "Client email")


@frappe.whitelist(methods=["POST"])
def programme_baseline_review(client=None, survey=None, action=None, reason=None):
    require_roles(KRCTI_PM, WOC_PM)
    owner = _get_client(client)
    doc = frappe.get_doc("Baseline Survey", survey)
    if doc.client_id != owner.name or doc.review_status != "Awaiting Review" or doc.status not in ("Completed", "Declined"):
        frappe.throw(_("Only a submitted baseline awaiting review can be verified or rejected."))
    if action == "verify":
        doc.review_status = "Verified"
        doc.verified_by = frappe.session.user
        doc.verified_on = now_datetime()
        doc.review_notes = ""
        audit_action = "Baseline verified and locked"
    elif action == "reject":
        reason = " ".join(str(reason or "").split())
        if len(reason) < 3 or len(reason) > 2000:
            frappe.throw(_("Provide a rejection reason of 3 to 2000 characters."))
        doc.review_status = "Rejected"
        doc.review_notes = reason
        audit_action = "Baseline rejected"
    else:
        frappe.throw(_("Choose verify or reject."))
    frappe.flags.allow_baseline_review = True
    try:
        doc.save(ignore_permissions=True)
    finally:
        frappe.flags.allow_baseline_review = False
    _audit(audit_action, owner.name, doc.name, f"cycle={doc.cycle}; reason={doc.review_notes or 'verified'}")
    return {"review_status": doc.review_status, "name": doc.name}


@frappe.whitelist(methods=["POST"])
def programme_update_client_email(client=None, email=None):
    require_roles(KRCTI_PM, WOC_PM)
    owner = _get_client(client)
    email = " ".join(str(email or "").split()).lower()
    if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        frappe.throw(_("Enter a valid email address or leave it blank."))
    previous = owner.email or ""
    owner.email = email
    owner.save(ignore_permissions=True)
    if previous != email:
        latest = _latest(owner.name)
        if latest and latest.review_status == "Pending Client":
            survey = frappe.get_doc("Baseline Survey", latest.name)
            survey.token_hash = ""
            survey.token_expires_on = None
            frappe.flags.allow_baseline_workflow = True
            try:
                survey.save(ignore_permissions=True)
            finally:
                frappe.flags.allow_baseline_workflow = False
            _audit("Baseline link invalidated after email change", owner.name, survey.name, f"cycle={survey.cycle}")
    _audit("Client email updated", owner.name, details=f"previous={previous or 'empty'}; current={email or 'empty'}")
    return {"email": email}


@frappe.whitelist(methods=["POST"])
def programme_assign_counsellor(client=None, counsellor=None):
    require_roles(KRCTI_PM, WOC_PM)
    owner = _get_client(client)
    latest = _latest(owner.name)
    if not latest or latest.review_status != "Verified":
        frappe.throw(_("Verify the client's baseline before assigning a counsellor."))
    if owner.assigned_counsellor:
        frappe.throw(_("A counsellor is already assigned to this client."))
    if not frappe.db.get_value("User", counsellor, "enabled") or COUNSELLOR not in frappe.get_roles(counsellor):
        frappe.throw(_("Choose an active counsellor."))
    owner.assigned_counsellor = counsellor
    frappe.flags.allow_programme_counsellor_assignment = True
    try:
        owner.save(ignore_permissions=True)
    finally:
        frappe.flags.allow_programme_counsellor_assignment = False
    write_audit_log("Counsellor assigned after baseline verification", owner.name, "Client management", details=f"counsellor={counsellor}; verified_baseline={latest.name}; cycle={latest.cycle}")
    return {"assigned_counsellor": counsellor}
