<template>
  <main class="min-h-[calc(100vh-72px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">

      <!-- ============ Header (same placement as the counsellor dashboard) ============ -->
      <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p class="text-sm font-medium text-[#737780]">{{ todayLabel }}</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">
            {{ data?.scope === "WoC" ? "WoC Programme Dashboard" : "KRCTI PM Dashboard" }}
          </h1>
          <p class="mt-1 flex items-center gap- text-sm text-[#737780]">
            <span class="mt-1">{{ data?.scope === "WoC" ? "WoC Scholarship Fund aggregate service monitoring" : "Service delivery across KRCTI counsellors" }}</span>
          </p>
<p v-if="syncedAt" class="mt-2  text-sm text-[#858891]">Last Update {{ syncedAt }}</p>
        </div>
        <div class="no-print flex flex-wrap gap-2">
          <button type="button" class="inline-flex items-center gap-2 rounded-lg border border-[#D9DBE0] bg-white px-4 py-2.5 text-sm font-semibold text-[#34363B] shadow-sm transition hover:border-[#BFC2C8] hover:bg-[#FAFAFB]" @click="exportCsv">
            <Download :size="17" /> Export Excel (CSV)
          </button>
          <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#A10E24]" @click="exportPdf">
            <Printer :size="17" /> Export PDF
          </button>
        </div>
      </div>

      <ErrorMessage class="mt-4" :message="summary.error" />
      <PageLoader v-if="summary.loading && !data" />

      <template v-if="data">
        <!-- ============ Headline figures (same card style as the counsellor dashboard) ============ -->
        <div class="mt-6 grid grid-cols-1 gap-3 transition-opacity sm:grid-cols-2 xl:grid-cols-4" :class="summary.loading ? 'opacity-60' : ''" aria-label="Headline figures">
          <router-link
            v-for="t in tiles"
            :key="t.label"
            :to="t.to"
            class="group rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(20,25,35,0.03)] transition hover:-translate-y-0.5 hover:border-[#D7A0AA] hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30"
          >
            <div class="flex items-start justify-between gap-3">
              <span class="text-sm font-medium text-[#737780]">{{ t.label }}</span>
              <span class="flex h-9 w-9 items-center justify-center rounded-lg" :class="t.tile"><component :is="t.icon" :size="18" /></span>
            </div>
            <p class="mt-4 text-[30px] font-semibold leading-none tracking-tight tabular-nums text-[#25272B]">{{ t.value }}</p>
            <p class="mt-2 flex items-center gap-1 text-xs text-[#858891]">
              {{ t.hint }}
              <ArrowUpRight :size="13" class="transition group-hover:-translate-y-px group-hover:translate-x-px group-hover:text-[#C8102E]" />
            </p>
          </router-link>
        </div>

        <div class="mt-5 transition-opacity" :class="summary.loading ? 'opacity-60' : ''">

          <!-- ============ Two-column layout ============ -->
          <div class="grid items-start gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.9fr)]">

            <!-- ===== Left column: By counsellor, modes + referrals, baseline surveys ===== -->
            <div class="min-w-0 space-y-5">

              <!-- By counsellor -->
              <section
                v-if="data.by_counsellor"
                id="counsellor-performance"
                ref="counsellorSection"
                class="card overflow-hidden transition-shadow"
                :class="focusCounsellors ? '!border-[#C8102E] ring-2 ring-[#C8102E]/20 shadow-md' : ''"
              >
                <div class="card-head">
                  <div>
                    <h2 class="card-title">By counsellor</h2>
                    <p class="card-sub">Caseload and session activity</p>
                  </div>
                  <router-link :to="{ name: 'ProgrammeSessions' }" class="no-print text-sm font-semibold text-[#B30F2A] hover:underline">View all sessions</router-link>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full min-w-[640px] text-left text-sm">
                    <thead>
                      <tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]">
                        <th class="whitespace-nowrap px-5 py-3">Counsellor</th>
                        <th class="whitespace-nowrap px-3 py-3">Active caseload</th>
                        <th class="whitespace-nowrap px-3 py-3">Delivery</th>
                        <th class="whitespace-nowrap px-3 py-3">Completed</th>
                        <th class="whitespace-nowrap px-3 py-3">Upcoming</th>
                        <th class="whitespace-nowrap px-5 py-3">Overdue</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#F0F1F3]">
                      <tr v-for="r in data.by_counsellor" :key="r.counsellor" class="transition hover:bg-[#FCFCFD]">
                        <td class="px-5 py-3.5">
                          <router-link
                            :to="{ name: 'ProgrammeSessions', query: { counsellor: r.counsellor_id } }"
                            class="flex w-fit items-center gap-3 rounded-md hover:text-[#B30F2A] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30"
                          >
                            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-semibold text-[#B30F2A]">{{ initials(r.counsellor) }}</span>
                            <span class="whitespace-nowrap font-medium text-[#33353A] hover:underline">{{ r.counsellor }}</span>
                          </router-link>
                        </td>
                        <td class="px-3 py-3.5 tabular-nums text-[#555860]">{{ r.active_caseload }}</td>
                        <td class="px-3 py-3.5">
                          <div class="flex items-center gap-2.5">
                            <div class="h-2 w-24 overflow-hidden rounded-full bg-[#EEF0F3]">
                              <div class="h-full rounded-full transition-[width] duration-500" :class="deliveryColor(r)" :style="{ width: `${delivery(r)}%` }"></div>
                            </div>
                            <span class="w-9 text-[13px] font-semibold tabular-nums text-[#3A3F47]">{{ delivery(r) }}%</span>
                          </div>
                        </td>
                        <td class="px-3 py-3.5 tabular-nums text-[#555860]">{{ r.completed_in_range }}</td>
                        <td class="px-3 py-3.5 tabular-nums text-[#555860]">{{ r.upcoming }}</td>
                        <td class="px-5 py-3.5">
                          <Badge v-if="r.overdue" :label="String(r.overdue)" theme="red" />
                          <span v-else class="tabular-nums text-[#858891]">0</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="border-t border-[#ECEDEF] px-5 py-3 text-xs text-[#858891]">Delivery = completed ÷ (completed + upcoming + overdue) in this period.</p>
              </section>

              <!-- Sessions completed + Referral analytics (equal fixed height) -->
              <div class="grid min-w-0 gap-5 md:grid-cols-2">

                <!-- Sessions by mode -->
                <section class="card flex h-[360px] flex-col overflow-hidden">
                  <div class="card-head shrink-0">
                    <div>
                      <h2 class="card-title">Sessions completed</h2>
                      <p class="card-sub">By mode of contact</p>
                    </div>
                    <span class="score-pill">{{ totalSessions }} total</span>
                  </div>
                  <ul v-if="modes.length" class="min-h-0 flex-1 space-y-5 overflow-y-auto p-5">
                    <li v-for="[mode, n] in modes" :key="mode">
                      <div class="flex items-baseline justify-between gap-3 text-sm">
                        <span class="font-medium text-[#33353A]">{{ mode }}</span>
                        <span class="tabular-nums"><span class="font-semibold">{{ n }}</span><span class="ml-2 text-[13px] text-[#858891]">{{ share(n) }}</span></span>
                      </div>
                      <div class="mt-2 h-2 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="h-full rounded-full bg-[#C8102E] transition-[width] duration-500" :style="{ width: bar(n) }"></div></div>
                    </li>
                  </ul>
                  <div v-else class="flex flex-1 flex-col items-center justify-center px-5 text-center">
                    <ClipboardCheck class="mx-auto text-[#B9BBC1]" :size="25" />
                    <p class="mt-3 text-sm font-medium text-[#555860]">No sessions completed in this period</p>
                  </div>
                </section>

                <!-- Referral analytics (scrolls inside itself when types exceed the card) -->
                <section class="card flex h-[360px] flex-col overflow-hidden">
                  <div class="card-head shrink-0">
                    <div>
                      <h2 class="card-title">Referral analytics</h2>
                      <p class="card-sub">Recorded referrals by type</p>
                    </div>
                    <span class="score-pill">{{ referralTotal }} total</span>
                  </div>
                  <ul v-if="referralRows.length" class="min-h-0 flex-1 divide-y divide-[#F0F1F3] overflow-y-auto">
                    <li v-for="[type, count] in referralRows" :key="type" class="flex items-center gap-3 px-5 py-3.5">
                      <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-[#B30F2A]"><Share2 :size="16" /></span>
                      <div class="min-w-0 flex-1">
                        <p class="truncate text-sm font-medium text-[#33353A]">{{ type }}</p>
                        <p class="text-xs text-[#858891]">{{ referralShare(count) }} of referrals</p>
                      </div>
                      <span class="text-[17px] font-semibold tabular-nums text-[#A10E24]">{{ count }}</span>
                    </li>
                  </ul>
                  <div v-else class="flex flex-1 flex-col items-center justify-center px-5 text-center">
                    <Share2 class="mx-auto text-[#B9BBC1]" :size="25" />
                    <p class="mt-3 text-sm font-medium text-[#555860]">No referrals recorded in this period</p>
                  </div>
                </section>
              </div>

              <!-- Baseline surveys -->
              <section class="card overflow-hidden">
                <div class="card-head">
                  <div>
                    <h2 class="card-title">Baseline surveys</h2>
                    <p class="card-sub">Aggregate completion and declination only</p>
                  </div>
                </div>
                <div class="grid grid-cols-3 gap-3 p-5">
                  <div v-for="[s, n] in baselineRows" :key="s" class="rounded-xl border border-[#ECEDEF] bg-[#FAFAFB] p-3.5">
                    <p class="text-xs font-medium text-[#737780]">{{ s }}</p>
                    <p class="mt-1 text-2xl font-semibold tabular-nums" :class="baselineTone(s)">{{ n }}</p>
                  </div>
                </div>
              </section>
            </div>

            <!-- ===== Right column: Appointment trends + Appointments by status ===== -->
            <div class="min-w-0 space-y-5">

              <!-- Appointment trends -->
              <section class="card overflow-hidden">
                <div class="card-head">
                  <div>
                    <h2 class="card-title">Appointment trends</h2>
                    <p class="card-sub">Appointments by date, all statuses</p>
                  </div>
                  <p class="text-right"><span class="block text-xl font-semibold leading-6 tabular-nums">{{ trendTotal }}</span><span class="text-xs text-[#858891]">in total</span></p>
                </div>
                <div v-if="trendRows.length" class="p-5">
                  <div class="h-[270px]"><Bar :data="trendChart" :options="trendOptions" /></div>
                </div>
                <div v-else class="px-5 py-12 text-center">
                  <CalendarDays class="mx-auto text-[#B9BBC1]" :size="25" />
                  <p class="mt-3 text-sm font-medium text-[#555860]">No appointments in this period</p>
                </div>
              </section>

              <!-- Appointments by status -->
              <section class="card overflow-hidden">
                <div class="card-head">
                  <div>
                    <h2 class="card-title">Appointments</h2>
                    <p class="card-sub">In this period, by status</p>
                  </div>
                </div>
                <template v-if="statusRows.length">
                  <div class="flex items-center justify-center p-5 pb-2">
                    <div class="h-[190px] w-[190px]"><Doughnut :data="statusChart" :options="doughnutOptions" :plugins="[centerText]" /></div>
                  </div>
                  <ul class="space-y-2.5 p-5 pt-3">
                    <li v-for="[s, n] in statusRows" :key="s" class="flex items-center gap-3">
                      <span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ background: statusColor(s) }"></span>
                      <span class="w-24 shrink-0 text-sm font-medium text-[#33353A]">{{ s }}</span>
                      <div class="h-2 flex-1 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="h-full rounded-full transition-[width] duration-500" :style="{ width: statusBar(n), background: statusColor(s) }"></div></div>
                      <span class="w-8 text-right text-sm font-semibold tabular-nums">{{ n }}</span>
                    </li>
                  </ul>
                </template>
                <div v-else class="px-5 py-12 text-center">
                  <CalendarDays class="mx-auto text-[#B9BBC1]" :size="25" />
                  <p class="mt-3 text-sm font-medium text-[#555860]">None in this period</p>
                </div>
              </section>
            </div>
          </div>
        </div>
      </template>

      <!-- ============ Shared programme appointment calendar ============ -->
      <section v-if="showCalendar && calendar.data" class="card mt-5 overflow-hidden">
        <div class="card-head">
          <div>
            <h2 class="card-title">{{ data?.scope === "WoC" ? "WoC appointment calendar" : "KRCTI counsellor calendar" }}</h2>
            <p class="card-sub">{{ filteredCalendar.length }} appointment{{ filteredCalendar.length === 1 ? "" : "s" }} in this period</p>
          </div>
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#B30F2A]"><CalendarDays :size="18" /></span>
        </div>
        <div class="no-print flex flex-wrap items-end gap-3 border-b border-[#ECEDEF] px-5 py-4">
          <label for="calendar-counsellor" class="w-full max-w-sm text-sm font-medium text-[#3A3F47]">View appointments for counsellor
            <select id="calendar-counsellor" v-model="selectedCounsellor" class="field mt-1.5">
              <option value="">Select a counsellor</option>
              <option value="__all__">All counsellors</option>
              <option v-for="counsellor in counsellorOptions" :key="counsellor.name" :value="counsellor.name">{{ counsellor.full_name }}</option>
            </select>
          </label>
        </div>
        <div v-if="filteredCalendar.length" class="overflow-x-auto">
          <table class="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]">
                <th class="whitespace-nowrap px-5 py-3">When</th>
                <th class="whitespace-nowrap px-3 py-3">Counsellor</th>
                <th class="whitespace-nowrap px-3 py-3">Session</th>
                <th class="whitespace-nowrap px-3 py-3">Mode</th>
                <th class="whitespace-nowrap px-3 py-3">Status</th>
                <th class="whitespace-nowrap px-5 py-3">Client record</th>
              </tr>
            </thead>
            <tbody v-for="group in calendarGroups" :key="group.scholar_code">
              <tr class="border-t border-[#ECEDEF] bg-[#FAFAFB]">
                <th colspan="6" class="px-5 py-2.5 text-left text-[13px] font-semibold text-[#2B2F36]">
                  Scholar/Participant Code
                  <span class="ml-1.5 rounded-md bg-[#FCE8EB] px-2 py-0.5 text-[#A10E24]">{{ group.scholar_code }}</span>
                </th>
              </tr>
              <tr v-for="(r, i) in group.appointments" :key="`${group.scholar_code}-${i}`" class="border-t border-[#F0F1F3] transition hover:bg-[#FCFCFD]">
                <td class="whitespace-nowrap px-5 py-3.5 font-medium tabular-nums text-[#33353A]">{{ fmtDateTime(r.start) }}</td>
                <td class="whitespace-nowrap px-3 py-3.5 text-[#555860]">{{ r.counsellor }}</td>
                <td class="whitespace-nowrap px-3 py-3.5 text-[#555860]">{{ r.session_type }}</td>
                <td class="whitespace-nowrap px-3 py-3.5 text-[#555860]">{{ r.mode }}</td>
                <td class="px-3 py-3.5"><Badge :label="r.overdue ? 'Overdue' : r.status" :theme="r.overdue ? 'red' : statusTheme(r.status)" /></td>
                <td class="px-5 py-3.5"><router-link :to="{ name: 'ProgrammeClientDetail', params: { name: r.client_id } }" class="font-semibold text-[#B30F2A] hover:underline">View record</router-link></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="px-5 py-12 text-center">
          <CalendarDays class="mx-auto text-[#B9BBC1]" :size="25" />
          <p class="mt-3 text-sm font-medium text-[#555860]">{{ selectedCounsellor ? "No appointments for this counsellor in the selected period." : "Select a counsellor to view appointments, or choose All counsellors." }}</p>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, nextTick, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { Archive, ArrowUpRight, CalendarDays, ClipboardCheck, Clock, Download, LockKeyhole, Printer, Share2, Users } from "lucide-vue-next"
import { Chart as ChartJS, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip } from "chart.js"
import { Bar, Doughnut } from "vue-chartjs"
import { fmtDateTime } from "../data/format"
import { me } from "../data/me"

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip)
ChartJS.defaults.font.family = "Inter, system-ui, sans-serif"
ChartJS.defaults.color = "#8A909A"

// Fixed reporting window (no user-facing date controls)
const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const daysAgo = (n) => iso(new Date(Date.now() - n * 86400000))
const to = iso(new Date())
const from = daysAgo(30)
const todayLabel = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" })

const route = useRoute()
const summary = createResource({ url: "krcti_mhpss.api.oversight.programme_summary" })
const calendar = createResource({ url: "krcti_mhpss.api.oversight.programme_calendar" })
const counsellors = createResource({ url: "krcti_mhpss.api.oversight.programme_counsellors" })
const selectedCounsellor = ref("")
const focusCounsellors = ref(false)
const counsellorSection = ref(null)
const syncedAt = ref("")
const data = computed(() => summary.data)
const showCalendar = computed(() => ["krcti_pm", "woc_pm", "admin"].includes(me.data?.role))

let focusTimer
function highlightCounsellors() {
	focusCounsellors.value = true
	nextTick(() => counsellorSection.value?.scrollIntoView({ behavior: "smooth", block: "center" }))
	clearTimeout(focusTimer)
	focusTimer = setTimeout(() => (focusCounsellors.value = false), 3000)
}

function load() {
	summary.submit({ date_from: from, date_to: to })
	if (showCalendar.value) {
		calendar.submit({ date_from: from, date_to: to })
		if (!counsellors.data) counsellors.submit()
	}
}
onMounted(() => (me.data ? load() : me.reload()))
watch(() => me.data, load)
watch([() => route.query.focus, data], ([focus, currentData]) => {
	if (focus === "counsellors" && currentData?.by_counsellor) highlightCounsellors()
}, { immediate: true })
watch(() => summary.data, (v) => {
	if (v) syncedAt.value = new Date().toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })
})

