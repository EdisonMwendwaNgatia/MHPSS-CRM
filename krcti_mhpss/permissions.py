import re

import frappe
from frappe import _

from krcti_mhpss.utils import SINGLE_ROLES, is_admin, is_counsellor


# ---- who may see which rows (applies to every list, search and report) ----

def client_conditions(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    if is_counsellor(user):
        return f"`tabClient`.`assigned_counsellor` = {frappe.db.escape(user)}"
    return "1=0"


def baseline_conditions(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    if is_counsellor(user):
        return (
            "`tabBaseline Survey`.`client_id` in (select `name` from `tabClient` "
            f"where `assigned_counsellor` = {frappe.db.escape(user)})"
        )
    return "1=0"


def appointment_conditions(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    if is_counsellor(user):
        return f"`tabAppointment`.`counsellor_id` = {frappe.db.escape(user)}"
    return "1=0"


# ---- who may open a single record. These only ever deny, never grant. ----
def _only_own(doc, ptype, user, owner):
    user = user or frappe.session.user

    if is_admin(user):
        return True

    if ptype == "create":
        return is_counsellor(user)

    if is_counsellor(user) and owner and owner == user:
        return True

    return False




def client_has_permission(doc, ptype=None, user=None, **kwargs):
    user = user or frappe.session.user

    assigned = doc.get("assigned_counsellor")
    counsellor = is_counsellor(user)
    result = _only_own(doc, ptype, user, assigned)

    frappe.logger("krcti_mhpss").warning(
        "CLIENT_PERMISSION_TRACE: "
        f"ptype={ptype!r}, "
        f"user={user!r}, "
        f"assigned={assigned!r}, "
        f"owner={doc.get('owner')!r}, "
        f"counsellor={counsellor!r}, "
        f"result={result!r}, "
        f"name={doc.name!r}"
    )

    return result



def baseline_has_permission(doc, ptype=None, user=None, **kwargs):
    owner = frappe.db.get_value("Client", doc.get("client_id"), "assigned_counsellor") if doc.get("client_id") else None
    return _only_own(doc, ptype, user, owner)


def appointment_has_permission(doc, ptype=None, user=None, **kwargs):
    return _only_own(doc, ptype, user, doc.get("counsellor_id"))


# ---- user accounts: one role each, strong passwords, role changes on record ----

def validate_user_roles(doc, method=None):
    if doc.name == "Administrator":
        return
    # Frappe's setup wizard intentionally gives its setup user System Manager
    # and every role on the site. Preserve that built-in full-access behavior.
    if any(row.role == "System Manager" for row in doc.roles):
        return
    held = sorted({row.role for row in doc.roles} & set(SINGLE_ROLES))
    if len(held) > 1:
        frappe.throw(_("Each user holds exactly one role. This user has: {0}.").format(", ".join(held)))


def validate_user_password(doc, method=None):
    password = doc.get("new_password")
    if not password:
        return
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password) or not re.search(r"[^A-Za-z0-9]", password):
        frappe.throw(_("The password needs at least 8 characters, with an uppercase letter, a number and a special character."))


def log_role_changes(doc, method=None):
    before = doc.get_doc_before_save()
    old = {row.role for row in before.roles} & set(SINGLE_ROLES) if before else set()
    new = {row.role for row in doc.roles} & set(SINGLE_ROLES)
    if old == new:
        return
    text = _("Role changed by {0}: {1} -> {2}").format(
        frappe.session.user, ", ".join(sorted(old)) or "none", ", ".join(sorted(new)) or "none"
    )
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "User",
            "reference_name": doc.name,
            "content": text,
        }
    ).insert(ignore_permissions=True)
