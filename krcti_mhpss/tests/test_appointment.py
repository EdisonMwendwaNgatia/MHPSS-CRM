import frappe
from frappe.utils import add_to_date, now_datetime

from krcti_mhpss.api import counsellor
from krcti_mhpss.tests.base import BaseCase


class TestAppointment(BaseCase):
    def test_an_appointment_has_every_required_detail(self):
        client = self.client(self.ann, "TEST-200", full_name="Booked Person")
        appt = self.appointment(self.ann, client.name, hours=24, session_type="First Session",
                                mode_of_contact="Physical Individual", location="Marsabit campus")
        self.assertEqual((appt.status, appt.counsellor_id, appt.client_name), ("Scheduled", self.ann, "Booked Person"))
        self.assertTrue(appt.name.startswith("APT-"))
        self.assertTrue(appt.end_time)

    def test_physical_sessions_need_a_location(self):
        client = self.client(self.ann, "TEST-201")
        for mode in ("Physical Individual", "Physical Group", "School Campaign"):
            with self.assertRaises(frappe.ValidationError, msg=mode):
                self.appointment(self.ann, client.name, hours=26, mode_of_contact=mode)
        self.assertTrue(self.appointment(self.ann, client.name, hours=27, mode_of_contact="Tele-counselling").name)

    def test_an_appointment_can_be_edited_cancelled_and_completed(self):
        client = self.client(self.ann, "TEST-202")
        appt = self.appointment(self.ann, client.name, hours=48)
        appt.date_time = add_to_date(now_datetime(), hours=72)
        appt.save()
        appt.status = "Completed"
        with self.assertRaises(frappe.ValidationError):
            appt.save()  # in the future
        appt.reload()
        appt.status = "Cancelled"
        appt.save()
        appt.status = "Scheduled"
        with self.assertRaises(frappe.ValidationError):
            appt.save()  # cancelled is final
        done = self.complete(self.appointment(self.ann, client.name, hours=-6))
        self.assertEqual(done.status, "Completed")

    def test_the_calendar_list_shows_only_my_appointments_and_flags_overdue(self):
        mine = self.client(self.ann, "TEST-203")
        theirs = self.client(self.ben, "TEST-204")
        soon = self.appointment(self.ann, mine.name, hours=5)
        late = self.appointment(self.ann, mine.name, hours=-8)
        other = self.appointment(self.ben, theirs.name, hours=6)
        frappe.set_user(self.ann)
        result = counsellor.my_appointments(add_to_date(now_datetime(), days=-3).date(), add_to_date(now_datetime(), days=3).date())
        rows = {r.name: r for r in result["appointments"]}
        self.assertIn(soon.name, rows)
        self.assertNotIn(other.name, rows)
        self.assertTrue(rows[late.name]["overdue"])
        self.assertFalse(rows[soon.name]["overdue"])
        self.assertGreaterEqual(result["overdue_total"], 1)
        self.complete(late)
        frappe.set_user(self.ann)
        again = {r.name: r for r in counsellor.my_appointments()["appointments"]}
        self.assertFalse(again.get(late.name, {}).get("overdue", False))

    def test_a_counsellor_cannot_book_or_touch_another_counsellors_work(self):
        client = self.client(self.ann, "TEST-205")
        appt = self.appointment(self.ann, client.name, hours=60)
        with self.assertRaises(frappe.ValidationError):
            self.appointment(self.ben, client.name, hours=61)
        frappe.set_user(self.ben)
        self.assertNotIn(appt.name, [r.name for r in frappe.get_list("Appointment", limit=0)])
        doc = frappe.get_doc("Appointment", appt.name)
        doc.notes = "snooping"
        with self.assertRaises(frappe.PermissionError):
            doc.save()

    def test_double_booking_and_the_first_session_rule(self):
        client = self.client(self.ann, "TEST-206")
        other = self.client(self.ann, "TEST-207")
        slot = add_to_date(now_datetime(), hours=90)
        self.appointment(self.ann, client.name, date_time=slot)
        with self.assertRaises(frappe.ValidationError):
            self.appointment(self.ann, other.name, date_time=slot)
        self.assertTrue(self.appointment(self.ann, other.name, date_time=slot, mode_of_contact="Physical Group",
                                         location="Hall").name)  # a group session may share the slot
        self.appointment(self.ann, client.name, hours=100, session_type="First Session")
        with self.assertRaises(frappe.ValidationError):
            self.appointment(self.ann, client.name, hours=101, session_type="First Session")

    def test_a_closed_case_takes_no_new_appointments(self):
        client = self.client(self.ann, "TEST-208")
        frappe.db.set_value("Client", client.name, "case_status", "Closed")
        with self.assertRaises(frappe.ValidationError):
            self.appointment(self.ann, client.name, hours=70)