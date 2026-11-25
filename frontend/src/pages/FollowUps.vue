<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p class="text-sm font-medium text-[#737780]">Session schedule</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Follow-ups</h1>
          <p class="mt-1 text-sm text-[#737780]">Scheduled follow-up sessions linked to each client’s case history.</p>
        </div>

      </div>

      <div v-if="data?.overdue_total" class="mt-5 flex items-start gap-3 rounded-xl border border-[#F0C8CE] bg-[#FFF6F7] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
        <AlertTriangle :size="19" class="mt-0.5 shrink-0" />
        <p><strong>{{ data.overdue_total }} overdue follow-up{{ data.overdue_total === 1 ? '' : 's' }}.</strong> These are past the appointment date set by the counsellor.</p>
      </div>

      <SearchFilterPanel class="mt-6" v-model:search="term" v-model:filter="status" search-label="Search follow-ups" placeholder="Client name, ID, participant code or mode" filter-label="Follow-up status" filter-aria-label="Filter follow-ups by status" :options="statusOptions" search-hint="Search by client name, client ID, participant code or mode of contact." />

      <ErrorMessage class="mt-4" :message="followups.error" />

      <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
        <ResultListHeader :title="searching ? 'Search results' : status || 'All follow-ups'" :description="resultDescription" :count="rows.length" :count-label="searching ? 'found' : 'total'" :loading="followups.loading" />

        <div v-if="followups.loading && !allRows.length" class="px-5 py-10"><PageLoader /></div>
        <EmptyState v-else-if="!rows.length" :icon="HeartHandshake" :title="searching || status ? 'No matching follow-ups' : 'No scheduled follow-ups'" :description="searching || status ? 'Try another name, participant code or status.' : 'Schedule a Follow-Up appointment to add it here.'">
          <router-link v-if="!searching && !status" :to="{ name: 'AppointmentNew', query: { type: 'Follow-Up' } }" class="inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2 text-sm font-semibold text-white hover:bg-[#A10E24]"><CalendarPlus :size="16" /> Book follow-up</router-link>
        </EmptyState>

        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[760px] text-left">
            <thead><tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><th class="px-5 py-3">Client</th><th class="px-4 py-3">Participant code</th><th class="px-4 py-3">Date &amp; time</th><th class="px-4 py-3">Mode</th><th class="px-4 py-3">Status</th><th class="px-5 py-3 text-right">Action</th></tr></thead>
            <tbody class="divide-y divide-[#F0F1F3]">
              <tr v-for="row in rows" :key="row.name" class="transition hover:bg-[#FCFCFD]">
                <td class="px-5 py-3.5"><ClientLink :client-id="row.client_id" :client-name="row.client_name" /></td>
                <td class="px-4 py-3.5 text-sm font-medium text-[#555860]">{{ row.scholar_code || '—' }}</td>
                <td class="px-4 py-3.5 text-sm text-[#555860]">
                  {{ fmtDateTime(row.date_time) }}
                  <span v-if="row.overdue" class="mt-0.5 block text-xs font-semibold text-[#A10E24]">Overdue against the scheduled date</span>
                </td>
                <td class="px-4 py-3.5 text-sm text-[#555860]">{{ row.mode_of_contact || '—' }}</td>
                <td class="px-4 py-3.5"><Badge :label="row.overdue ? 'Overdue' : 'Scheduled'" :theme="row.overdue ? 'red' : 'blue'" /></td>
                <td class="px-5 py-3.5 text-right">
                  <router-link :to="{ name: 'SessionRecord', params: { name: row.name } }" class="inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#A10E24]"><ClipboardList :size="16" /> In-session</router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="allRows.length" class="flex flex-wrap items-center justify-between gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
          <p class="text-xs text-[#737780]">Showing {{ rows.length }} of {{ allRows.length }} follow-ups</p>
          <p class="text-xs text-[#858891]">Open a client to see their full case history.</p>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { AlertTriangle, CalendarPlus, ClipboardList, HeartHandshake } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"
import ClientLink from "../components/ClientLink.vue"
import EmptyState from "../components/EmptyState.vue"
import ResultListHeader from "../components/ResultListHeader.vue"
import SearchFilterPanel from "../components/SearchFilterPanel.vue"

const term = ref("")
const status = ref("")
const statusOptions = [
	{ label: "All statuses", value: "" },
	{ label: "Scheduled", value: "Scheduled" },
	{ label: "Overdue", value: "Overdue" },
]

const followups = createResource({ url: "krcti_mhpss.api.counsellor.my_followups" })
const data = computed(() => followups.data)
const allRows = computed(() => data.value?.followups || [])

const searching = computed(() => term.value.trim().length > 0)

const rows = computed(() => {
	const q = term.value.trim().toLowerCase()
	return allRows.value.filter((row) => {
		if (status.value === "Overdue" && !row.overdue) return false
		if (status.value === "Scheduled" && row.overdue) return false
		if (!q) return true
		return [row.client_name, row.client_id, row.scholar_code, row.mode_of_contact]
			.some((value) => (value || "").toLowerCase().includes(q))
	})
})

const resultDescription = computed(() =>
	searching.value
		? `Matching “${term.value.trim()}”`
		: `Showing follow-ups${status.value ? ` that are ${status.value.toLowerCase()}` : " across all statuses"}`
)

onMounted(() => followups.submit())
</script>
