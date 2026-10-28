import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, cint, get_datetime, now_datetime

from krcti_mhpss.utils import GROUP_MODES, PHYSICAL_MODES, is_admin


class Appointment(Document):
    def before_insert(self):
        self.status = "Scheduled"
        if not is_admin():
            self.counsellor_id = frappe.session.user
        elif not self.counsellor_id and self.client_id:
            self.counsellor_id = frappe.db.get_value("Client", self.client_id, "assigned_counsellor")

    def validate(self):
        self.check_people()
        self.check_values()
        self.check_slot()
        self.check_status()

    def check_people(self):
        client = (
            frappe.db.get_value("Client", self.client_id, ["assigned_counsellor", "case_status"], as_dict=True)
            if self.client_id
            else None
        )
        if not client or (not is_admin() and client.assigned_counsellor != frappe.session.user):
            frappe.throw(_("Client not found."), frappe.DoesNotExistError)
        if client.assigned_counsellor != self.counsellor_id:
            frappe.throw(_("The counsellor must be the one assigned to this client."))
        if not is_admin() and self.counsellor_id != frappe.session.user:
            frappe.throw(_("You can only manage your own appointments."), frappe.PermissionError)
        if client.case_status == "Closed" and not is_admin():
            frappe.throw(_("This case is closed and its records are read-only."))
        before = self.get_doc_before_save()
        if before and before.client_id != self.client_id:
            frappe.throw(_("The client of an appointment cannot be changed."))

    def check_values(self):
        if self.mode_of_contact in PHYSICAL_MODES and not (self.location or "").strip():
            frappe.throw(_("Enter the physical location for this kind of session."))
        minutes = cint(self.duration_minutes) or 60
        if not 15 <= minutes <= 480:
            frappe.throw(_("The duration must be between 15 and 480 minutes."))
        self.duration_minutes = minutes
        if self.date_time:
            self.end_time = add_to_date(get_datetime(self.date_time), minutes=minutes)

    def check_slot(self):
        if self.status != "Scheduled" or not self.date_time:
            return
        if self.mode_of_contact not in GROUP_MODES:
            clash = frappe.db.exists(
                "Appointment",
                {
                    "counsellor_id": self.counsellor_id,
                    "date_time": get_datetime(self.date_time),
                    "status": "Scheduled",
                    "mode_of_contact": ["not in", list(GROUP_MODES)],
                    "name": ["!=", self.name or ""],
                },
            )
            if clash:
                frappe.throw(_("You already have an appointment at this time."))
        if self.session_type == "First Session":
            other = frappe.db.exists(
                "Appointment",
                {
                    "client_id": self.client_id,
                    "session_type": "First Session",
                    "status": ["!=", "Cancelled"],
                    "name": ["!=", self.name or ""],
                },
            )
            if other:
                frappe.throw(_("This client already has a First Session. Use Follow-Up for later sessions."))

    def check_status(self):
        before = self.get_doc_before_save()
        if not before:
            return
        if before.status in ("Completed", "Cancelled") and not is_admin():
            frappe.throw(_("A {0} appointment cannot be changed.").format(before.status.lower()))
        if self.status == "Completed" and before.status != "Completed":
            if self.date_time and get_datetime(self.date_time) > now_datetime():
                frappe.throw(_("An appointment in the future cannot be marked as Completed."))
            required = (
                "session_details", "presenting_issues", "interventions_applied", "risk_assessment", "follow_up_plan",
            )
            missing = [frappe.unscrub(field) for field in required if not (self.get(field) or "").strip()]
            if missing:
                frappe.throw(_("Complete these session record fields first: {0}.").format(", ".join(missing)))
            if self.urgency_level not in ("Low", "Moderate", "High", "Immediate"):
                frappe.throw(_("Choose an urgency level before completing the session."))
            if self.session_type == "Follow-Up":
                followup_fields = ("progress_previous_goals", "counsellor_observations", "next_session_focus")
                missing_followup = [frappe.unscrub(field) for field in followup_fields if not (self.get(field) or "").strip()]
                if missing_followup:
                    frappe.throw(_("Complete these follow-up fields first: {0}.").format(", ".join(missing_followup)))
