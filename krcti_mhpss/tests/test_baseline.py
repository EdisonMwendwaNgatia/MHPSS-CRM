import frappe

from krcti_mhpss.api import counsellor
from krcti_mhpss.tests.base import BaseCase, survey_data


class TestBaseline(BaseCase):
    def test_a_full_survey_is_saved_and_stamped(self):
        client = self.client(self.ann, "TEST-100", full_name="Survey Person")
        frappe.set_user(self.ann)
        doc = frappe.get_doc(survey_data(client.name)).insert()
        self.assertEqual((doc.status, doc.completed_by, doc.client_name), ("Completed", self.ann, "Survey Person"))
        self.assertTrue(doc.completed_on)

    def test_only_one_survey_per_client(self):
        client = self.client(self.ann, "TEST-101")
        frappe.set_user(self.ann)
        frappe.get_doc(survey_data(client.name)).insert()
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(survey_data(client.name)).insert()

    def test_consent_is_explicit_and_a_declination_is_recorded(self):
        client = self.client(self.ann, "TEST-102")
        frappe.set_user(self.ann)
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({"doctype": "Baseline Survey", "client_id": client.name}).insert()
        doc = frappe.get_doc({"doctype": "Baseline Survey", "client_id": client.name, "consent": "Declined",
                              "declined_reason": "Not ready"}).insert()
        self.assertEqual(doc.status, "Declined")
        # The counsellor can still book sessions without baseline data.
        self.assertTrue(self.appointment(self.ann, client.name, hours=30).name)

    def test_a_submitted_survey_is_locked_except_for_the_administrator(self):
        client = self.client(self.ann, "TEST-103")
        frappe.set_user(self.ann)
        doc = frappe.get_doc(survey_data(client.name)).insert()
        doc.main_concerns = "Changed"
        with self.assertRaises(frappe.ValidationError):
            doc.save()
        frappe.set_user(self.sam)
        doc.reload()
        doc.main_concerns = "Corrected by the administrator"
        doc.save()

    def test_a_draft_can_be_partial_but_not_completed(self):
        client = self.client(self.ann, "TEST-104")
        frappe.set_user(self.ann)
        draft = frappe.get_doc({"doctype": "Baseline Survey", "client_id": client.name, "consent": "Consented",
                                "status": "Pending", "main_concerns": "Started"}).insert()
        draft.status = "Completed"
        with self.assertRaises(frappe.ValidationError):
            draft.save()
        draft.reload()
        draft.wellbeing_self_rating = 11
        with self.assertRaises(frappe.ValidationError):
            draft.save()

    def test_a_counsellor_cannot_survey_or_see_another_counsellors_client(self):
        client = self.client(self.ann, "TEST-105")
        frappe.set_user(self.ann)
        survey = frappe.get_doc(survey_data(client.name)).insert()
        frappe.set_user(self.ben)
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(survey_data(client.name)).insert()
        self.assertNotIn(survey.name, [r.name for r in frappe.get_list("Baseline Survey", limit=0)])
        self.assertFalse(frappe.has_permission("Baseline Survey", "read", survey.name))

    def test_the_survey_is_visible_read_only_inside_the_client_profile(self):
        client = self.client(self.ann, "TEST-106")
        frappe.set_user(self.ann)
        self.assertIsNone(counsellor.client_profile(client.name)["survey"])
        frappe.get_doc(survey_data(client.name)).insert()
        self.assertEqual(counsellor.client_profile(client.name)["survey"]["main_concerns"], "Exams and money")
        frappe.set_user(self.ben)
        with self.assertRaises(frappe.DoesNotExistError):
            counsellor.client_profile(client.name)