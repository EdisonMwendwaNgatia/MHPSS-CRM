import frappe
from frappe import _
from frappe.utils import cint

from krcti_mhpss.api.oversight import _names
from krcti_mhpss.permissions import write_audit_log
from krcti_mhpss.utils import (
    ADMIN_ROLE,
    ADMIN_ROLES,
    CLIENT_ROLE,
    COUNSELLOR,
    KRCTI_PM,
    WOC_PM,
    require_roles,
)


DPO_ROLE = "KRCS Data Protection Officer"
MANAGED_ROLES = (*ADMIN_ROLES, COUNSELLOR, KRCTI_PM, WOC_PM, CLIENT_ROLE, DPO_ROLE)
AUDIT_ROLES = (*ADMIN_ROLES, DPO_ROLE)


def _recent_audit(filters=None, limit=10):
    filters = filters or {}
    return frappe.get_all(
        "KRCTI Audit Log",
        filters=filters,
        fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"],
        order_by="creation desc",
        limit=limit,
    )


def _user_roles(user_names):
    if not user_names:
        return {}
    rows = frappe.get_all(
        "Has Role", filters={"parent": ["in", list(user_names)], "parenttype": "User"},
        fields=["parent", "role"],
    )
    result = {user: [] for user in user_names}
    for row in rows:
        if row.role in MANAGED_ROLES:
            result.setdefault(row.parent, []).append(row.role)
    return result


@frappe.whitelist()
def admin_overview():
    """Administrative totals and recent immutable activity; never includes clinical fields."""
    require_roles(ADMIN_ROLE)
    users = frappe.get_all(
        "User", filters={"name": ["!=", "Guest"]}, fields=["name", "enabled", "user_type"], limit=0
    )
    roles = _user_roles({row.name for row in users})
    counts = {role: 0 for role in MANAGED_ROLES}
    for row in users:
        for role in roles.get(row.name, []):
            counts[role] = counts.get(role, 0) + 1
    recent = _recent_audit(limit=10)
    actor_names = _names({row.actor for row in recent if row.actor})
    for row in recent:
        row["actor_name"] = actor_names.get(row.actor, row.actor)
    return {
        "total_users": len(users),
        "active_users": sum(bool(row.enabled) for row in users),
        "inactive_users": sum(not bool(row.enabled) for row in users),
        "system_administrators": sum(counts.get(role, 0) for role in ADMIN_ROLES),
        "krcti_managers": counts.get(KRCTI_PM, 0),
        "woc_managers": counts.get(WOC_PM, 0),
        "counsellors": counts.get(COUNSELLOR, 0),
        "recent_activities": recent,
    }


@frappe.whitelist()
def admin_users(search=None, start=0, page_length=50):
    """Search system and website accounts without returning credentials or private settings."""
    require_roles(ADMIN_ROLE)
    start = max(0, cint(start))
    page_length = max(1, min(cint(page_length) or 50, 100))
    filters = [["User", "name", "!=", "Guest"]]
    or_filters = None
    search = " ".join(str(search or "").split())[:80]
    if search:
        like = f"%{search}%"
        or_filters = [["User", "name", "like", like], ["User", "full_name", "like", like]]
    total = frappe.db.count("User", filters=filters)
    rows = frappe.get_all(
        "User", filters=filters, or_filters=or_filters,
        fields=["name", "full_name", "first_name", "last_name", "enabled", "user_type", "last_login", "creation"],
        order_by="full_name asc, name asc", start=start, page_length=page_length,
    )
    role_map = _user_roles({row.name for row in rows})
    for row in rows:
        row["roles"] = role_map.get(row.name, [])
    if search:
        total = len(frappe.get_all("User", filters=filters, or_filters=or_filters, pluck="name", limit=0))
    return {"users": rows, "total": total, "start": start, "page_length": page_length, "roles": list(MANAGED_ROLES)}


