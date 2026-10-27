import { computed, ref } from "vue"

const pending = ref(0) // API requests in flight
const routeLoading = ref(false) // a page is being fetched

// Requests the app repeats in the background, such as waiting for a crop check. They never show the bar.
const QUIET = ["/api/method/grocery_point.api.farming_tools.diagnosis_detail"]

export const busy = computed(() => pending.value > 0 || routeLoading.value)

export function setRouteLoading(value) {
	routeLoading.value = value
}

function isTracked(url) {
	return url.includes("/api/method/") && !QUIET.some((quiet) => url.includes(quiet))
}

// Counts every API call, whoever makes it, so no page needs its own bookkeeping.
export function installBusyTracking() {
	if (window.__gpBusyInstalled) return
	window.__gpBusyInstalled = true
	const original = window.fetch.bind(window)
	window.fetch = (input, init) => {
		const url = typeof input === "string" ? input : input?.url || String(input)
		if (!isTracked(url)) return original(input, init)
		pending.value += 1
		return original(input, init).finally(() => {
			pending.value = Math.max(0, pending.value - 1)
		})
	}
}

// Installed when this file is first loaded, so it must be the first import in main.js.
installBusyTracking()