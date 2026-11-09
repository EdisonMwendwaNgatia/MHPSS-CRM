import "./data/busy"
import { Badge, Button, ErrorMessage, FormControl, FrappeUI, TextInput, frappeRequest, setConfig } from "frappe-ui"
import { createApp } from "vue"
import App from "./App.vue"
import PageLoader from "./components/PageLoader.vue"
import Spinner from "./components/Spinner.vue"
import "./index.css"
import router from "./router"

const globalComponents = { Badge, Button, ErrorMessage, FormControl, TextInput, PageLoader, Spinner }

// When hosted separately from Frappe, send API requests to the backend with the
// browser's session cookies. Local bench development continues to use Vite's proxy.
const frappeUrl = import.meta.env.VITE_FRAPPE_URL?.replace(/\/+$/, "")
if (frappeUrl) {
	const backend = new URL(frappeUrl)
	const useSameOriginProxy = import.meta.env.VITE_FRAPPE_PROXY === "1"
	const browserFetch = window.fetch.bind(window)
	window.fetch = (input, init = {}) => {
		const requestUrl = input instanceof Request ? input.url : String(input)
		const url = new URL(requestUrl, window.location.href)
		if (url.origin !== window.location.origin || !url.pathname.startsWith("/api/")) {
			return browserFetch(input, init)
		}
		const headers = new Headers(input instanceof Request ? input.headers : undefined)
		new Headers(init.headers || {}).forEach((value, name) => headers.set(name, value))
		headers.set("X-Frappe-Site-Name", import.meta.env.VITE_FRAPPE_SITE_NAME || backend.hostname)
		if (!useSameOriginProxy) {
			url.host = backend.host
			url.protocol = backend.protocol
			url.username = backend.username
			url.password = backend.password
		}
		const request = input instanceof Request ? new Request(url.toString(), input) : url.toString()
		return browserFetch(request, { ...init, headers, credentials: "include" })
	}
}

const app = createApp(App)
setConfig("resourceFetcher", frappeRequest)
app.use(FrappeUI, { socketio: frappeUrl ? false : true })
app.use(router)
for (const [name, component] of Object.entries(globalComponents)) app.component(name, component)
app.mount("#app")
