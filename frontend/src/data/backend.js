const frappeUrl = import.meta.env.VITE_FRAPPE_URL?.replace(/\/+$/, "")

export function backendUrl(path) {
	if (!path) return ""
	if (/^(https?:)?\/\//i.test(path) || !frappeUrl) return path
	if (import.meta.env.VITE_FRAPPE_PROXY === "1") return path
	return `${frappeUrl}${path.startsWith("/") ? path : `/${path}`}`
}
