import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

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
			window.location.assign("/frontend/")
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			window.location.assign("/frontend/login")
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})