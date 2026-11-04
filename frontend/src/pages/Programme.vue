<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1200px]">
      <!-- Page header -->
      <div>
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl font-semibold leading-8">{{ data?.scope === "WoC" ? "WoC Programme Dashboard" : "KRCTI PM Dashboard" }}</h1>
            <p class="mt-0.5 text-sm text-[#5B616B]">{{ data?.scope === "WoC" ? "WoC Scholarship Fund aggregate service monitoring" : "Service delivery across KRCTI counsellors" }}</p>
          </div>
          <div class="flex gap-2 no-print">
            <button type="button" class="export-button" @click="exportCsv"><Download :size="16" /> Export Excel (CSV)</button>
            <button type="button" class="export-button" @click="exportPdf"><Printer :size="16" /> Export PDF</button>
          </div>
        </div>
        <p class="mt-3 inline-flex items-start gap-2 rounded-lg bg-[#E0EAFD] px-3.5 py-2.5 text-[13px] leading-[18px] text-[#1B4DB1]">
          <LockKeyhole :size="16" class="mt-px shrink-0" />
          Totals only. Client records and session notes are never shown here.
        </p>
      </div>

      <!-- Date range -->
      <section class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-4 sm:p-5" aria-label="Reporting period">
        <div class="flex flex-wrap items-end gap-x-4 gap-y-4">
          <div class="w-full sm:w-48">
            <label for="range-from" class="text-sm font-medium">From</label>
            <input id="range-from" v-model="from" type="date" :max="to" class="field mt-1.5" :class="invalidRange ? 'field-error' : ''" :aria-invalid="invalidRange" />
          </div>
          <div class="w-full sm:w-48">
            <label for="range-to" class="text-sm font-medium">To</label>
            <input id="range-to" v-model="to" type="date" :min="from" class="field mt-1.5" :class="invalidRange ? 'field-error' : ''" :aria-invalid="invalidRange" />
          </div>
          <div class="flex flex-wrap gap-2 sm:ml-auto" role="group" aria-label="Quick ranges">
            <button
              v-for="p in presets"
              :key="p.label"
              type="button"
              class="inline-flex h-11 items-center rounded-[10px] border px-4 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
              :class="isActive(p) ? 'border-[#C8102E] bg-[#FCE8EB] text-[#A10E24]' : 'border-[#D5D8DE] bg-white hover:bg-[#F4F5F7]'"
              :aria-pressed="isActive(p)"
              @click="applyPreset(p)"
            >{{ p.label }}</button>
          </div>
        </div>
        <p v-if="invalidRange" class="mt-3 flex items-center gap-1.5 text-[13px] text-[#A10E24]" role="alert"><AlertCircle :size="15" />The start date must be on or before the end date.</p>
      </section>

      <ErrorMessage class="mt-4" :message="summary.error" />
      <PageLoader v-if="summary.loading && !data" />

      <template v-if="data">
        <div class="transition-opacity" :class="summary.loading ? 'opacity-60' : ''">
          <!-- Headline figures -->
          <section class="mt-5 grid grid-cols-2 gap-4 lg:grid-cols-4" aria-label="Headline figures">
            <div v-for="t in tiles" :key="t.label" class="flex items-center gap-3.5 rounded-xl border border-[#E4E6EA] bg-white p-4">
              <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px]" :class="t.tile"><component :is="t.icon" :size="20" /></span>
              <div class="min-w-0">
                <p class="text-[13px] leading-[18px] text-[#5B616B]">{{ t.label }}</p>
                <p class="text-[28px] font-semibold leading-[34px] tabular-nums">{{ t.value }}</p>
              </div>
            </div>
          </section>

          <div class="mt-5 grid items-start gap-5 lg:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)]">
            <div class="min-w-0 space-y-5">
              <!-- Sessions by mode -->
              <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
                <div class="flex items-center justify-between gap-3 border-b border-[#E4E6EA] px-5 py-4">
                  <div>
                    <h2 class="text-lg font-semibold leading-6">Sessions completed</h2>
                    <p class="mt-0.5 text-[13px] text-[#5B616B]">By mode of contact</p>
                  </div>
                  <p class="text-right"><span class="block text-xl font-semibold leading-6 tabular-nums">{{ totalSessions }}</span><span class="text-[13px] text-[#5B616B]">in total</span></p>
                </div>
                <ul v-if="modes.length" class="space-y-5 p-5">
                  <li v-for="[mode, n] in modes" :key="mode">
                    <div class="flex items-baseline justify-between gap-3 text-sm">
                      <span class="font-medium">{{ mode }}</span>
                      <span class="tabular-nums"><span class="font-semibold">{{ n }}</span><span class="ml-2 text-[13px] text-[#5B616B]">{{ share(n) }}</span></span>
                    </div>
                    <div class="mt-2 h-2.5 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="h-full rounded-full bg-[#C8102E] transition-[width] duration-500" :style="{ width: bar(n) }"></div></div>
                  </li>
                </ul>
                <p v-else class="px-5 py-10 text-center text-sm text-[#5B616B]">No sessions completed in this period.</p>
              </section>

              <!-- By counsellor -->
              <section v-if="data.by_counsellor" class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
                <div class="border-b border-[#E4E6EA] px-5 py-4">
                  <h2 class="text-lg font-semibold leading-6">By counsellor</h2>
                  <p class="mt-0.5 text-[13px] text-[#5B616B]">Caseload and session activity</p>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full text-left text-sm">
                    <thead>
                      <tr class="bg-[#F4F5F7] text-xs uppercase tracking-[0.04em] text-[#5B616B]">
                        <th class="whitespace-nowrap px-5 py-2.5 font-semibold">Counsellor</th>
                        <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Active caseload</th>
                        <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Completed</th>
                        <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Upcoming</th>
                        <th class="whitespace-nowrap px-5 py-2.5 font-semibold">Overdue</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="r in data.by_counsellor" :key="r.counsellor" class="border-t border-[#E4E6EA] transition hover:bg-[#F4F5F7]/60">
                        <td class="px-5 py-3.5">
                          <span class="flex items-center gap-3">
                            <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#2B2F36] text-xs font-semibold text-white">{{ initials(r.counsellor) }}</span>
                            <span class="whitespace-nowrap font-semibold">{{ r.counsellor }}</span>
                          </span>
                        </td>
                        <td class="px-3 py-3.5 tabular-nums">{{ r.active_caseload }}</td>
                        <td class="px-3 py-3.5 tabular-nums">{{ r.completed_in_range }}</td>
                        <td class="px-3 py-3.5 tabular-nums">{{ r.upcoming }}</td>
                        <td class="px-5 py-3.5">
                          <Badge v-if="r.overdue" :label="String(r.overdue)" theme="red" />
                          <span v-else class="tabular-nums text-[#5B616B]">0</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>
            </div>

            <div class="space-y-5">
              <!-- Appointments by status -->
              <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
                <div class="border-b border-[#E4E6EA] px-5 py-4">
                  <h2 class="text-lg font-semibold leading-6">Appointments</h2>
                  <p class="mt-0.5 text-[13px] text-[#5B616B]">In this period, by status</p>
                </div>
                <ul v-if="statusRows.length" class="divide-y divide-[#E4E6EA]">
                  <li v-for="[s, n] in statusRows" :key="s" class="flex items-center justify-between gap-3 px-5 py-3.5">
                    <Badge :label="s" :theme="statusTheme(s)" />
                    <span class="text-[15px] font-semibold tabular-nums">{{ n }}</span>
                  </li>
                </ul>
                <p v-else class="px-5 py-10 text-center text-sm text-[#5B616B]">None in this period.</p>
              </section>

              <!-- Baseline surveys -->
              <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
                <div class="border-b border-[#E4E6EA] px-5 py-4">
                  <h2 class="text-lg font-semibold leading-6">Baseline surveys</h2>
                  <p class="mt-0.5 text-[13px] text-[#5B616B]">Aggregate completion and declination only</p>
                </div>
                <ul v-if="baselineRows.length" class="divide-y divide-[#E4E6EA]">
                  <li v-for="[s, n] in baselineRows" :key="s" class="flex items-center justify-between gap-3 px-5 py-3.5">
                    <span class="text-sm font-medium">{{ s }}</span>
                    <span class="text-[15px] font-semibold tabular-nums">{{ n }}</span>
                  </li>
                </ul>
                <p v-else class="px-5 py-10 text-center text-sm text-[#5B616B]">None yet.</p>
              </section>
            </div>
          </div>

          <div class="mt-5 grid gap-5 lg:grid-cols-2">
            <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
              <div class="border-b border-[#E4E6EA] px-5 py-4"><h2 class="text-lg font-semibold leading-6">Referral analytics</h2><p class="mt-0.5 text-[13px] text-[#5B616B]">Recorded referrals by type in this period</p></div>
              <ul v-if="referralRows.length" class="divide-y divide-[#E4E6EA]">
                <li v-for="[type, count] in referralRows" :key="type" class="flex items-center justify-between gap-3 px-5 py-3.5"><span class="text-sm font-medium">{{ type }}</span><span class="text-[15px] font-semibold tabular-nums">{{ count }}</span></li>
              </ul>
              <p v-else class="px-5 py-8 text-center text-sm text-[#5B616B]">No referrals recorded in this period.</p>
            </section>
            <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
              <div class="border-b border-[#E4E6EA] px-5 py-4"><h2 class="text-lg font-semibold leading-6">Appointment trends</h2><p class="mt-0.5 text-[13px] text-[#5B616B]">Appointments by date, all statuses</p></div>
              <div v-if="trendRows.length" class="space-y-3 p-5">
                <div v-for="row in trendRows" :key="row.date" class="grid grid-cols-[84px_1fr_34px] items-center gap-3 text-sm"><span class="text-xs tabular-nums text-[#5B616B]">{{ formatDay(row.date) }}</span><div class="h-2.5 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="h-full rounded-full bg-[#C8102E]" :style="{ width: trendBar(row.total) }"></div></div><span class="text-right font-semibold tabular-nums">{{ row.total }}</span></div>
              </div>
              <p v-else class="px-5 py-8 text-center text-sm text-[#5B616B]">No appointments in this period.</p>
            </section>
          </div>
        </div>
      </template>

      <!-- Shared programme appointment calendar -->
      <section v-if="showCalendar && calendar.data" class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
        <div class="flex items-center justify-between gap-3 border-b border-[#E4E6EA] px-5 py-4">
          <div>
            <h2 class="text-lg font-semibold leading-6">{{ data?.scope === "WoC" ? "WoC appointment calendar" : "KRCTI counsellor calendar" }}</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">{{ filteredCalendar.length }} appointment{{ filteredCalendar.length === 1 ? "" : "s" }} in this period</p>
          </div>
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><CalendarDays :size="19" /></span>
        </div>
        <div class="flex flex-wrap items-end gap-3 border-b border-[#E4E6EA] px-5 py-4">
          <label for="calendar-counsellor" class="w-full max-w-sm text-sm font-medium text-[#3A3F47]">View appointments for counsellor
            <select id="calendar-counsellor" v-model="selectedCounsellor" class="field mt-1.5">
              <option value="">Select a counsellor</option>
              <option value="__all__">All counsellors</option>
              <option v-for="counsellor in counsellorOptions" :key="counsellor" :value="counsellor">{{ counsellor }}</option>
            </select>
          </label>
        </div>
        <div v-if="filteredCalendar.length" class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="bg-[#F4F5F7] text-xs uppercase tracking-[0.04em] text-[#5B616B]">
                <th class="whitespace-nowrap px-5 py-2.5 font-semibold">When</th>
                <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Counsellor</th>
                <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Session</th>
                <th class="whitespace-nowrap px-3 py-2.5 font-semibold">Mode</th>
                <th class="whitespace-nowrap px-5 py-2.5 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody v-for="group in calendarGroups" :key="group.scholar_code">
              <tr class="border-t border-[#D5D8DE] bg-[#F4F5F7]">
                <th colspan="5" class="px-5 py-3 text-left text-sm font-semibold text-[#2B2F36]">Scholar/Participant Code: <span class="text-[#A10E24]">{{ group.scholar_code }}</span></th>
              </tr>
              <tr v-for="(r, i) in group.appointments" :key="`${group.scholar_code}-${i}`" class="border-t border-[#E4E6EA] transition hover:bg-[#F4F5F7]/60">
                <td class="whitespace-nowrap px-5 py-3.5 font-medium tabular-nums">{{ fmtDateTime(r.start) }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.counsellor }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.session_type }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.mode }}</td>
                <td class="px-5 py-3.5"><Badge :label="r.overdue ? 'Overdue' : r.status" :theme="r.overdue ? 'red' : statusTheme(r.status)" /></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="px-5 py-8 text-center text-sm text-[#5B616B]">{{ selectedCounsellor ? "No appointments for this counsellor in the selected period." : "Select a counsellor to view appointments, or choose All counsellors." }}</p>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref, watch } from "vue"
