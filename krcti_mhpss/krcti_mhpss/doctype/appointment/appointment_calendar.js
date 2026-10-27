frappe.views.calendar["Appointment"] = {
	field_map: { start: "date_time", end: "end_time", id: "name", title: "client_name" },
	get_css_class(doc) {
		if (doc.status === "Cancelled") return "danger"
		if (doc.status === "Completed") return "success"
		return "warning"
	},
}
