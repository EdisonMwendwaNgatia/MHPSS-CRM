import { session } from "@/data/session"
import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"

const COUNSELLOR = ["counsellor"]
const OVERSIGHT = ["krcti_pm", "woc_pm"]
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
	{ path: "/follow-ups", name: "FollowUps", component: () => import("@/pages/FollowUps.vue"), meta: app(COUNSELLOR) },
	{ path: "/sessions", name: "SessionRecords", component: () => import("@/pages/SessionRecords.vue"), meta: app(COUNSELLOR) },
	{ path: "/sessions/:name", name: "SessionRecord", component: () => import("@/pages/SessionRecord.vue"), props: true, meta: app(COUNSELLOR) },
	{ path: "/programme", name: "Programme", component: () => import("@/pages/Programme.vue"), meta: app(OVERSIGHT) },
	{ path: "/programme/clients/new", name: "ProgrammeClientNew", component: () => import("@/pages/ClientForm.vue"), meta: app(OVERSIGHT) },
	{ path: "/programme/clients", name: "ProgrammeClients", component: () => import("@/pages/ProgrammeClients.vue"), meta: app(OVERSIGHT) },
	{ path: "/programme/clients/:name", name: "ProgrammeClientDetail", component: () => import("@/pages/ProgrammeOperations.vue"), props: { kind: "client" }, meta: app(OVERSIGHT) },
	{ path: "/programme/counsellors", name: "ProgrammeCounsellors", component: () => import("@/pages/ProgrammeOperations.vue"), props: { kind: "counsellors" }, meta: app(OVERSIGHT) },
	{ path: "/programme/sessions", name: "ProgrammeSessions", component: () => import("@/pages/ProgrammeSessionManagement.vue"), meta: app(OVERSIGHT) },
	{ path: "/programme/activity", name: "ProgrammeActivity", redirect: { name: "ProgrammeSessions" }, meta: app(OVERSIGHT) },
	{ path: "/audit-logs", name: "AuditLogs", component: () => import("@/pages/AuditLogs.vue"), meta: app(["dpo"]) },
]

const frontendBase = import.meta.env.VITE_APP_BASE || "/frontend"
const router = createRouter({ history: createWebHistory(frontendBase), routes })

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		// `promise` is null until a resource fetch is started. Fetch explicitly so
		// successful logins are verified against the backend session cookie.
		const user = await userResource.fetch()
		isLoggedIn = !!user && user !== "Guest"
		session.user = isLoggedIn ? user : null
	} catch (error) {
		isLoggedIn = false
	}
	if (to.name === "Login" && isLoggedIn) next({ name: "Home" })
	else if (to.name !== "Login" && !isLoggedIn) next({ name: "Login" })
	else next()
})

export default router
