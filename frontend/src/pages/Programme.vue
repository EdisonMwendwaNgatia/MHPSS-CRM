<template>
  <main class="mx-auto max-w-5xl px-4 py-6 md:px-8 md:py-8">
    <h1 class="text-xl font-semibold text-gp-ink">Programme overview</h1>
    <p class="mt-1 text-sm text-gp-muted">
      {{ data?.scope === "WoC" ? "The WoC scholarship programme." : "All KRCTI counsellors." }}
      Totals only. Client records and session notes are never shown here.
    </p>

    <div class="mt-4 grid gap-3 rounded-lg border border-gp-line bg-white p-4 sm:grid-cols-2">
      <FormControl label="From" type="date" v-model="from" />
      <FormControl label="To" type="date" v-model="to" />
    </div>

    <ErrorMessage class="mt-3" :message="summary.error" />
    <PageLoader v-if="summary.loading && !data" />

    <template v-if="data">
      <div class="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        <div v-for="[label, value] in tiles" :key="label" class="rounded-lg border border-gp-line bg-white p-4">
          <span class="block text-2xl font-semibold text-gp">{{ value }}</span>
          <span class="mt-1 block text-sm text-gp-muted">{{ label }}</span>
        </div>
      </div>

      <section class="mt-6 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Sessions completed, by mode of contact</h2>
        <div v-for="[mode, n] in Object.entries(data.sessions_by_mode)" :key="mode" class="mt-3">
          <div class="flex justify-between text-sm"><span class="text-gp-ink">{{ mode }}</span><span class="text-gp-muted">{{ n }}</span></div>
          <div class="mt-1 h-2 rounded bg-gp-bg"><div class="h-2 rounded bg-gp" :style="{ width: bar(n) }"></div></div>
        </div>
      </section>

      <section v-if="data.by_counsellor" class="mt-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">By counsellor</h2>
        <div class="mt-3 overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="text-xs text-gp-muted">
              <tr><th class="py-2 pr-3 font-medium">Counsellor</th><th class="px-3 font-medium">Active caseload</th><th class="px-3 font-medium">Completed</th><th class="px-3 font-medium">Upcoming</th><th class="pl-3 font-medium">Overdue</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in data.by_counsellor" :key="r.counsellor" class="border-t border-gp-line">
                <td class="py-2 pr-3 font-medium text-gp-ink">{{ r.counsellor }}</td>
                <td class="px-3">{{ r.active_caseload }}</td><td class="px-3">{{ r.completed_in_range }}</td>
                <td class="px-3">{{ r.upcoming }}</td>
                <td class="pl-3" :class="r.overdue ? 'font-medium text-red-600' : ''">{{ r.overdue }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <section class="rounded-lg border border-gp-line bg-white p-5">
          <h2 class="font-semibold text-gp-ink">Appointments in this period</h2>
          <p v-for="(n, s) in data.appointments_by_status" :key="s" class="mt-2 flex justify-between text-sm"><span>{{ s }}</span><span class="text-gp-muted">{{ n }}</span></p>
          <p v-if="!Object.keys(data.appointments_by_status).length" class="mt-2 text-sm text-gp-muted">None.</p>
        </section>
        <section class="rounded-lg border border-gp-line bg-white p-5">
          <h2 class="font-semibold text-gp-ink">Baseline surveys</h2>
          <p v-for="(n, s) in data.baseline" :key="s" class="mt-2 flex justify-between text-sm"><span>{{ s }}</span><span class="text-gp-muted">{{ n }}</span></p>
          <p v-if="!Object.keys(data.baseline).length" class="mt-2 text-sm text-gp-muted">None yet.</p>
        </section>
      </div>
      <p class="mt-4 text-xs text-gp-muted">Referral figures arrive with the session form in the next release.</p>
    </template>

    <section v-if="showCalendar && calendar.data?.length" class="mt-6 rounded-lg border border-gp-line bg-white p-5">
      <h2 class="font-semibold text-gp-ink">Counsellor calendar</h2>
      <div class="mt-3 overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="text-xs text-gp-muted"><tr><th class="py-2 pr-3 font-medium">When</th><th class="px-3 font-medium">Counsellor</th><th class="px-3 font-medium">Session</th><th class="px-3 font-medium">Mode</th><th class="pl-3 font-medium">Status</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in calendar.data" :key="i" class="border-t border-gp-line">
              <td class="py-2 pr-3">{{ fmtDateTime(r.start) }}</td><td class="px-3">{{ r.counsellor }}</td>
              <td class="px-3">{{ r.session_type }}</td><td class="px-3">{{ r.mode }}</td>
              <td class="pl-3"><Badge :label="r.overdue ? 'Overdue' : r.status" :theme="r.overdue ? 'red' : r.status === 'Completed' ? 'green' : r.status === 'Cancelled' ? 'gray' : 'blue'" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref, watch } from "vue"
import { fmtDateTime } from "../data/format"
import { me } from "../data/me"

const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const to = ref(iso(new Date()))
const from = ref(iso(new Date(Date.now() - 30 * 86400000)))

const summary = createResource({ url: "krcti_mhpss.api.oversight.programme_summary" })
const calendar = createResource({ url: "krcti_mhpss.api.oversight.programme_calendar" })
const data = computed(() => summary.data)
const showCalendar = computed(() => ["krcti_pm", "admin"].includes(me.data?.role))

function load() {
	if (from.value > to.value) return
	summary.submit({ date_from: from.value, date_to: to.value })
	if (showCalendar.value) calendar.submit({ date_from: from.value, date_to: to.value })
}
onMounted(() => me.data ? load() : me.reload())
watch(() => me.data, load)
watch([from, to], load)

const mostSessions = computed(() => Math.max(1, ...Object.values(data.value?.sessions_by_mode || { x: 1 })))
const bar = (n) => `${Math.round((n / mostSessions.value) * 100)}%`
const sum = (o) => Object.values(o || {}).reduce((a, b) => a + b, 0)
const tiles = computed(() => [
	["Active clients", data.value.caseload.Active],
	["Follow-up pending", data.value.caseload["Follow-Up Pending"]],
	["Closed cases", data.value.caseload.Closed],
	["Sessions completed", sum(data.value.sessions_by_mode)],
])
</script>