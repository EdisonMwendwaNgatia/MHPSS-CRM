<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1200px]">
      <!-- Page header -->
      <div>
        <h1 class="text-2xl font-semibold leading-8">Programme overview</h1>
        <p class="mt-0.5 text-sm text-[#5B616B]">{{ data?.scope === "WoC" ? "The WoC scholarship programme" : "All KRCTI counsellors" }}</p>
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
                  <p class="mt-0.5 text-[13px] text-[#5B616B]">Initial wellbeing assessments</p>
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

          <p class="mt-5 flex items-center gap-2 text-[13px] text-[#5B616B]"><Info :size="15" class="shrink-0" />Referral figures arrive with the session form in the next release.</p>
        </div>
      </template>

      <!-- Counsellor calendar (programme managers and admins) -->
      <section v-if="showCalendar && calendar.data?.length" class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
        <div class="flex items-center justify-between gap-3 border-b border-[#E4E6EA] px-5 py-4">
          <div>
            <h2 class="text-lg font-semibold leading-6">Counsellor calendar</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">{{ calendar.data.length }} session{{ calendar.data.length === 1 ? "" : "s" }} in this period</p>
          </div>
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><CalendarDays :size="19" /></span>
        </div>
        <div class="overflow-x-auto">
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
            <tbody>
              <tr v-for="(r, i) in calendar.data" :key="i" class="border-t border-[#E4E6EA] transition hover:bg-[#F4F5F7]/60">
                <td class="whitespace-nowrap px-5 py-3.5 font-medium tabular-nums">{{ fmtDateTime(r.start) }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.counsellor }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.session_type }}</td>
                <td class="whitespace-nowrap px-3 py-3.5">{{ r.mode }}</td>
                <td class="px-5 py-3.5"><Badge :label="r.overdue ? 'Overdue' : r.status" :theme="r.overdue ? 'red' : statusTheme(r.status)" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref, watch } from "vue"
import { AlertCircle, Archive, CalendarDays, ClipboardCheck, Clock, Info, LockKeyhole, Users } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"
import { me } from "../data/me"

const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const daysAgo = (n) => iso(new Date(Date.now() - n * 86400000))
const to = ref(iso(new Date()))
const from = ref(daysAgo(30))

const summary = createResource({ url: "krcti_mhpss.api.oversight.programme_summary" })
const calendar = createResource({ url: "krcti_mhpss.api.oversight.programme_calendar" })
const data = computed(() => summary.data)
const showCalendar = computed(() => ["krcti_pm", "admin"].includes(me.data?.role))
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
const baselineRows = computed(() => Object.entries(data.value?.baseline || {}))

const statusTheme = (s) => ({ Completed: "green", Cancelled: "gray", Scheduled: "blue", Overdue: "red" })[s] || "gray"
const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()

const tiles = computed(() => {
	const c = data.value?.caseload || {}
	return [
		{ label: "Active clients", value: c.Active ?? 0, icon: Users, tile: "bg-[#FCE8EB] text-[#A10E24]" },
		{ label: "Follow-up pending", value: c["Follow-Up Pending"] ?? 0, icon: Clock, tile: "bg-[#FDECC8] text-[#8A4B00]" },
		{ label: "Closed cases", value: c.Closed ?? 0, icon: Archive, tile: "bg-[#E4E6EA] text-[#3A3F47]" },
		{ label: "Sessions completed", value: totalSessions.value, icon: ClipboardCheck, tile: "bg-[#DCF3E4] text-[#146C3A]" },
	]
})
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
</style>