@frappe.whitelist(methods=["POST"])
def admin_save_user(name=None, email=None, first_name=None, last_name=None, user_type="System User", role=None, enabled=1, password=None):
    """Create/update a website or system account and set exactly one managed role."""
    require_roles(ADMIN_ROLE)
    if role not in MANAGED_ROLES:
        frappe.throw(_("Choose a valid system role."))
    if user_type not in ("System User", "Website User"):
        frappe.throw(_("Choose System User or Website User."))
    if name == "Administrator":
        frappe.throw(_("The built-in Administrator account cannot be managed here."))
    if name and name == frappe.session.user and (not cint(enabled) or role not in ADMIN_ROLES):
        frappe.throw(_("You cannot deactivate or remove your own System Manager role."))

    if name:
        user = frappe.get_doc("User", name)
    else:
        email = (email or "").strip().lower()
        if not email or "@" not in email:
            frappe.throw(_("Enter a valid email address for the account."))
        if frappe.db.exists("User", email):
            frappe.throw(_("A user with this email address already exists."))
        user = frappe.new_doc("User")
        user.email = email
        user.send_welcome_email = 0

    user.first_name = " ".join(str(first_name or "").split())
    user.last_name = " ".join(str(last_name or "").split())
    if not user.first_name:
        frappe.throw(_("Enter a first name."))
    user.user_type = user_type
    user.enabled = 1 if cint(enabled) else 0
    user.set("roles", [])
    user.append("roles", {"role": role})
    if password:
        user.new_password = password

    if name:
        user.save(ignore_permissions=True)
    else:
        if not password:
            frappe.throw(_("Set a password when creating an account."))
        user.insert(ignore_permissions=True)
    return {"name": user.name, "full_name": user.full_name, "enabled": user.enabled, "role": role}


@frappe.whitelist()
def admin_audit_logs(start=0, page_length=100, search=None):
    """Audit data is visible only to System Managers and the KRCS Data Protection Officer."""
    require_roles(*AUDIT_ROLES)
    start = max(0, cint(start))
    page_length = max(1, min(cint(page_length) or 100, 200))
    filters = {}
    search = " ".join(str(search or "").split())[:80]
    if search:
        like = f"%{search}%"
        rows = frappe.get_all(
            "KRCTI Audit Log", filters=filters,
            or_filters=[["actor", "like", like], ["action", "like", like], ["affected_record", "like", like], ["details", "like", like]],
            fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"],
            order_by="creation desc", start=start, page_length=page_length,
        )
        total = len(frappe.get_all("KRCTI Audit Log", or_filters=[["actor", "like", like], ["action", "like", like], ["affected_record", "like", like], ["details", "like", like]], pluck="name", limit=0))
    else:
        rows = _recent_audit(limit=page_length + start)[start:]
        total = frappe.db.count("KRCTI Audit Log")
    actor_names = _names({row.actor for row in rows if row.actor})
    for row in rows:
        row["actor_name"] = actor_names.get(row.actor, row.actor)
    return {"logs": rows, "total": total, "start": start, "page_length": page_length}


@frappe.whitelist()
def admin_user_activity(user=None, start=0, page_length=100):
    """Audit history for activity performed by or directly affecting one user account."""
    require_roles(*AUDIT_ROLES)
    if not user or not frappe.db.exists("User", user):
        frappe.throw(_("Choose a valid user account."))
    start = max(0, cint(start))
    page_length = max(1, min(cint(page_length) or 100, 200))
    rows = frappe.get_all(
        "KRCTI Audit Log",
        or_filters=[["actor", "=", user], ["affected_record", "=", user]],
        fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"],
        order_by="creation desc", start=start, page_length=page_length,
    )
    total = len(frappe.get_all("KRCTI Audit Log", or_filters=[["actor", "=", user], ["affected_record", "=", user]], pluck="name", limit=0))
    actor_names = _names({row.actor for row in rows if row.actor})
    for row in rows:
        row["actor_name"] = actor_names.get(row.actor, row.actor)
    return {"logs": rows, "total": total, "start": start, "page_length": page_length}
