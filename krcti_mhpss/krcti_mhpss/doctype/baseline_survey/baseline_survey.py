import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, now_datetime

from krcti_mhpss.utils import is_admin

REQUIRED = {
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


class BaselineSurvey(Document):
    def validate(self):
        self.protect_stamps()
        self.check_client()
        self.check_lock()
        self.apply_consent()
        self.check_values()
        self.check_completion()

    def protect_stamps(self):
        """Who recorded the survey, and when, is set by the server and never by the request."""
        before = self.get_doc_before_save()
        if before:
            self.completed_by, self.completed_on = before.completed_by, before.completed_on
        else:
            self.completed_by = self.completed_on = None

    def check_client(self):
        owner = frappe.db.get_value("Client", self.client_id, "assigned_counsellor") if self.client_id else None
        workflow_call = bool(
            getattr(frappe.flags, "allow_baseline_workflow", False)
            or getattr(frappe.flags, "allow_baseline_review", False)
        )
        if not self.client_id or not frappe.db.exists("Client", self.client_id) or (not workflow_call and (
            not is_admin() and owner != frappe.session.user
        )):
            frappe.throw(_("Client not found."), frappe.DoesNotExistError)
        before = self.get_doc_before_save()
        if before and before.client_id != self.client_id:
            frappe.throw(_("The client of a survey cannot be changed."))

    def check_lock(self):
        before = self.get_doc_before_save()
        if not before:
            return
        if before.review_status == "Verified":
            frappe.throw(_("This verified baseline is permanently locked."), frappe.PermissionError)
        if before.status not in ("Completed", "Declined"):
            return
        if not getattr(frappe.flags, "allow_baseline_review", False):
            frappe.throw(_("This submitted survey is locked."), frappe.PermissionError)
        protected = (
            "client_id", "cycle", "status", "consent", "declined_reason", "wellbeing_self_rating", "stress_frequency",
            "main_concerns", "main_concerns_other", "support_availability", "coping_ability", "coping_behaviour",
            "coping_behaviour_other", "preferred_support_type", "interest_in_support", "willingness_for_followup",
            "marital_status", "dependants", "domestic_situation", "conflict_exposure", "exposure_details",
            "completed_by", "completed_on", "submitted_via", "email_sent_to", "token_hash", "token_expires_on",
        )
        if any(before.get(field) != self.get(field) for field in protected):
            frappe.throw(_("Submitted baseline answers cannot be changed during review."), frappe.PermissionError)

    def apply_consent(self):
        if self.consent == "Declined":
            self.status = "Declined"
        elif self.status == "Declined":
            self.status = "Pending"
        if self.status in ("Completed", "Declined") and not self.completed_on:
            self.completed_by = frappe.session.user
            self.completed_on = now_datetime()

    def check_values(self):
        if self.consent != "Consented":
            return
        rating = cint(self.wellbeing_self_rating)
        if not 1 <= rating <= 10:
            frappe.throw(_("The wellbeing self-rating must be between 1 and 10."))
        if cint(self.dependants) < 0:
            frappe.throw(_("Dependants cannot be negative."))
        options = {
            "stress_frequency": {"Daily", "Weekly", "Monthly", "Rarely"},
            "support_availability": {"Yes", "No", "Partial"},
            "coping_ability": {"Strong", "Moderate", "Weak"},
            "coping_behaviour": {"Talk to friend or family", "Keep it to myself", "Pray/spiritual practice", "Other"},
            "preferred_support_type": {"Individual counselling", "Group session", "Stress management", "Peer support", "Referral services", "Psychoeducation"},
            "marital_status": {"Single", "Married", "Separated", "Divorced", "Widowed", "Other"},
            "conflict_exposure": {"Yes", "No", "Prefer not to say"},
        }
        for field, allowed in options.items():
            if self.get(field) not in allowed:
                frappe.throw(_("Choose a valid option for {0}.").format(field.replace("_", " ")))
        for field in ("declined_reason", "main_concerns", "main_concerns_other", "coping_behaviour_other", "domestic_situation", "exposure_details"):
            if len(str(self.get(field) or "")) > 2000:
                frappe.throw(_("{0} cannot exceed 2000 characters.").format(field.replace("_", " ")))
        if self.coping_behaviour == "Other" and not (self.coping_behaviour_other or "").strip():
            frappe.throw(_("Describe the other coping mechanism."))
        concerns = [part.strip() for part in str(self.main_concerns or "").split(",") if part.strip()]
        valid_concerns = {"Academic pressure", "Financial challenges", "Family issues", "Relationships", "Loneliness", "Health Concerns", "Substance/Gambling", "Other"}
        if not concerns or any(item not in valid_concerns for item in concerns):
            frappe.throw(_("Select one or more valid presenting concerns."))
        if "Other" in concerns and not (self.main_concerns_other or "").strip():
            frappe.throw(_("Describe the other concern."))

    def check_completion(self):
        if self.consent != "Consented" or self.status != "Completed":
            return
        missing = [label for name, label in REQUIRED.items() if not self.get(name)]
        if missing:
            frappe.throw(_("Complete these answers before marking the survey as Completed: {0}").format(", ".join(missing)))
