import frappe
from frappe import _
from frappe.model.document import Document


class AppointmentManagementEvent(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_("Session management history cannot be changed."), frappe.PermissionError)

	def on_trash(self):
		frappe.throw(_("Session management history cannot be deleted."), frappe.PermissionError)
