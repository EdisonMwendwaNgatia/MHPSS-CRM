import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Cohort(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(
                    _("End Date cannot be earlier than Start Date.")
                )
