import { createResource } from "frappe-ui"

// This endpoint is read-only. GET avoids CSRF validation for the auth check,
// which is important when the SPA is served separately from Frappe.
export const userResource = createResource({
	url: "frappe.auth.get_logged_user",
	method: "GET",
	cache: "User",
})
