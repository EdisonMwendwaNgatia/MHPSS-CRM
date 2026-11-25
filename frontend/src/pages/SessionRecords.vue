<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p class="text-sm font-medium text-[#737780]">Session history</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Session records</h1>
          <p class="mt-1 text-sm text-[#737780]">Chronological records of completed counselling sessions.</p>
        </div>
        <router-link :to="{ name: 'Appointments' }" class="inline-flex items-center justify-center gap-2 self-start rounded-lg border border-[#D9DBE0] bg-white px-4 py-2.5 text-sm font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8] sm:self-auto">
          <CalendarDays :size="17" /> Appointments
        </router-link>
      </div>

      <SearchFilterPanel class="mt-6" v-model:search="term" v-model:filter="type" search-label="Search session records" placeholder="Client, ID, participant code, type or summary" filter-label="Session type" filter-aria-label="Filter session records by type" :options="typeOptions" search-hint="Search by client name, client ID, participant code, session type, mode of contact or summary." />

      <ErrorMessage class="mt-4" :message="records.error" />

      <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#ECEDEF] px-5 py-4">
          <div>
            <h2 class="text-base font-semibold text-[#25272B]">{{ searching ? 'Search results' : type || 'Completed sessions' }}</h2>
            <p class="mt-0.5 text-xs text-[#858891]">{{ resultDescription }}</p>
          </div>
          <div class="flex items-center gap-2">
            <LoaderCircle v-if="records.loading" :size="16" class="animate-spin text-[#858891]" />
            <span v-if="searching" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ rows.length }} found</span>
            <span v-else class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ rows.length }} total</span>
          </div>
        </div>

        <div v-if="records.loading && !allRows.length" class="px-5 py-10"><PageLoader /></div>
        <div v-else-if="!rows.length" class="px-5 py-14 text-center">
          <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><BookOpen :size="22" /></span>
          <p class="mt-3 text-sm font-semibold text-[#33353A]">{{ searching || type ? 'No matching session records' : 'No session records yet' }}</p>
          <p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ searching || type ? 'Try another name, participant code, session type or keyword.' : 'Completed session summaries will appear here.' }}</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[920px] text-left">
            <thead><tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><th class="px-5 py-3">Client</th><th class="px-4 py-3">Participant code</th><th class="px-4 py-3">Date &amp; time</th><th class="px-4 py-3">Session type</th><th class="px-4 py-3">Mode</th><th class="px-4 py-3">Summary</th><th class="px-4 py-3">Status</th><th class="px-5 py-3 text-right">Action</th></tr></thead>
            <tbody class="divide-y divide-[#F0F1F3]">
              <tr v-for="row in rows" :key="row.name" class="transition hover:bg-[#FCFCFD]">
                <td class="px-5 py-3.5"><ClientLink :client-id="row.client_id" :client-name="row.client_name" /></td>
                <td class="px-4 py-3.5 text-sm font-medium text-[#555860]">{{ row.scholar_code || '—' }}</td>
                <td class="whitespace-nowrap px-4 py-3.5 text-sm text-[#555860]">{{ fmtDateTime(row.date_time) }}</td>
                <td class="px-4 py-3.5 text-sm text-[#555860]">{{ row.session_type || '—' }}</td>
                <td class="px-4 py-3.5 text-sm text-[#555860]">{{ row.mode_of_contact || '—' }}</td>
                <td class="max-w-[280px] px-4 py-3.5 text-sm text-[#555860]"><span class="block truncate">{{ summaryText(row) }}</span></td>
                <td class="px-4 py-3.5"><Badge label="Recorded" theme="green" /></td>
                <td class="px-5 py-3.5 text-right">
                  <router-link :to="{ name: 'SessionRecord', params: { name: row.name } }" class="inline-flex items-center gap-2 rounded-lg border border-[#D9DBE0] bg-white px-3.5 py-2 text-sm font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8]"><Eye :size="16" /> View record</router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="allRows.length" class="flex flex-wrap items-center justify-between gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
          <p class="text-xs text-[#737780]">Showing {{ rows.length }} of {{ allRows.length }} session records</p>
          <p class="text-xs text-[#858891]">Open a record to see the full session details.</p>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { BookOpen, CalendarDays, Eye, LoaderCircle } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"
import ClientLink from "../components/ClientLink.vue"
import SearchFilterPanel from "../components/SearchFilterPanel.vue"

const term = ref("")
const type = ref("")

function issueText(value) {
	try {
		const parsed = JSON.parse(value)
		return Array.isArray(parsed) ? parsed.join(", ") : value
	} catch {
		return value || ""
	}
}
const summaryText = (row) => issueText(row.presenting_issues) || row.session_details || "Session summary recorded"

const records = createResource({ url: "krcti_mhpss.api.counsellor.my_session_records" })
const allRows = computed(() => records.data || [])

const typeOptions = computed(() => {
	const types = [...new Set(allRows.value.map((row) => row.session_type).filter(Boolean))].sort()
	return [{ label: "All session types", value: "" }, ...types.map((value) => ({ label: value, value }))]
})

const searching = computed(() => term.value.trim().length > 0)

const rows = computed(() => {
	const q = term.value.trim().toLowerCase()
	return allRows.value.filter((row) => {
		if (type.value && row.session_type !== type.value) return false
		if (!q) return true
		return [row.client_name, row.client_id, row.scholar_code, row.session_type, row.mode_of_contact, summaryText(row)]
			.some((value) => (value || "").toLowerCase().includes(q))
	})
})

const resultDescription = computed(() =>
	searching.value
		? `Matching “${term.value.trim()}”`
		: `Showing records${type.value ? ` for ${type.value.toLowerCase()} sessions` : " across all session types"}`
)

onMounted(() => records.submit())
</script>
