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
        if not self.client_id or not frappe.db.exists("Client", self.client_id) or (
            not is_admin() and owner != frappe.session.user
        ):
            frappe.throw(_("Client not found."), frappe.DoesNotExistError)
        before = self.get_doc_before_save()
        if before and before.client_id != self.client_id:
            frappe.throw(_("The client of a survey cannot be changed."))
        if frappe.db.exists("Baseline Survey", {"client_id": self.client_id, "name": ["!=", self.name or ""]}):
            frappe.throw(_("A baseline survey already exists for this client."))

    def check_lock(self):
        before = self.get_doc_before_save()
        if before and before.status in ("Completed", "Declined") and not is_admin():
            frappe.throw(_("This survey is locked. Only the System Administrator can change a submitted survey."))

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
        if rating and not 1 <= rating <= 10:
            frappe.throw(_("The wellbeing self-rating must be between 1 and 10."))
        if cint(self.dependants) < 0:
            frappe.throw(_("Dependants cannot be negative."))

    def check_completion(self):
        if self.consent != "Consented" or self.status != "Completed":
            return
        missing = [label for name, label in REQUIRED.items() if not self.get(name)]
        if missing:
            frappe.throw(_("Complete these answers before marking the survey as Completed: {0}").format(", ".join(missing)))