import { AlertCircle, Archive, CalendarDays, ClipboardCheck, Clock, Download, LockKeyhole, Printer, Users } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"
import { me } from "../data/me"

const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const daysAgo = (n) => iso(new Date(Date.now() - n * 86400000))
const to = ref(iso(new Date()))
const from = ref(daysAgo(30))

const summary = createResource({ url: "krcti_mhpss.api.oversight.programme_summary" })
const calendar = createResource({ url: "krcti_mhpss.api.oversight.programme_calendar" })
const selectedCounsellor = ref("")
const data = computed(() => summary.data)
const showCalendar = computed(() => ["krcti_pm", "woc_pm", "admin"].includes(me.data?.role))
const invalidRange = computed(() => !!from.value && !!to.value && from.value > to.value)

function load() {
	if (from.value > to.value) return
	summary.submit({ date_from: from.value, date_to: to.value })
	if (showCalendar.value) calendar.submit({ date_from: from.value, date_to: to.value })
}
onMounted(() => me.data ? load() : me.reload())
watch(() => me.data, load)
watch([from, to], load)

// Quick ranges
const startOfMonth = () => { const d = new Date(); return iso(new Date(d.getFullYear(), d.getMonth(), 1)) }
const presets = [
	{ label: "Last 7 days", from: () => daysAgo(7) },
	{ label: "Last 30 days", from: () => daysAgo(30) },
	{ label: "Last 90 days", from: () => daysAgo(90) },
	{ label: "This month", from: startOfMonth },
]
const applyPreset = (p) => { to.value = iso(new Date()); from.value = p.from() }
const isActive = (p) => to.value === iso(new Date()) && from.value === p.from()

