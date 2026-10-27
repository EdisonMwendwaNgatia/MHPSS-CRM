import { session } from "@/data/session"
import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"

const COUNSELLOR = ["counsellor", "admin"]
const OVERSIGHT = ["krcti_pm", "woc_pm", "admin"]
const app = (roles) => ({ app: true, roles })

const routes = [
	{ path: "/", redirect: { name: "Home" } },
	{ path: "/login", name: "Login", component: () => import("@/pages/Login.vue") },
	{ path: "/home", name: "Home", component: () => import("@/pages/Home.vue"), meta: { app: true } },
	{ path: "/clients", name: "Clients", component: () => import("@/pages/Clients.vue"), meta: app(COUNSELLOR) },
	{ path: "/clients/new", name: "ClientNew", component: () => import("@/pages/ClientForm.vue"), meta: app(COUNSELLOR) },
	{ path: "/clients/:name", name: "ClientProfile", component: () => import("@/pages/ClientProfile.vue"), props: true, meta: app(COUNSELLOR) },
	{ path: "/clients/:name/edit", name: "ClientEdit", component: () => import("@/pages/ClientForm.vue"), props: true, meta: app(COUNSELLOR) },
	{ path: "/clients/:name/baseline", name: "Baseline", component: () => import("@/pages/BaselineForm.vue"), props: true, meta: app(COUNSELLOR) },
	{ path: "/appointments", name: "Appointments", component: () => import("@/pages/Appointments.vue"), meta: app(COUNSELLOR) },
	{ path: "/appointments/new", name: "AppointmentNew", component: () => import("@/pages/AppointmentForm.vue"), meta: app(COUNSELLOR) },
	{ path: "/appointments/:name", name: "AppointmentEdit", component: () => import("@/pages/AppointmentForm.vue"), props: true, meta: app(COUNSELLOR) },
	{ path: "/programme", name: "Programme", component: () => import("@/pages/Programme.vue"), meta: app(OVERSIGHT) },
]

const router = createRouter({ history: createWebHistory("/frontend"), routes })

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}
	if (to.name === "Login" && isLoggedIn) next({ name: "Home" })
	else if (to.name !== "Login" && !isLoggedIn) next({ name: "Login" })
	else next()
})

export default router