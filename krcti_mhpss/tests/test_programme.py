import frappe

from krcti_mhpss.api import oversight
from krcti_mhpss.tests.base import BaseCase


class TestProgrammeNumbers(BaseCase):
    def setUp(self):
        super().setUp()
        suffix = "A" if (
            self._testMethodName == "test_the_counsellor_table_and_the_totals_are_right"
        ) else "B"

        a1 = self.client(self.ann, f"TP{suffix}-400")
        a2 = self.client(self.ann, f"TP{suffix}-401")
        b1 = self.client(self.ben, f"TP{suffix}-402")
        self.complete(self.appointment(self.ann, a1.name, hours=-5))
        self.complete(self.appointment(self.ben, b1.name, hours=-7, mode_of_contact="Physical Individual", location="Hall"))
        self.appointment(self.ann, a2.name, hours=40)
        self.appointment(self.ann, a1.name, hours=-12)  # overdue

    def test_the_counsellor_table_and_the_totals_are_right(self):
        frappe.set_user(self.kpm)
        data = oversight.programme_summary()
        rows = {r["counsellor"]: r for r in data["by_counsellor"]}
        self.assertEqual(
            {k: rows["Ann"][k] for k in ("active_caseload", "completed_in_range", "upcoming", "overdue")},
            {"active_caseload": 2, "completed_in_range": 1, "upcoming": 1, "overdue": 1},
        )
        self.assertEqual((rows["Ben"]["active_caseload"], rows["Ben"]["completed_in_range"]), (1, 1))
        self.assertGreaterEqual(data["sessions_by_mode"]["Phone Call"], 1)
        self.assertGreaterEqual(data["sessions_by_mode"]["Physical Individual"], 1)
        self.assertEqual(set(data["sessions_by_mode"]), {"Physical Individual", "Physical Group", "Tele-counselling", "Phone Call", "School Campaign"})

    def test_the_date_range_is_respected(self):
        frappe.set_user(self.kpm)
        old = oversight.programme_summary("2000-01-01", "2000-01-31")
        self.assertEqual(sum(old["sessions_by_mode"].values()), 0)
        with self.assertRaises(frappe.ValidationError):
            oversight.programme_summary("2000-01-01", "2030-01-01")