// Figures
const sum = (o) => Object.values(o || {}).reduce((a, b) => a + b, 0)
const totalSessions = computed(() => sum(data.value?.sessions_by_mode))
const modes = computed(() => Object.entries(data.value?.sessions_by_mode || {}).sort((a, b) => b[1] - a[1]))
const mostSessions = computed(() => Math.max(1, ...modes.value.map(([, n]) => n)))
const bar = (n) => `${Math.round((n / mostSessions.value) * 100)}%`
const share = (n) => (totalSessions.value ? `${Math.round((n / totalSessions.value) * 100)}%` : "0%")
const statusRows = computed(() => Object.entries(data.value?.appointments_by_status || {}))
const baselineRows = computed(() => ["Completed", "Declined", "Pending"].map((s) => [s, data.value?.baseline?.[s] || 0]))
const referralRows = computed(() => Object.entries(data.value?.referrals || {}))
const trendRows = computed(() => data.value?.appointment_trends || [])
const counsellorOptions = computed(() => [...new Set((calendar.data || []).map((appointment) => appointment.counsellor).filter(Boolean))].sort((a, b) => a.localeCompare(b)))
watch(counsellorOptions, (options) => {
	if (selectedCounsellor.value && selectedCounsellor.value !== "__all__" && !options.includes(selectedCounsellor.value)) selectedCounsellor.value = ""
})
const filteredCalendar = computed(() => {
	if (!selectedCounsellor.value) return []
	if (selectedCounsellor.value === "__all__") return calendar.data || []
	return (calendar.data || []).filter((appointment) => appointment.counsellor === selectedCounsellor.value)
})
const calendarGroups = computed(() => {
	const groups = new Map()
	for (const appointment of filteredCalendar.value) {
		const scholar_code = appointment.scholar_code || "Code unavailable"
		if (!groups.has(scholar_code)) groups.set(scholar_code, [])
		groups.get(scholar_code).push(appointment)
	}
	return [...groups.entries()]
		.sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
		.map(([scholar_code, appointments]) => ({ scholar_code, appointments }))
})
const maxTrend = computed(() => Math.max(1, ...trendRows.value.map((r) => r.total)))
const trendBar = (n) => `${Math.round((n / maxTrend.value) * 100)}%`
const formatDay = (day) => new Date(`${day}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })

const statusTheme = (s) => ({ Completed: "green", Cancelled: "gray", Scheduled: "blue", Overdue: "red" })[s] || "gray"
const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()

const tiles = computed(() => {
	const c = data.value?.caseload || {}
	return [
		{ label: "Active clients", value: c.Active ?? 0, icon: Users, tile: "bg-[#FCE8EB] text-[#A10E24]" },
		{ label: "Pending follow-ups", value: data.value?.pending_followups ?? c["Follow-Up Pending"] ?? 0, icon: Clock, tile: "bg-[#FDECC8] text-[#8A4B00]" },
		{ label: "Closed cases", value: c.Closed ?? 0, icon: Archive, tile: "bg-[#E4E6EA] text-[#3A3F47]" },
		{ label: "Sessions completed", value: totalSessions.value, icon: ClipboardCheck, tile: "bg-[#DCF3E4] text-[#146C3A]" },
	]
})

function exportCsv() {
	const rows = [
		[`${data.value?.scope || "Programme"} aggregate report`, `${from.value} to ${to.value}`],
		["Overview", "Count"],
		...tiles.value.map((tile) => [tile.label, tile.value]),
		["Sessions by contact mode", "Count"], ...modes.value,
		["Appointments by status", "Count"], ...statusRows.value,
		["Appointment date", "Count"], ...trendRows.value.map((r) => [r.date, r.total]),
		["Referral type", "Count"], ...referralRows.value,
		["Baseline survey status", "Count"], ...baselineRows.value,
	]
	if (data.value?.by_counsellor) rows.push(["Counsellor", "Active caseload", "Completed sessions", "Upcoming", "Overdue"], ...data.value.by_counsellor.map((r) => [r.counsellor, r.active_caseload, r.completed_in_range, r.upcoming, r.overdue]))
	const csv = rows.map((row) => row.map((cell) => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(",")).join("\r\n")
	const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" }))
	const link = document.createElement("a")
	link.href = url
	link.download = `${data.value?.scope === "WoC" ? "woc" : "krcti"}-programme-report-${from.value}-to-${to.value}.csv`
	link.click()
	setTimeout(() => URL.revokeObjectURL(url), 1000)
}
function exportPdf() { window.print() }
</script>

<style scoped>
.field {
	display: block;
	height: 44px;
	width: 100%;
	border-radius: 8px;
	border: 1px solid #d5d8de;
	background: #fff;
	padding: 0 12px;
	font: 14px Inter, system-ui, sans-serif;
	color: #2b2f36;
}
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.25); }
.field-error { border-color: #a10e24; }
.export-button { display: inline-flex; height: 40px; align-items: center; gap: 8px; border: 1px solid #d5d8de; border-radius: 9px; background: white; padding: 0 12px; color: #383c44; font-size: 13px; font-weight: 600; }
.export-button:hover { background: #f4f5f7; }
@media print {
	.no-print, .field, button { display: none !important; }
	main { min-height: 0 !important; background: white !important; padding: 0 !important; }
	main > div { max-width: none !important; }
	section, .rounded-xl { break-inside: avoid; box-shadow: none !important; }
}
</style>
