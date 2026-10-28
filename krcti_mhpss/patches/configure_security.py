import frappe


def execute():
    settings = frappe.get_single("System Settings")
    settings.language ="en"
    settings.session_expiry = "00:30"
    settings.enable_password_policy = 1
    settings.minimum_password_score = 3
    settings.time_zone = "Africa/Nairobi"
    settings.country = "Kenya"
    settings.save(ignore_permissions=True)
