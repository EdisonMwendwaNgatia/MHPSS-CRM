import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_to_date, now_datetime

from krcti_mhpss.install import ensure_roles
from krcti_mhpss.utils import ADMIN_ROLE, CLIENT_ROLE, COUNSELLOR, KRCTI_PM, WOC_PM

DOMAIN = "@test.krcti.local"
USERS = {"ann": COUNSELLOR, "ben": COUNSELLOR, "kpm": KRCTI_PM, "wpm": WOC_PM, "sam": ADMIN_ROLE, "cli": CLIENT_ROLE}


def client_data(code, **extra):
    return {
        "doctype": "Client", "scholar_code": code, "full_name": "Test Scholar", "phone_number": "0700 000 001",
        "age": 19, "gender": "Female", "sex": "Female", "institution": "Test TVET College",
        "course_programme": "Plumbing", "year_of_study": 1, "county_location": "Marsabit",
        "programme_stream": "Scholarship/Education", "referral_source": "School", **extra,
    }


def survey_data(client, **extra):
    return {
        "doctype": "Baseline Survey", "client_id": client, "consent": "Consented", "status": "Completed",
        "wellbeing_self_rating": 6, "stress_frequency": "Weekly", "main_concerns": "Exams and money",
        "support_availability": "Partial", "coping_ability": "Moderate", "interest_in_support": 1,
        "preferred_support_type": "Individual", "willingness_for_followup": 1,
        "coping_behaviour": "Talks to a friend", "marital_status": "Single", "dependants": 0,
        "domestic_situation": "Lives with relatives", "conflict_exposure": "No", **extra,
    }


def cleanup():
    frappe.set_user("Administrator")
    clients = frappe.get_all("Client", filters={"scholar_code": ["like", "TEST-%"]}, pluck="name")
    for doctype in ("Appointment", "Baseline Survey"):
        for name in frappe.get_all(doctype, filters={"client_id": ["in", clients or ["-"]]}, pluck="name"):
            frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
    for name in clients:
        frappe.delete_doc("Client", name, force=True, ignore_permissions=True)
    for user in frappe.get_all("User", filters={"name": ["like", f"%{DOMAIN}"]}, pluck="name"):
        frappe.delete_doc("User", user, force=True, ignore_permissions=True)


class BaseCase(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cleanup()
        ensure_roles()
        for short, role in USERS.items():
            address = f"{short}{DOMAIN}"
            frappe.get_doc(
                {"doctype": "User", "email": address, "first_name": short.title(), "send_welcome_email": 0,
                 "roles": [{"role": role}]}
            ).insert(ignore_permissions=True)
            setattr(cls, short, address)

    @classmethod
    def tearDownClass(cls):
        cleanup()
        super().tearDownClass()

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")

    def client(self, user, code, **extra):
        frappe.set_user(user)
        return frappe.get_doc(client_data(code, **extra)).insert()

    def appointment(self, user, client, hours=24, **extra):
        frappe.set_user(user)
        data = {"doctype": "Appointment", "client_id": client, "session_type": "Follow-Up",
                "mode_of_contact": "Phone Call", "date_time": add_to_date(now_datetime(), hours=hours), **extra}
        return frappe.get_doc(data).insert()

    
    def complete(self, appointment):
        frappe.set_user(appointment.counsellor_id)
        doc = frappe.get_doc("Appointment", appointment.name)
        doc.status = "Completed"
        doc.save()
        return doc
