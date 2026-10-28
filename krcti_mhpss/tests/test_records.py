from pathlib import Path

import frappe
from frappe.utils import add_to_date, now_datetime

from krcti_mhpss.api import records
from krcti_mhpss.tests.base import BaseCase, client_data, survey_data

ANSWERS = {k: v for k, v in survey_data("x").items() if k not in ("doctype", "client_id", "status")}


def payload(**extra):
    data = {k: v for k, v in client_data("ignored").items() if k not in ("doctype", "scholar_code")}
    data.update(extra)
    return data


class TestRecords(BaseCase):
    def test_a_client_is_registered_with_server_set_fields_only(self):
        frappe.set_user(self.ann)
        name = records.save_client(None, payload(full_name="Auto Code Test"))["name"]
        doc = frappe.get_doc("Client", name)
        self.assertRegex(doc.scholar_code, r"^WoC-\d{4}$")
        self.assertEqual((doc.assigned_counsellor, doc.case_status), (self.ann, "Active"))
        for bad in ({"scholar_code": "TEST-601"}, {"assigned_counsellor": self.ben}, {"case_status": "Closed"}, {"owner": self.ben},
                    {"name": "CL-99999"}, {"docstatus": 1}):
            with self.assertRaises(frappe.ValidationError, msg=str(bad)):
                records.save_client(None, payload(**bad))
        self.assertFalse(frappe.db.exists("Client", {"scholar_code": "TEST-601"}))

    def test_updates_change_only_the_allowed_fields_on_your_own_clients(self):
        client = self.client(self.ann, "TEST-610")
        frappe.set_user(self.ann)
        records.save_client(client.name, {"phone_number": "0711 111 111", "year_of_study": 2})
        self.assertEqual(frappe.db.get_value("Client", client.name, ["phone_number", "year_of_study"]), ("0711111111", 2))
        for bad in ({"scholar_code": "TEST-X"}, {"assigned_counsellor": self.ben}, {"case_status": "Closed"}):
            with self.assertRaises(frappe.ValidationError, msg=str(bad)):
                records.save_client(client.name, bad)
        frappe.set_user(self.ben)
        with self.assertRaises(frappe.DoesNotExistError):
            records.save_client(client.name, {"phone_number": "0722 222 222"})

    def test_the_generic_api_cannot_bypass_the_protected_fields(self):
        from frappe.client import set_value

        client = self.client(self.ann, "TEST-620")
        frappe.set_user(self.ann)
        for field, value in (
            ("scholar_code", "TEST-HACK"),
            ("assigned_counsellor", self.ben),
        ):
            expected = (
                (frappe.ValidationError, frappe.PermissionError)
                if field == "assigned_counsellor"
                else frappe.ValidationError
            )

            with self.assertRaises(expected, msg=field):
                set_value("Client", client.name, field, value)
        frappe.set_user(self.sam)
        set_value("Client", client.name, "scholar_code", "TEST-620B")  # the administrator may correct a code
        self.assertEqual(frappe.db.get_value("Client", client.name, "scholar_code"), "TEST-620B")

    def test_survey_stamps_cannot_be_forged(self):
        client = self.client(self.ann, "TEST-630")
        frappe.set_user(self.ann)
        doc = frappe.get_doc(
            survey_data(client.name, completed_by=self.ben, completed_on="2020-01-01 00:00:00")
        ).insert()
        doc.reload()
        self.assertEqual(doc.completed_by, self.ann)
        self.assertNotEqual(str(doc.completed_on)[:4], "2020")
        stamp = (doc.completed_by, doc.completed_on)

        frappe.set_user(self.sam)
        doc.main_concerns = "Corrected by the administrator"
        doc.completed_by = self.ben
        doc.completed_on = "2021-01-01 00:00:00"
        doc.save()
        doc.reload()
        self.assertEqual((doc.completed_by, doc.completed_on), stamp)

    def test_the_baseline_endpoint_sets_status_and_stamps_itself(self):
        client = self.client(self.ann, "TEST-640")
        frappe.set_user(self.ann)
        for bad in ({"status": "Pending"}, {"completed_by": self.ben}, {"client_id": "x"}):
            with self.assertRaises(frappe.ValidationError, msg=str(bad)):
                records.record_baseline(client.name, {"consent": "Consented", **ANSWERS, **bad})
        for incomplete in ({"consent": "Maybe"}, {"consent": "Consented"}, {}):
            with self.assertRaises(frappe.ValidationError, msg=str(incomplete)):
                records.record_baseline(client.name, incomplete)

        name = records.record_baseline(client.name, {"consent": "Consented", **ANSWERS})["name"]
        doc = frappe.get_doc("Baseline Survey", name)
        self.assertEqual((doc.status, doc.completed_by), ("Completed", self.ann))
        with self.assertRaises(frappe.ValidationError):
            records.record_baseline(client.name, {"consent": "Declined"})  # one survey per client

        other = self.client(self.ann, "TEST-641")
        declined = records.record_baseline(other.name, {"consent": "Declined", "declined_reason": "Not ready"})["name"]
        self.assertEqual(frappe.db.get_value("Baseline Survey", declined, "status"), "Declined")
        frappe.set_user(self.ben)
        with self.assertRaises(frappe.DoesNotExistError):
            records.record_baseline(client.name, {"consent": "Declined"})

    def test_the_appointment_endpoints(self):
        client = self.client(self.ann, "TEST-650")
        frappe.set_user(self.ann)
        when = str(add_to_date(now_datetime(), hours=48))
        good = {"date_time": when, "session_type": "Follow-Up", "mode_of_contact": "Phone Call"}
        for bad in ({"counsellor_id": self.ben}, {"status": "Completed"}, {"client_id": "x"}, {"end_time": when}):
            with self.assertRaises(frappe.ValidationError, msg=str(bad)):
                records.save_appointment(None, client.name, {**good, **bad})

        name = records.save_appointment(None, client.name, good)["name"]
        detail = records.appointment_detail(name)
        self.assertEqual((detail["client_id"], detail["counsellor_id"], detail["status"]), (client.name, self.ann, "Scheduled"))
        records.save_appointment(name, None, {"notes": "Bring the form", "mode_of_contact": "Tele-counselling"})
        self.assertEqual(frappe.db.get_value("Appointment", name, "notes"), "Bring the form")
        for bad_status in ("Completed", "Pending"):  # the first is still in the future
            with self.assertRaises(frappe.ValidationError, msg=bad_status):
                records.set_appointment_status(name, bad_status)

        past = self.appointment(self.ann, client.name, hours=-5)
        frappe.set_user(self.ann)
        with self.assertRaises(frappe.ValidationError):
            records.set_appointment_status(past.name, "Completed")
        records.record_session(past.name, {
            "session_details": "Session completed.", "presenting_issues": "Concerns reviewed.",
            "interventions_applied": "Supportive counselling.", "urgency_level": "Low",
            "risk_assessment": "No immediate risk identified.", "follow_up_plan": "Review next time.",
            "progress_previous_goals": "Progress reviewed.", "counsellor_observations": "Engaged.",
            "next_session_focus": "Continue current goals.",
        })
        self.assertEqual(frappe.db.get_value("Appointment", past.name, "status"), "Completed")
        with self.assertRaises(frappe.ValidationError):
            records.set_appointment_status(past.name, "Cancelled")
        with self.assertRaises(frappe.ValidationError):
            records.save_appointment(past.name, None, {"notes": "edit"})
        records.set_appointment_status(name, "Cancelled")

        frappe.set_user(self.ben)
        for call in (
            lambda: records.appointment_detail(name),
            lambda: records.set_appointment_status(name, "Cancelled"),
            lambda: records.save_appointment(name, None, {"notes": "x"}),
            lambda: records.save_appointment(None, client.name, good),
        ):
            with self.assertRaises(frappe.DoesNotExistError):
                call()

    def test_the_case_status_endpoint(self):
        client = self.client(self.ann, "TEST-660")
        frappe.set_user(self.ann)
        records.set_case_status(client.name, "Follow-Up Pending")
        self.assertEqual(frappe.db.get_value("Client", client.name, "case_status"), "Follow-Up Pending")
        for bad in ("Archived", "", None):
            with self.assertRaises(frappe.ValidationError, msg=str(bad)):
                records.set_case_status(client.name, bad)
        with self.assertRaises(frappe.ValidationError):
            records.set_case_status(client.name, "Closed")  # no completed Termination session yet

        self.complete(self.appointment(self.ann, client.name, hours=-4, session_type="Termination"))
        frappe.set_user(self.ann)
        records.set_case_status(client.name, "Closed")
        with self.assertRaises(frappe.ValidationError):
            records.set_case_status(client.name, "Active")  # a counsellor cannot re-open
        frappe.set_user(self.sam)
        records.set_case_status(client.name, "Active")

    def test_nobody_else_can_use_the_write_endpoints(self):
        client = self.client(self.ann, "TEST-670")
        calls = (
            lambda: records.save_client(None, payload()),
            lambda: records.save_client(client.name, {"age": 20}),
            lambda: records.set_case_status(client.name, "Active"),
            lambda: records.record_baseline(client.name, {"consent": "Declined"}),
            lambda: records.save_appointment(None, client.name, {}),
            lambda: records.set_appointment_status("APT-00001", "Cancelled"),
            lambda: records.appointment_detail("APT-00001"),
        )
        for user in (self.kpm, self.wpm, self.cli):
            frappe.set_user(user)
            for call in calls:
                with self.assertRaises(frappe.PermissionError, msg=user):
                    call()
        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            calls[0]()

    def test_the_screens_never_call_the_generic_client_methods(self):
        source = Path(frappe.get_app_path("krcti_mhpss")).parent / "frontend" / "src"
        if not source.exists():
            self.skipTest("The frontend source is not on this machine.")
        offenders = [str(p) for p in source.rglob("*") if p.suffix in (".vue", ".js") and "frappe.client." in p.read_text()]
        self.assertEqual(offenders, [])
