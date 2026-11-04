import frappe
from frappe import _
from frappe.model.document import Document


class KRCTIAuditLog(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_("Audit records are immutable."), frappe.PermissionError)

	def on_trash(self):
		frappe.throw(_("Audit records cannot be deleted."), frappe.PermissionError)
