import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint

from krcti_mhpss.utils import COUNSELLOR, is_admin, is_counsellor, normalize_phone

CODE = re.compile(r"^(?:WoC-\d{4}|[A-Z0-9][A-Z0-9/_-]{2,39})$")


class Client(Document):
    def before_insert(self):
        self.case_status = "Active"
        if is_counsellor() and not is_admin():
            self.assigned_counsellor = frappe.session.user

    def validate(self):
        if not self.scholar_code:
            while True:
                generated = make_autoname("WoC-.####")
                if not re.fullmatch(r"WoC-\d{4}", generated):
                    frappe.throw(_("The WoC participant code range is exhausted."))
                if not frappe.db.exists("Client", {"scholar_code": generated}):
                    self.scholar_code = generated
                    break
        self.tidy()
        self.check_immutable()
        self.check_code()
        self.check_values()
        self.check_counsellor()
        self.check_case_status()

    def tidy(self):
        code = " ".join((self.scholar_code or "").split())
        self.scholar_code = f"WoC-{code[4:]}" if re.fullmatch(r"woc-\d{4}", code, re.IGNORECASE) else code.upper()
        self.full_name = " ".join((self.full_name or "").split())
        self.institution = " ".join((self.institution or "").split())
        self.phone_number = normalize_phone(self.phone_number)

    def check_immutable(self):
        before = self.get_doc_before_save()
        if before and before.scholar_code != self.scholar_code and not is_admin():
            frappe.throw(_("The Scholar/Participant Code cannot be changed. Ask the System Administrator."))

    def check_code(self):
        if not CODE.match(self.scholar_code or ""):
            frappe.throw(_("Enter a valid Scholar/Participant Code (letters, numbers, - / _ and at least 3 characters)."))
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
        if not 1 <= cint(self.year_of_study) <= 8:
            frappe.throw(_("Year of study must be between 1 and 8."))
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
