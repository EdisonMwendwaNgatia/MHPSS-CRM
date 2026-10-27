import frappe

from krcti_mhpss.utils import ADMIN_ROLE, CLIENT_ROLE, COUNSELLOR, KRCTI_PM, WOC_PM, roles_of

ROLE_KEYS = (
    (ADMIN_ROLE, "admin"), (COUNSELLOR, "counsellor"), (KRCTI_PM, "krcti_pm"),
    (WOC_PM, "woc_pm"), (CLIENT_ROLE, "client"),
)


@frappe.whitelist()
def me():
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to continue.", frappe.AuthenticationError)
    roles = roles_of()
    return {
        "user": frappe.session.user,
        "full_name": frappe.db.get_value("User", frappe.session.user, "full_name"),
        "role": next((key for name, key in ROLE_KEYS if name in roles), None),
    }