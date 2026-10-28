import frappe

from frappe.permissions import has_controller_permissions
from krcti_mhpss.api import counsellor
from krcti_mhpss.tests.base import BaseCase, client_data
from krcti_mhpss.permissions import client_has_permission
import traceback


class TestClient(BaseCase):
    def test_a_counsellor_registers_a_client_with_every_field(self):
        doc = self.client(self.ann, "test-001", disability_status=1, disability_type="Hearing",
                          refugee_status=1, referral_source="Other", referral_source_other="Chief")
        self.assertTrue(doc.name.startswith("CL-"))
        self.assertEqual(doc.scholar_code, "TEST-001")
        self.assertEqual((doc.assigned_counsellor, doc.case_status, doc.phone_number), (self.ann, "Active", "0700000001"))
        self.assertEqual((doc.disability_type, doc.refugee_status), ("Hearing", 1))

    def test_every_required_field_is_enforced(self):
        frappe.set_user(self.ann)
        required = ("full_name", "phone_number", "age", "gender", "institution",
                    "course_programme", "year_of_study", "county_location", "programme_stream", "referral_source")
        for name in required:
            data = client_data("TEST-REQ")
            data.pop(name)
            with self.assertRaises(frappe.ValidationError, msg=name):
                frappe.get_doc(data).insert()

    def test_a_duplicate_code_is_caught_without_leaking_another_counsellors_client(self):
        first = self.client(self.ann, "TEST-010").name
        frappe.set_user(self.ann)
        with self.assertRaises(frappe.ValidationError) as own:
            frappe.get_doc(client_data(" test-010 ")).insert()
        self.assertIn(first, str(own.exception))

        frappe.set_user(self.ben)
        with self.assertRaises(frappe.ValidationError) as other:
            frappe.get_doc(client_data("TEST-010")).insert()
        self.assertNotIn(first, str(other.exception))
        self.assertNotIn("Test Scholar", str(other.exception))

        frappe.set_user(self.sam)
        with self.assertRaises(frappe.ValidationError) as admin:
            frappe.get_doc(client_data("TEST-010")).insert()
        self.assertIn(first, str(admin.exception))

    def test_clients_are_found_by_code_name_phone_and_institution(self):
        name = self.client(self.ann, "TEST-020", full_name="Zuri Searchable", institution="Searchable College",
                           phone_number="+254 712 345 678").name
        frappe.set_user(self.ann)
        for term in ("TEST-020", "zuri searchable", "Searchable Col", "0712345678", "712 345 678", "+254712345678"):
            self.assertIn(name, [r.name for r in counsellor.search_clients(term)], term)
        self.assertEqual(counsellor.search_clients("x"), [])
        frappe.set_user(self.ben)
        self.assertNotIn(name, [r.name for r in counsellor.search_clients("TEST-020")])

    def test_the_referral_source_is_recorded_and_checked(self):
        doc = self.client(self.ann, "TEST-030", referral_source="Peer")
        self.assertEqual(doc.referral_source, "Peer")
        frappe.set_user(self.ann)
        for bad in ("", "Radio"):
            with self.assertRaises(frappe.ValidationError):
                frappe.get_doc(client_data("TEST-031", referral_source=bad)).insert()

    def test_the_case_status_rules(self):
        doc = self.client(self.ann, "TEST-060", case_status="Closed")
        self.assertEqual(doc.case_status, "Active")
        doc.case_status = "Follow-Up Pending"
        doc.save()
        doc.case_status = "Closed"
        with self.assertRaises(frappe.ValidationError):
            doc.save()  # no completed Termination session yet

        self.complete(self.appointment(self.ann, doc.name, hours=-4, session_type="Termination"))
        frappe.set_user(self.ann)
        doc.reload()
        doc.case_status = "Closed"
        doc.save()
        doc.phone_number = "0711111111"
        with self.assertRaises(frappe.ValidationError):
            doc.save()  # closed records are read-only

        frappe.set_user(self.sam)
        doc.reload()
        doc.case_status = "Active"
        doc.save()  # the administrator can re-open it

    def test_a_counsellor_can_update_details_but_not_reassign(self):
        doc = self.client(self.ann, "TEST-070")
        doc.phone_number = "0722 222 222"
        doc.institution = "New College"
        doc.year_of_study = 2
        doc.save()
        doc.reload()

        self.assertEqual(
            (doc.phone_number, doc.institution, doc.year_of_study),
            ("0722222222", "New College", 2),
        )
        doc.assigned_counsellor = self.ben
        with self.assertRaises(frappe.PermissionError):
            doc.save()

        frappe.set_user(self.sam)
        doc.reload()
        doc.assigned_counsellor = self.ben
        doc.save()
        frappe.set_user(self.ann)
        self.assertFalse(frappe.has_permission("Client", "read", doc.name))

    def test_bad_values_are_refused(self):
        frappe.set_user(self.ann)
        bad = ({"age": 5}, {"age": 120}, {"year_of_study": 0}, {"year_of_study": 9}, {"phone_number": "123"},
               {"disability_status": 1}, {"scholar_code": "!!"})
        for i, extra in enumerate(bad):
            with self.assertRaises(frappe.ValidationError, msg=str(extra)):
                frappe.get_doc(client_data(f"TEST-V{i}", **extra)).insert()
        frappe.set_user(self.sam)
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(client_data("TEST-V9", assigned_counsellor=self.kpm)).insert()
