import frappe

# Counsellors keep Desk access for now as a fallback. Everyone else works in the app.
ROLES = {
    "System Manager": 1,
    "MHPSS Counsellor": 1,
    "KRCTI Programme Manager": 0,
    "WoC Programme Manager": 0,
    "MHPSS Client": 0,
}


def ensure_roles():
    """Create any missing role and fix its Desk setting. Safe to run any number of times."""
    for role, desk in ROLES.items():
        if frappe.db.exists("Role", role):
            if frappe.db.get_value("Role", role, "desk_access") != desk:
                frappe.db.set_value("Role", role, "desk_access", desk)
        else:
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": desk}).insert(
                ignore_permissions=True
            )


def after_migrate():
    ensure_roles()


def after_install():
    ensure_roles()
    path = frappe.get_app_path("krcti_mhpss", "patches.txt")
    with open(path) as handle:
        lines = [line.strip() for line in handle]
    for line in lines:
        if not line or line.startswith(("#", "[")) or ":" in line:
            continue
        frappe.get_attr(f"{line}.execute")()
    frappe.db.commit()