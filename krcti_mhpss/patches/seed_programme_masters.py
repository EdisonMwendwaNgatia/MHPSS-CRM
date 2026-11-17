import frappe


def ensure_master(doctype, fieldname, value):
    """Create an active master record only when it does not already exist."""
    if frappe.db.exists(doctype, value):
        return

    frappe.get_doc({
        "doctype": doctype,
        fieldname: value,
        "is_active": 1,
    }).insert(ignore_permissions=True)


def execute():
    # Approved entries plus historic values already in use so migrations do not
    # invalidate existing client records.
    institutions = {
        "Mary Immaculate Teachers Training college",
        "Meru National Polytechnic",
        "Nakuru Teachers Training college",
        "Nyandarua National Polytechnic",
        "Nyeri National Polytechnic",
    }
    courses = {
        "Diploma in Primary Teacher Education (DPTE)",
        "Diploma in Electricals and Electronics Engineering",
        "Diploma in Building Technician",
        "Diploma in Automotive Engineering Technician",
    }
    for value in frappe.get_all("Client", pluck="institution"):
        if value:
            institutions.add(value)
    for value in frappe.get_all("Client", pluck="course_programme"):
        if value:
            courses.add(value)

    for institution in sorted(institutions):
        ensure_master("Institution", "institution_name", institution)

    for programme in sorted(courses):
        ensure_master("Course Programme", "course_programme_name", programme)

    for programme in ("KRCTI", "WoC"):
        ensure_master("Study Programme", "study_programme_name", programme)
