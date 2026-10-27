frappe.listview_settings["Appointment"] = {
	add_fields: ["status", "date_time"],
	get_indicator(doc) {
		if (doc.status === "Scheduled" && doc.date_time && frappe.datetime.str_to_obj(doc.date_time) < new Date()) {
			return [__("Overdue"), "red", "status,=,Scheduled"]
		}
		const colors = { Scheduled: "blue", Completed: "green", Cancelled: "gray" }
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status]
	},
}