// Figures
const sum = (o) => Object.values(o || {}).reduce((a, b) => a + b, 0)
const totalSessions = computed(() => data.value?.completed_sessions ?? sum(data.value?.sessions_by_mode))
const modes = computed(() => Object.entries(data.value?.sessions_by_mode || {}).sort((a, b) => b[1] - a[1]))
const mostSessions = computed(() => Math.max(1, ...modes.value.map(([, n]) => n)))
const bar = (n) => `${Math.round((n / mostSessions.value) * 100)}%`
const share = (n) => (totalSessions.value ? `${Math.round((n / totalSessions.value) * 100)}%` : "0%")
const statusRows = computed(() => Object.entries(data.value?.appointments_by_status || {}))
const statusTotal = computed(() => statusRows.value.reduce((a, [, n]) => a + n, 0))
const statusBar = (n) => `${statusTotal.value ? Math.round((n / statusTotal.value) * 100) : 0}%`
const baselineRows = computed(() => ["Completed", "Declined", "Pending"].map((s) => [s, data.value?.baseline?.[s] || 0]))
const baselineTone = (s) => ({ Completed: "text-[#146C3A]", Declined: "text-[#A10E24]", Pending: "text-[#8A4B00]" })[s] || ""
const referralRows = computed(() => Object.entries(data.value?.referrals || {}))
const referralTotal = computed(() => referralRows.value.reduce((a, [, n]) => a + n, 0))
const referralShare = (n) => (referralTotal.value ? `${Math.round((n / referralTotal.value) * 100)}%` : "0%")
const trendRows = computed(() => data.value?.appointment_trends || [])
const trendTotal = computed(() => trendRows.value.reduce((a, r) => a + r.total, 0))
const counsellorOptions = computed(() => [...(counsellors.data || [])].sort((a, b) => a.full_name.localeCompare(b.full_name)))
watch(counsellorOptions, (options) => {
	if (selectedCounsellor.value && selectedCounsellor.value !== "__all__" && !options.some((person) => person.name === selectedCounsellor.value)) selectedCounsellor.value = ""
})
const filteredCalendar = computed(() => {
	if (!selectedCounsellor.value) return []
	if (selectedCounsellor.value === "__all__") return calendar.data || []
	return (calendar.data || []).filter((appointment) => appointment.counsellor_id === selectedCounsellor.value)
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
const formatDay = (day) => new Date(`${day}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })

const statusTheme = (s) => ({ Completed: "green", Cancelled: "gray", Scheduled: "blue", Overdue: "red" })[s] || "gray"
const STATUS_COLORS = { Completed: "#1F9D55", Cancelled: "#B4B9C2", Scheduled: "#2F6FED", Overdue: "#C8102E" }
const statusColor = (s) => STATUS_COLORS[s] || "#8A909A"
const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()

// Counsellor delivery rate
const delivery = (r) => {
	const total = (r.completed_in_range || 0) + (r.upcoming || 0) + (r.overdue || 0)
	return total ? Math.round(((r.completed_in_range || 0) / total) * 100) : 0
}
const deliveryColor = (r) => (r.overdue && delivery(r) < 50 ? "bg-[#C8102E]" : delivery(r) >= 70 ? "bg-[#1F9D55]" : "bg-[#E8A317]")

const tiles = computed(() => {
	const c = data.value?.caseload || {}
	return [
		{ label: "Active clients", value: (c.Active ?? 0) + (c["Follow-Up Pending"] ?? 0), hint: "View active clients", icon: Users, tile: "bg-[#FCE8EB] text-[#B30F2A]", to: { name: "ProgrammeClients", query: { status: "Active" } } },
		{ label: "Pending follow-ups", value: data.value?.pending_followups ?? c["Follow-Up Pending"] ?? 0, hint: "See counsellor workload", icon: Clock, tile: "bg-[#FFF4D9] text-[#A87814]", to: { name: "Programme", query: { focus: "counsellors" } } },
		{ label: "Closed cases", value: c.Closed ?? 0, hint: "View closed clients", icon: Archive, tile: "bg-[#E4E6EA] text-[#3A3F47]", to: { name: "ProgrammeClients", query: { status: "Closed" } } },
		{ label: "Sessions completed", value: totalSessions.value, hint: "View all sessions", icon: ClipboardCheck, tile: "bg-[#EAF5EE] text-[#26834B]", to: { name: "ProgrammeSessions" } },
	]
})

// ---- Charts ----
const trendChart = computed(() => {
	const max = Math.max(1, ...trendRows.value.map((r) => r.total))
	return {
		labels: trendRows.value.map((r) => formatDay(r.date)),
		datasets: [{
			data: trendRows.value.map((r) => r.total),
			backgroundColor: trendRows.value.map((r) => (r.total === max ? "#C8102E" : "#F3B8C1")),
			hoverBackgroundColor: "#A10E24",
			borderRadius: 8,
			borderSkipped: false,
			maxBarThickness: 36,
		}],
	}
})
const trendOptions = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: { display: false },
		tooltip: { backgroundColor: "#2B2F36", padding: 10, cornerRadius: 8, displayColors: false, callbacks: { label: (c) => `${c.parsed.y} appointment${c.parsed.y === 1 ? "" : "s"}` } },
	},
	scales: {
		x: { grid: { display: false }, border: { display: false }, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 8, font: { size: 11 } } },
		y: { beginAtZero: true, border: { display: false }, grid: { color: "#EEF0F3" }, ticks: { precision: 0, font: { size: 11 } } },
	},
}

const statusChart = computed(() => ({
	labels: statusRows.value.map(([s]) => s),
	datasets: [{
		data: statusRows.value.map(([, n]) => n),
		backgroundColor: statusRows.value.map(([s]) => statusColor(s)),
		borderColor: "#fff",
		borderWidth: 3,
		hoverOffset: 4,
	}],
}))
const doughnutOptions = {
	responsive: true,
	maintainAspectRatio: false,
	cutout: "72%",
	plugins: { legend: { display: false }, tooltip: { backgroundColor: "#2B2F36", padding: 10, cornerRadius: 8 } },
}
const centerText = {
	id: "centerText",
	afterDraw(chart) {
		const { ctx, chartArea: { left, right, top, bottom } } = chart
		const x = (left + right) / 2
		const y = (top + bottom) / 2
		ctx.save()
		ctx.textAlign = "center"
		ctx.textBaseline = "middle"
		ctx.fillStyle = "#2B2F36"
		ctx.font = "600 30px Inter, system-ui, sans-serif"
		ctx.fillText(String(statusTotal.value), x, y - 8)
		ctx.fillStyle = "#8A909A"
		ctx.font = "12px Inter, system-ui, sans-serif"
		ctx.fillText("appointments", x, y + 16)
		ctx.restore()
	},
}

// ---- Exports ----
function exportCsv() {
	const rows = [
		[`${data.value?.scope || "Programme"} aggregate report`, `${from} to ${to}`],
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
	link.download = `${data.value?.scope === "WoC" ? "woc" : "krcti"}-programme-report-${from}-to-${to}.csv`
	link.click()
	setTimeout(() => URL.revokeObjectURL(url), 1000)
}
function exportPdf() { window.print() }
</script>

<style scoped>
/* ---------- Surfaces (match the counsellor dashboard cards) ---------- */
.card {
	border-radius: 12px;
	border: 1px solid #e4e6ea;
	background: #fff;
	box-shadow: 0 1px 2px rgba(20, 25, 35, 0.03);
}
.card-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 16px 20px;
	border-bottom: 1px solid #ecedef;
}
.card-title { font-size: 16px; font-weight: 600; line-height: 24px; color: #25272b; }
.card-sub { margin-top: 2px; font-size: 12px; color: #858891; }

/* ---------- Controls ---------- */
.field {
	display: block;
	height: 44px;
	width: 100%;
	border-radius: 10px;
	border: 1px solid #d5d8de;
	background: #fff;
	padding: 0 12px;
	font: 14px Inter, system-ui, sans-serif;
	color: #2b2f36;
}
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.25); }
.score-pill {
	border-radius: 8px;
	background: #fce8eb;
	padding: 5px 10px;
	font-size: 12.5px;
	font-weight: 600;
	color: #a10e24;
	font-variant-numeric: tabular-nums;
	white-space: nowrap;
}

/* ---------- Print ---------- */
@media print {
	.no-print, button, .field { display: none !important; }
	main { min-height: 0 !important; background: white !important; padding: 0 !important; }
	main > div { max-width: none !important; }
	.card { break-inside: avoid; box-shadow: none !important; }
}
</style>
