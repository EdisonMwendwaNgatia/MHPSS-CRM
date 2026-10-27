import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.utils import add_days, getdate, now_datetime, nowdate

from krcti_mhpss.utils import ADMIN_ROLE, COUNSELLOR, KRCTI_PM, MODES, WOC_PM, require_roles, roles_of


def _range(date_from, date_to):
    end = getdate(date_to or nowdate())
    start = getdate(date_from or add_days(end, -30))
    if start > end or (end - start).days > 400:
        frappe.throw(_("Choose a date range of up to 400 days."))
    return start, end


def _group(table, column, *conditions):
    field = getattr(table, column)

    query = (
        frappe.qb.from_(table)
        .select(field, Count("*").as_("n"))
        .groupby(field)
    )

    for condition in conditions:
        query = query.where(condition)

    return {
        row[column]: row["n"]
        for row in query.run(as_dict=True)
    }

def _names(users):
    rows = frappe.get_all("User", filters={"name": ["in", sorted(users)]}, fields=["name", "full_name"]) if users else []
    return {row.name: row.full_name for row in rows}


@frappe.whitelist()
def programme_summary(date_from=None, date_to=None):
    """Aggregate numbers for programme managers. No client or session detail, ever."""
    require_roles(KRCTI_PM, WOC_PM, ADMIN_ROLE)
    start, end = _range(date_from, date_to)
    first, last = f"{start} 00:00:00", f"{end} 23:59:59"
    full_view = bool({KRCTI_PM, ADMIN_ROLE} & roles_of())

    Client, Appointment, Survey = (frappe.qb.DocType(n) for n in ("Client", "Appointment", "Baseline Survey"))
    in_range = (Appointment.date_time >= first, Appointment.date_time <= last)
    now = now_datetime()

    caseload = _group(Client, "case_status")
    sessions = _group(Appointment, "mode_of_contact", Appointment.status == "Completed", *in_range)

    result = {
        "scope": "KRCTI" if KRCTI_PM in roles_of() else ("WoC" if WOC_PM in roles_of() else "Admin"),
        "range": {"from": str(start), "to": str(end)},
        "caseload": {s: caseload.get(s, 0) for s in ("Active", "Follow-Up Pending", "Closed")},
        "clients_by_stream": _group(Client, "programme_stream"),
        "sessions_by_mode": {mode: sessions.get(mode, 0) for mode in MODES},
        "appointments_by_status": _group(Appointment, "status", *in_range),
        "baseline": _group(Survey, "status"),
        "referrals": None,  # recorded in the session form, which is the next release
        "by_counsellor": None,
    }

    if full_view:
        counsellors = frappe.get_all(
            "Has Role", filters={"role": COUNSELLOR, "parenttype": "User"}, pluck="parent", parent_doctype="User"
        )
        names = _names(set(counsellors))
        open_cases = _group(Client, "assigned_counsellor", Client.case_status != "Closed")
        done = _group(Appointment, "counsellor_id", Appointment.status == "Completed", *in_range)
        upcoming = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time >= now)
        overdue = _group(Appointment, "counsellor_id", Appointment.status == "Scheduled", Appointment.date_time < now)
        result["by_counsellor"] = sorted(
            (
                {
                    "counsellor": names[user],
                    "active_caseload": open_cases.get(user, 0),
                    "completed_in_range": done.get(user, 0),
                    "upcoming": upcoming.get(user, 0),
                    "overdue": overdue.get(user, 0),
                }
                for user in names
            ),
            key=lambda row: row["counsellor"],
        )
    return result


@frappe.whitelist()
def programme_calendar(date_from=None, date_to=None):
    """The KRCTI programme manager's calendar of counsellor activity. It carries no client details."""
    require_roles(KRCTI_PM, ADMIN_ROLE)
    start, end = _range(date_from, date_to)
    Appointment = frappe.qb.DocType("Appointment")
    rows = (
        frappe.qb.from_(Appointment)
        .select(
            Appointment.counsellor_id, Appointment.date_time, Appointment.end_time,
            Appointment.session_type, Appointment.mode_of_contact, Appointment.status,
        )
        .where(Appointment.date_time >= f"{start} 00:00:00")
        .where(Appointment.date_time <= f"{end} 23:59:59")
        .orderby(Appointment.date_time)
        .limit(500)
        .run(as_dict=True)
    )
    names = _names({row.counsellor_id for row in rows})
    now = now_datetime()
    return [
        {
            "counsellor": names.get(row.counsellor_id, ""),
            "start": row.date_time,
            "end": row.end_time,
            "session_type": row.session_type,
            "mode": row.mode_of_contact,
            "status": row.status,
            "overdue": row.status == "Scheduled" and row.date_time < now,
        }
        for row in rows
    ]