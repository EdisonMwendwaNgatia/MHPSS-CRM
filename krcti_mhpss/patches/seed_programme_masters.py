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
    # Existing institutions.
    for institution in (
        "Taita College",
        "Taita Taveta College",
        "Vuria College",
    ):
        ensure_master("Institution", "institution_name", institution)

    # Existing course programmes.
    for programme in (
        "Graphic Design",
        "Dress Making",
    ):
        ensure_master("Course Programme", "course_programme_name", programme)

    # Programme ownership options.
    for programme in ("KRCTI", "WoC"):
        ensure_master("Study Programme", "study_programme_name", programme)

    # Normalize the institution name for the existing record.
    if frappe.db.exists("Client", "CL-00021"):
        frappe.db.set_value(
            "Client",
            "CL-00021",
            "institution",
            "Taita Taveta College",
            update_modified=False,
        )

    # Assign all four existing clients to WoC.
    for client_name in ("CL-00009", "CL-00010", "CL-00018", "CL-00021"):
        if frappe.db.exists("Client", client_name):
            frappe.db.set_value(
                "Client",
                client_name,
                "study_programme",
                "WoC",
                update_modified=False,
            )
