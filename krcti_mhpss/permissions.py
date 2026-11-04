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
        escaped = frappe.db.escape(user)
        return (
            f"(`tabClient`.`assigned_counsellor` = {escaped} or `tabClient`.`name` in ("
            "select a.`client_id` from `tabAppointment` a "
            "inner join `tabAppointment Referral` r on r.`parent` = a.`name` "
            f"where r.`from_counsellor` = {escaped} or r.`to_counsellor` = {escaped}))"
        )
    return "1=0"


def baseline_conditions(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    if is_counsellor(user):
        return (
            "`tabBaseline Survey`.`client_id` in (select `name` from `tabClient` "
            f"where {client_conditions(user)})"
        )
    return "1=0"


def appointment_conditions(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    if is_counsellor(user):
        escaped = frappe.db.escape(user)
        return (
            f"(`tabAppointment`.`counsellor_id` = {escaped} or `tabAppointment`.`client_id` in ("
            "select a.`client_id` from `tabAppointment` a "
            "inner join `tabAppointment Referral` r on r.`parent` = a.`name` "
            f"where r.`from_counsellor` = {escaped} or r.`to_counsellor` = {escaped}))"
        )
    return "1=0"


def counsellor_in_case(client_name, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    if not is_counsellor(user) or not client_name:
        return False
    assigned = frappe.db.get_value("Client", client_name, "assigned_counsellor")
    if assigned == user:
        return True
    if frappe.db.exists("Appointment", {"client_id": client_name, "counsellor_id": user}):
        return True
    return bool(
        frappe.db.sql(
            """select r.name from `tabAppointment Referral` r
               inner join `tabAppointment` a on a.name = r.parent
               where a.client_id = %s and (r.from_counsellor = %s or r.to_counsellor = %s) limit 1""",
            (client_name, user, user),
        )
    )


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
    result = _only_own(doc, ptype, user, assigned) or (
        ptype in ("read", "write") and counsellor_in_case(doc.name, user)
    )

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
    if is_admin(user):
        return ptype in ("read", "report", "export", "print")
    owner = frappe.db.get_value("Client", doc.get("client_id"), "assigned_counsellor") if doc.get("client_id") else None
    return _only_own(doc, ptype, user, owner) or (
        ptype in ("read", "write") and counsellor_in_case(doc.get("client_id"), user)
    )


def appointment_has_permission(doc, ptype=None, user=None, **kwargs):
    if is_admin(user):
        return ptype in ("read", "report", "export", "print")
    return _only_own(doc, ptype, user, doc.get("counsellor_id")) or (
        ptype == "read" and counsellor_in_case(doc.get("client_id"), user)
    ) or (
        ptype == "write" and getattr(frappe.flags, "allow_appointment_referral", False)
        and counsellor_in_case(doc.get("client_id"), user)
    )


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


def write_audit_log(action, affected_record=None, module="System administration", outcome="Success", details=None, actor=None):
    """Insert minimal activity metadata into the append-only audit log."""
    if not frappe.db.exists("DocType", "KRCTI Audit Log"):
        return
    frappe.get_doc({
        "doctype": "KRCTI Audit Log",
        "actor": actor or frappe.session.user,
        "action": str(action)[:140],
        "affected_record": str(affected_record or "")[:140],
        "module": str(module or "")[:80],
        "outcome": outcome if outcome in ("Success", "Failure") else "Success",
        "details": str(details or "")[:500],
    }).insert(ignore_permissions=True)


def log_user_created(doc, method=None):
    if doc.name != "Administrator":
        write_audit_log("User account created", doc.name, "User management")


def log_user_updated(doc, method=None):
    before = doc.get_doc_before_save()
    if not before or doc.name == "Administrator":
        return
    old = {row.role for row in before.roles} & set(SINGLE_ROLES)
    new = {row.role for row in doc.roles} & set(SINGLE_ROLES)
    if old != new:
        write_audit_log("User role changed", doc.name, "Role management", details=f"{', '.join(sorted(old)) or 'none'} → {', '.join(sorted(new)) or 'none'}")
    if before.enabled != doc.enabled:
        write_audit_log("User account activated" if doc.enabled else "User account deactivated", doc.name, "User management")
    if before.first_name != doc.first_name or before.last_name != doc.last_name or before.user_type != doc.user_type:
        write_audit_log("User account updated", doc.name, "User management")


def log_role_changes(doc, method=None):
    """Compatibility alias for sites with the earlier cached User hook name."""
    return log_user_updated(doc, method)


def log_user_login(login_manager):
    if frappe.session.user and frappe.session.user != "Guest":
        write_audit_log("User logged in", frappe.session.user, "Authentication")


def log_user_logout(login_manager=None):
    if frappe.session.user and frappe.session.user != "Guest":
        write_audit_log("User logged out", frappe.session.user, "Authentication")


def log_client_registration(doc, method=None):
    write_audit_log("Client registered", doc.name, "Client management")


def log_client_update(doc, method=None):
    before = doc.get_doc_before_save()
    if before and before.as_dict() != doc.as_dict():
        write_audit_log("Client updated", doc.name, "Client management")


def log_appointment_activity(doc, method=None):
    if getattr(frappe.flags, "programme_session_action", False):
        return
    before = doc.get_doc_before_save()
    if not before:
        write_audit_log("Appointment booked", doc.name, "Appointments")
        return
    if before.status != doc.status and doc.status == "Completed":
        write_audit_log("Session completed", doc.name, "Session records")
    elif before.status != doc.status and doc.status == "Cancelled":
        write_audit_log("Appointment cancelled", doc.name, "Appointments")
    elif before.counsellor_id != doc.counsellor_id:
        write_audit_log("Appointment reassigned", doc.name, "Session management")
    elif any(before.get(field) != doc.get(field) for field in ("date_time", "duration_minutes", "session_type", "mode_of_contact", "location", "notes")):
        write_audit_log("Appointment updated", doc.name, "Appointments")
