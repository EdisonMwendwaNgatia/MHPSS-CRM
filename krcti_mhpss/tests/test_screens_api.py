import frappe

from krcti_mhpss.api import counsellor, session
from krcti_mhpss.tests.base import BaseCase


class TestScreensApi(BaseCase):
    def test_everyone_learns_their_own_role_and_guests_are_refused(self):
        expected = {self.ann: "counsellor", self.ben: "counsellor", self.kpm: "krcti_pm",
                    self.wpm: "woc_pm", self.sam: "admin", self.cli: "client"}
        for user, role in expected.items():
            frappe.set_user(user)
            self.assertEqual(session.me()["role"], role, user)
        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            session.me()

    def test_programme_managers_cannot_list_clients(self):
        self.client(self.ann, "TEST-510")
        for user in (self.kpm, self.wpm, self.cli):
            frappe.set_user(user)
            with self.assertRaises(frappe.PermissionError):
                counsellor.list_clients()

    def test_the_client_list_is_only_my_clients_and_the_total_is_too(self):
        mine = [self.client(self.ann, f"TEST-50{i}").name for i in range(3)]
        theirs = self.client(self.ben, "TEST-509").name
        frappe.set_user(self.ann)
        result = counsellor.list_clients()
        self.assertEqual({r.name for r in result["data"]}, set(mine))
        self.assertNotIn(theirs, [r.name for r in result["data"]])
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(counsellor.list_clients(page_length=2)["data"]), 2)
        self.assertEqual(counsellor.list_clients("Closed")["total"], 0)
    def tearDown(self):
        frappe.set_user("Administrator")

        codes = [
            "TEST-500",
            "TEST-501",
            "TEST-502",
            "TEST-509",
            "TEST-510",
        ]

        clients = frappe.get_all(
            "Client",
            filters={"scholar_code": ["in", codes]},
            pluck="name",
        )

        for doctype in ("Appointment", "Baseline Survey"):
            records = frappe.get_all(
                doctype,
                filters={"client_id": ["in", clients or ["-"]]},
                pluck="name",
            )
            for name in records:
                frappe.delete_doc(
                    doctype,
                    name,
                    force=True,
                    ignore_permissions=True,
                )

        for name in clients:
            frappe.delete_doc(
                "Client",
                name,
                force=True,
                ignore_permissions=True,
            )

        super().tearDown()