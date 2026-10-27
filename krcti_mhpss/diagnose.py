import frappe
from frappe.permissions import (
    add_permission,
    get_role_permissions,
    has_permission,
    update_permission_property,
)

from krcti_mhpss.install import ensure_roles
from krcti_mhpss.utils import COUNSELLOR

DOCTYPES = ("Client", "Baseline Survey", "Appointment")
WANT = ("read", "write", "create")


def effective(doctype):
    """Return the effective DocType permissions currently defined in metadata."""
    rows = []
    for p in frappe.get_meta(doctype).permissions:
        rows.append({
            "role": p.role,
            **{
                k: int(p.get(k) or 0)
                for k in ("read", "write", "create", "delete")
            },
        })
    return rows


def report():
    """Report DocType permissions and test the counsellor's create permissions."""
    ensure_roles()

    out = {
        "custom_docperms": {
            d: frappe.db.count("Custom DocPerm", {"parent": d})
            for d in DOCTYPES
        },
        "effective": {
            d: effective(d)
            for d in DOCTYPES
        },
        "hooks": {
            d: frappe.get_hooks("has_permission").get(d)
            for d in DOCTYPES
        },
    }

    user = "diag@test.krcti.local"

    # WARNING: This removes an existing user with the same email.
    if frappe.db.exists("User", user):
        frappe.delete_doc(
            "User",
            user,
            force=True,
            ignore_permissions=True,
        )

    frappe.get_doc({
        "doctype": "User",
        "email": user,
        "first_name": "Diag",
        "send_welcome_email": 0,
        "roles": [{"role": COUNSELLOR}],
    }).insert(ignore_permissions=True)

    try:
        user_type = frappe.db.get_value("User", user, "user_type")
        frappe.set_user(user)

        meta = frappe.get_meta("Client")

        out["counsellor"] = {
            "roles": frappe.get_roles(user),
            "user_type": user_type,
            "role_permission_create": get_role_permissions(
                meta, user
            ).get("create"),
            "doctype_create": bool(
                has_permission("Client", "create", user=user)
            ),
            "document_create": bool(
                frappe.get_doc({
                    "doctype": "Client"
                }).has_permission("create", user=user)
            ),
        }

    finally:
        frappe.set_user("Administrator")
        # Roll back the temporary diagnostic user's database changes.
        frappe.db.rollback()

    return out


def repair():
    """Reload DocTypes, reset permission overrides, repair counsellor permissions,
    and return the resulting permission configuration.
    """
    ensure_roles()

    for doctype in DOCTYPES:
        frappe.reload_doc(
            "krcti_mhpss",
            "doctype",
            frappe.scrub(doctype),
            force=True,
            reset_permissions=True,
        )

    frappe.clear_cache()

    added = []

    for doctype in DOCTYPES:
        mine = next(
            (
                p for p in effective(doctype)
                if p["role"] == COUNSELLOR
            ),
            None,
        )

        for ptype in WANT:
            if not mine or not mine[ptype]:
                add_permission(doctype, COUNSELLOR, 0)
                update_permission_property(
                    doctype,
                    COUNSELLOR,
                    0,
                    ptype,
                    1,
                )
                added.append(f"{doctype}:{ptype}")

    frappe.clear_cache()
    frappe.db.commit()

    return {
        "added": added,
        "effective": {
            d: effective(d)
            for d in DOCTYPES
        },
    }
