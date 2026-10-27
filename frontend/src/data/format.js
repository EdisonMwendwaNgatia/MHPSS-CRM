const when = (v) => new Date(String(v).replace(" ", "T"))

export const fmtDate = (v) =>
	v ? when(v).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" }) : ""
export const fmtTime = (v) => (v ? when(v).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "")
export const fmtDateTime = (v) => (v ? `${fmtDate(v)}, ${fmtTime(v)}` : "")
export const toInput = (v) => (v ? String(v).slice(0, 16).replace(" ", "T") : "")
export const fromInput = (v) => (v ? `${String(v).replace("T", " ")}${String(v).length === 16 ? ":00" : ""}` : "")
export const dayKey = (v) => String(v).slice(0, 10)

export const caseTheme = (s) => ({ Active: "green", "Follow-Up Pending": "orange", Closed: "gray" })[s] || "gray"
export const apptLabel = (row) => (row.overdue ? "Overdue" : row.status)
export const apptTheme = (row) =>
	row.overdue ? "red" : ({ Scheduled: "blue", Completed: "green", Cancelled: "gray" })[row.status] || "gray"