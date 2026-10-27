import json

import frappe

from krcti_mhpss.api import counsellor, oversight
from krcti_mhpss.tests.base import BaseCase, USERS
from krcti_mhpss.utils import COUNSELLOR, KRCTI_PM


class TestRoleMatrix(BaseCase):
    def test_every_role_exists_and_an_account_holds_exactly_one(self):
        for role in set(USERS.values()):
            self.assertTrue(frappe.db.exists("Role", role), role)
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({"doctype": "User", "email": f"two{self.ann[3:]}", "first_name": "Two", "send_welcome_email": 0,
                            "roles": [{"role": COUNSELLOR}, {"role": KRCTI_PM}]}).insert(ignore_permissions=True)

    def test_role_changes_are_recorded(self):
        user = frappe.get_doc("User", self.ben)

        try:
            user.roles = []
            user.append("roles", {"role": KRCTI_PM})
            user.save(ignore_permissions=True)

            notes = frappe.get_all(
                "Comment",
                filters={
                    "reference_doctype": "User",
                    "reference_name": self.ben,
                },
                pluck="content",
            )

            self.assertTrue(
                any(COUNSELLOR in note and KRCTI_PM in note for note in notes)
            )
        finally:
            user = frappe.get_doc("User", self.ben)
            user.roles = []
            user.append("roles", {"role": COUNSELLOR})
            user.save(ignore_permissions=True)

    def test_the_administrator_sees_everything_and_the_counsellor_cannot_delete(self):
        mine = self.client(self.ann, "TEST-300")
        theirs = self.client(self.ben, "TEST-301")
        frappe.set_user(self.sam)
        names = [r.name for r in frappe.get_list("Client", limit=0)]
        self.assertIn(mine.name, names)
        self.assertIn(theirs.name, names)
        frappe.set_user(self.ann)
        with self.assertRaises(frappe.PermissionError):
            frappe.delete_doc("Client", mine.name)

    def test_counsellors_never_see_each_others_lists(self):
        mine = self.client(self.ann, "TEST-302")
        theirs = self.client(self.ben, "TEST-303")
        frappe.set_user(self.ann)
        names = [r.name for r in frappe.get_list("Client", limit=0)]
        self.assertIn(mine.name, names)
        self.assertNotIn(theirs.name, names)
        self.assertFalse(frappe.has_permission("Client", "read", theirs.name))

    def test_programme_managers_and_clients_have_no_record_access(self):
        client = self.client(self.ann, "TEST-304")
        self.appointment(self.ann, client.name, hours=33)
        for user in (self.kpm, self.wpm, self.cli):
            frappe.set_user(user)
            for doctype in ("Client", "Baseline Survey", "Appointment"):
                with self.assertRaises(frappe.PermissionError, msg=f"{user} {doctype}"):
                    frappe.get_list(doctype)
            self.assertFalse(frappe.has_permission("Client", "read", client.name))
            with self.assertRaises(frappe.PermissionError):
                counsellor.search_clients("TEST-304")
            with self.assertRaises(frappe.PermissionError):
                counsellor.client_profile(client.name)

    def test_the_programme_views_carry_numbers_only_and_differ_by_role(self):
        client = self.client(self.ann, "TEST-305", full_name="Secret Person", phone_number="0799123456")
        self.complete(self.appointment(self.ann, client.name, hours=-9))
        frappe.set_user(self.kpm)
        krcti = oversight.programme_summary()
        calendar = oversight.programme_calendar()
        frappe.set_user(self.wpm)
        woc = oversight.programme_summary()
        for payload in (krcti, calendar, woc):
            text = json.dumps(payload, default=str)
            for secret in ("Secret Person", "0799123456", "TEST-305", client.name):
                self.assertNotIn(secret, text)
        self.assertEqual(krcti["scope"], "KRCTI")
        self.assertIn("Ann", [row["counsellor"] for row in krcti["by_counsellor"]])
        self.assertEqual(woc["scope"], "WoC")
        self.assertIsNone(woc["by_counsellor"])
        with self.assertRaises(frappe.PermissionError):
            oversight.programme_calendar()  # the WoC manager does not get the KRCTI calendar
        for user in (self.ann, self.cli):
            frappe.set_user(user)
            with self.assertRaises(frappe.PermissionError):
                oversight.programme_summary()