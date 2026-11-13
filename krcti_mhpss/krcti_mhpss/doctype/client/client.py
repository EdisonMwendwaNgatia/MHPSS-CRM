import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint

from krcti_mhpss.utils import COUNSELLOR, get_active_cohort, is_admin, is_counsellor, normalize_phone

CODE = re.compile(r"^WoCS_C([1-9])(\d{2})$")


class Client(Document):
    def before_insert(self):
        self.case_status = "Active"
        if is_counsellor() and not is_admin():
            self.assigned_counsellor = frappe.session.user
        # Cohort is a programme-wide setting. Never trust a cohort submitted by a
        # client form; changing the setting only affects records created from now on.
        self.cohort = get_active_cohort()
        self.generate_scholar_code()

    def generate_scholar_code(self):
        cohort = cint(self.cohort)
        if not 1 <= cohort <= 9:
            frappe.throw(_("Choose a cohort from 1 to 9 before registering the client."))

        existing_count = frappe.db.count("Client", {"cohort": str(cohort)})
        if existing_count >= 99:
            frappe.throw(_("Cohort {0} already has 99 clients. Activate another cohort in Programme Settings.").format(cohort))

        # Frappe's naming series counter is locked per cohort, so concurrent registrations
        # receive distinct two-digit numbers. Skip any matching codes imported previously.
        series = f"WoCS_C{cohort}.##"
        for _ in range(99):
            code = make_autoname(series)
            match = CODE.fullmatch(code)
            if not match or int(match.group(2)) > 99:
                frappe.throw(_("Cohort {0} already has 99 scholar codes.").format(cohort))
            if not frappe.db.exists("Client", {"scholar_code": code}):
                self.scholar_code = code
                return
        frappe.throw(_("Cohort {0} already has 99 scholar codes.").format(cohort))

    def validate(self):
        self.tidy()
        self.check_immutable()
        self.check_code()
        self.check_values()
        self.check_counsellor()
        self.check_case_status()

    def tidy(self):
        self.scholar_code = " ".join((self.scholar_code or "").split())
        self.full_name = " ".join((self.full_name or "").split())
        self.institution = " ".join((self.institution or "").split())
        self.phone_number = normalize_phone(self.phone_number)

    def check_immutable(self):
        before = self.get_doc_before_save()
        if before and before.cohort != self.cohort:
            if not is_admin():
                frappe.throw(_("The client cohort cannot be changed."))
            if before.scholar_code == self.scholar_code:
                frappe.throw(_("Change the scholar code when changing the cohort."))
        if before and before.scholar_code != self.scholar_code and not is_admin():
            frappe.throw(_("The Scholar/Participant Code cannot be changed. Ask the System Administrator."))

    def check_code(self):
        before = self.get_doc_before_save()
        # Keep existing historical identifiers valid when editing older client records.
        match = CODE.fullmatch(self.scholar_code or "")
        unchanged_legacy_code = before and before.scholar_code == self.scholar_code
        if not unchanged_legacy_code and (not match or int(match.group(1)) != cint(self.cohort)):
            frappe.throw(_("The Scholar/Participant Code must match the selected cohort."))
        other = frappe.db.get_value(
            "Client",
            {"scholar_code": self.scholar_code, "name": ["!=", self.name or ""]},
            ["name", "full_name", "assigned_counsellor"],
            as_dict=True,
        )
        if not other:
            return
        # The existing record is shown only to its own counsellor or the administrator.
        if is_admin() or other.assigned_counsellor == frappe.session.user:
            frappe.throw(
                _("A client with this Scholar/Participant Code already exists: {0} ({1}).").format(
                    other.name, other.full_name
                )
            )
        frappe.throw(
            _("This Scholar/Participant Code is already registered to another counsellor. Please contact the System Administrator.")
        )

    def check_values(self):
        if not 10 <= cint(self.age) <= 100:
            frappe.throw(_("Enter a valid age (10 to 100)."))
        if self.is_new() and not 1 <= cint(self.cohort) <= 9:
            frappe.throw(_("Choose a cohort from 1 to 9."))
        if self.cohort and not 1 <= cint(self.cohort) <= 9:
            frappe.throw(_("Cohort must be from 1 to 9."))
        if not 1 <= cint(self.year_of_study) <= 10:
            frappe.throw(_("Year of study must be between 1 and 10."))
        if not 9 <= len(self.phone_number or "") <= 15:
            frappe.throw(_("Enter a valid phone number."))
        if self.disability_status and not (self.disability_type or "").strip():
            frappe.throw(_("Enter the type of disability."))
        if not self.disability_status:
            self.disability_type = ""
        if self.referral_source != "Other":
            self.referral_source_other = ""

    def check_counsellor(self):
        if self.assigned_counsellor:
            enabled = frappe.db.get_value("User", self.assigned_counsellor, "enabled")
            if not enabled or COUNSELLOR not in frappe.get_roles(self.assigned_counsellor):
                frappe.throw(_("The assigned counsellor must be an active counsellor."))
        before = self.get_doc_before_save()
        if before and before.assigned_counsellor != self.assigned_counsellor and not is_admin():
            frappe.throw(_("Only the System Administrator can reassign a client."))

    def check_case_status(self):
        before = self.get_doc_before_save()
        if not before:
            return
        if before.case_status == "Closed" and not is_admin():
            frappe.throw(_("This case is closed. Closed records are read-only."))
        if self.case_status == "Closed" and before.case_status != "Closed":
            done = frappe.db.exists(
                "Appointment", {"client_id": self.name, "session_type": "Termination", "status": "Completed"}
            )
            if not done and not getattr(frappe.flags, "close_case_without_termination", False):
                frappe.throw(_("A case can be closed only after a completed Termination session."))
