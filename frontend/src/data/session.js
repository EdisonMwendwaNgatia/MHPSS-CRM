import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

const frontendBase = (import.meta.env.VITE_APP_BASE || "/frontend").replace(/\/$/, "")

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let user = cookies.get("user_id")
	if (user === "Guest") user = null
	return user
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return { usr: email, pwd: password }
		},
		onSuccess() {
			window.location.assign(`${frontendBase}/` || "/")
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			window.location.assign(`${frontendBase}/login`)
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})
