import re

import frappe
from frappe.utils import get_datetime, now_datetime

ADMIN_ROLE = "System Manager"
KRCTI_ADMIN_ROLE = "KRCTI System Administrator"
ADMIN_ROLES = (ADMIN_ROLE, KRCTI_ADMIN_ROLE)
COUNSELLOR = "MHPSS Counsellor"
KRCTI_PM = "KRCTI Programme Manager"
WOC_PM = "WoC Programme Manager"
CLIENT_ROLE = "MHPSS Client"
DPO_ROLE = "KRCS Data Protection Officer"

# Mutually exclusive MHPSS business roles.
SINGLE_ROLES = (*ADMIN_ROLES, COUNSELLOR, KRCTI_PM, WOC_PM, CLIENT_ROLE, DPO_ROLE)

MODES = ("Physical Individual", "Physical Group", "Tele-counselling", "Phone Call", "School Campaign")
PHYSICAL_MODES = ("Physical Individual", "Physical Group", "School Campaign")
GROUP_MODES = ("Physical Group", "School Campaign")


def roles_of(user=None):
    return set(frappe.get_roles(user or frappe.session.user))


def is_admin(user=None):
    return bool(set(ADMIN_ROLES) & roles_of(user))


def is_counsellor(user=None):
    return COUNSELLOR in roles_of(user)


def require_roles(*allowed):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to continue.", frappe.AuthenticationError)
    allowed = set(allowed)
    if ADMIN_ROLE in allowed:
        allowed.update(ADMIN_ROLES)
    if not (allowed & roles_of()):
        frappe.throw("You do not have access to this.", frappe.PermissionError)


def normalize_phone(value):
    """Digits only, with Kenyan numbers in the 07XXXXXXXX form, so searches match any format."""
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("254") and len(digits) == 12:
        digits = "0" + digits[3:]
    elif len(digits) == 9 and digits[0] in "71":
        digits = "0" + digits
    return digits


def is_overdue(status, date_time):
    return status == "Scheduled" and bool(date_time) and get_datetime(date_time) < now_datetime()
