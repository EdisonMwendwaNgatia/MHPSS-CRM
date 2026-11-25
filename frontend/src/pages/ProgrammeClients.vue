<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- Header -->
			<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
				<div>
					<p class="text-sm font-medium text-[#737780]">Programme management</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Programme clients</h1>
					<p class="mt-1 text-sm text-[#737780]">Client records, case statuses and counsellor assignments within your programme.</p>
				</div>
				<router-link :to="{ name: 'ProgrammeClientNew' }" class="btn btn-primary self-start sm:self-auto">
					<UserRoundPlus :size="17" /> Register client
				</router-link>
			</div>

			<!-- Toolbar -->
			<section class="mt-6 rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
				<div class="flex flex-col gap-4 lg:flex-row lg:items-end">
					<label class="block min-w-0 flex-1">
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Search clients</span>
						<span class="flex h-11 items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10">
							<Search :size="17" class="shrink-0 text-[#858891]" />
							<input v-model="term" type="search" placeholder="Participant code, name, phone or institution" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
							<button v-if="term" type="button" class="inline-flex shrink-0 items-center gap-1 rounded-md px-1.5 py-0.5 text-xs font-medium text-[#858891] transition hover:bg-[#F4F5F7] hover:text-[#33353A]" @click="term = ''"><X :size="13" /> Clear</button>
						</span>
					</label>

					<div>
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Case status</span>
						<div class="inline-flex w-full rounded-lg bg-[#F4F5F7] p-1 lg:w-auto" role="group" aria-label="Filter by case status">
							<button v-for="option in statusOptions" :key="option.value" type="button" class="seg" :class="status === option.value ? 'seg-on' : ''" :aria-pressed="status === option.value" @click="chooseStatus(option.value)">{{ option.label }}</button>
						</div>
					</div>
				</div>
				<p v-if="cohort" class="mt-3 flex items-center gap-2 text-xs text-[#5B616B]">Showing clients in Cohort {{ cohort }} <button type="button" class="font-semibold text-[#A10E24] hover:underline" @click="clearCohort">Clear cohort filter</button></p>
				<p v-if="searching" class="mt-3 text-xs text-[#858891]">Searching by participant code, client name, phone number or institution.</p>
			</section>

			<ErrorMessage class="mt-4" :message="clients.error" />

			<!-- Clients -->
			<section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
				<ResultListHeader :title="searching ? 'Search results' : selectedStatus.label" :description="resultDescription" :count="totalClients" :count-label="searching ? 'found' : 'total'" :loading="clients.loading && !!clientList.length" />

				<div v-if="clients.loading && !clientList.length" class="px-5 py-10"><PageLoader /></div>

				<EmptyState v-else-if="!clientList.length" :icon="UsersRound" :title="searching ? 'No matching clients' : 'No clients found'" :description="searching ? 'Try another participant code, client name, phone number or institution.' : 'Register a client to add them to this programme.'">
					<router-link v-if="!searching" :to="{ name: 'ProgrammeClientNew' }" class="btn btn-primary"><UserRoundPlus :size="16" /> Register client</router-link>
				</EmptyState>

				<div v-else class="overflow-x-auto">
					<table class="w-full min-w-[1020px] text-left">
						<thead>
							<tr class="border-b border-[#ECEDEF] bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]">
								<th class="px-5 py-3">Client</th>
								<th class="px-4 py-3">Participant code</th>
								<th class="px-4 py-3">Counsellor</th>
								<th class="px-4 py-3">Institution</th>
								<th class="px-4 py-3 text-center">Sessions</th>
								<th class="px-4 py-3">Baseline</th>
								<th class="px-4 py-3">Case status</th>
								<th class="px-5 py-3 text-right">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-[#F0F1F3]">
							<tr v-for="row in clientList" :key="row.name" class="group/row transition hover:bg-[#FCFCFD]">
								<td class="w-[260px] max-w-[260px] px-5 py-3.5">
									<router-link
										:to="{ name: 'ProgrammeClientDetail', params: { name: row.name } }"
										class="group flex items-center gap-3"
										:title="row.full_name"
										:aria-label="row.full_name"
									>
										<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials(row.full_name) }}</span>
										<span class="min-w-0">
											<span class="block truncate text-sm font-semibold text-[#33353A] group-hover:text-[#B30F2A]">{{ firstName(row.full_name) }}</span>
											<span v-if="restOfName(row.full_name)" class="block truncate text-xs text-[#62656D]">{{ restOfName(row.full_name) }}</span>
											<span class="mt-0.5 block truncate text-xs text-[#858891]">{{ row.phone_number || row.name }}</span>
										</span>
									</router-link>
								</td>

								<td class="whitespace-nowrap px-4 py-3.5">
									<span v-if="row.scholar_code" class="inline-block rounded-md bg-[#F4F5F7] px-2 py-1 text-xs font-semibold tabular-nums text-[#44474E]">{{ row.scholar_code }}</span>
									<span v-else class="text-sm text-[#A0A2A8]">—</span>
								</td>

								<td class="px-4 py-3.5">
									<div v-if="row.counsellor_name" class="flex items-center gap-2.5">
										<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#F4F5F7] text-[10px] font-bold text-[#62656D]">{{ initials(row.counsellor_name) }}</span>
										<span class="truncate text-sm font-medium text-[#44474E]">{{ row.counsellor_name }}</span>
									</div>
									<span v-else class="inline-flex items-center gap-1.5 rounded-full bg-[#FDECC8] px-2.5 py-1 text-xs font-semibold text-[#8A4B00]"><span class="h-1.5 w-1.5 rounded-full bg-[#8A4B00]"></span> Unassigned</span>
								</td>

								<td class="max-w-[220px] px-4 py-3.5 text-sm text-[#555860]"><span class="block truncate">{{ row.institution || '—' }}</span></td>

								<td class="whitespace-nowrap px-4 py-3.5 text-center text-sm font-semibold tabular-nums text-[#33353A]">{{ row.sessions ?? 0 }}</td>

								<td class="whitespace-nowrap px-4 py-3.5">
									<span v-if="row.baseline_review_status === 'Verified'" class="inline-flex items-center gap-1.5 rounded-full bg-[#DCF3E4] px-2.5 py-1 text-xs font-semibold text-[#146C3A]"><ShieldCheck :size="13" /> Verified</span>
									<span v-else-if="row.baseline_review_status" class="inline-flex items-center gap-1.5 rounded-full bg-[#E4E6EA] px-2.5 py-1 text-xs font-semibold text-[#3A3F47]"><Clock :size="13" /> {{ row.baseline_review_status }}</span>
									<span v-else class="text-sm text-[#A0A2A8]">—</span>
								</td>

								<td class="px-4 py-3.5"><Badge :label="row.case_status || 'Active'" :theme="caseTheme(row.case_status)" /></td>

								<td class="px-5 py-3.5">
									<div class="flex items-center justify-end gap-2">
										<template v-if="!row.assigned_counsellor">
											<router-link v-if="row.baseline_review_status === 'Verified'" :to="{ name: 'ProgrammeClientDetail', params: { name: row.name }, query: { tab: 'survey' } }" class="btn btn-accent btn-sm" title="Open assignment controls">
												<UserRoundPlus :size="15" /> Assign
											</router-link>
											<button v-else type="button" class="btn btn-secondary btn-sm" disabled title="Assign counsellor is available after baseline verification">
												<Lock :size="14" /> Assign
											</button>
										</template>
										<router-link :to="{ name: 'ProgrammeClientDetail', params: { name: row.name } }" class="btn btn-secondary btn-sm">
											<Eye :size="15" /> View record <ArrowRight :size="14" class="text-[#A0A2A8]" />
										</router-link>
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<div v-if="clientList.length" class="flex flex-wrap items-center justify-between gap-3 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
					<p class="text-xs text-[#737780]">Showing {{ clientList.length }} of {{ totalClients }} clients</p>
					<button v-if="totalClients > clientList.length" type="button" class="btn btn-secondary" :disabled="clients.loading" @click="fetchClients(true)">
						<LoaderCircle v-if="clients.loading" :size="15" class="animate-spin" /> {{ clients.loading ? 'Loading…' : 'Load more' }}
					</button>
					<p v-else class="text-xs text-[#858891]">Use search to find a specific client.</p>
				</div>
			</section>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { ArrowRight, Clock, Eye, Lock, LoaderCircle, Search, ShieldCheck, UserRoundPlus, UsersRound, X } from "lucide-vue-next"
import { caseTheme } from "../data/format"
import EmptyState from "../components/EmptyState.vue"
import ResultListHeader from "../components/ResultListHeader.vue"

const term = ref("")
const route = useRoute()
const cohort = ref(["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(route.query.cohort) ? route.query.cohort : "")
const status = ref(["Active", "Closed", ""].includes(route.query.status) ? route.query.status : cohort.value ? "" : "Active")

const statusOptions = [
	{ label: "Active", value: "Active" },
	{ label: "Closed", value: "Closed" },
	{ label: "All clients", value: "" },
]

const clientRows = ref([])
const totalClients = ref(0)
let appendResults = false
const clients = createResource({
	url: "krcti_mhpss.api.oversight.programme_clients",
	onSuccess(result) {
		clientRows.value = appendResults ? [...clientRows.value, ...(result.clients || [])] : (result.clients || [])
		totalClients.value = result.total || 0
		appendResults = false
	},
})

const searching = computed(() => term.value.trim().length > 0)
const clientList = computed(() => clientRows.value)
const selectedStatus = computed(() => statusOptions.find((opt) => opt.value === status.value) || statusOptions[0])

const resultDescription = computed(() => {
	const scope = cohort.value ? ` in Cohort ${cohort.value}` : ""
	if (searching.value) return `Matching “${term.value.trim()}”${scope}`
	if (status.value === "Active") return `Showing all active cases, including clients awaiting follow-up${scope}`
	return `Showing clients${status.value ? ` with ${status.value.toLowerCase()} cases` : " across all case statuses"}${scope}`
})

const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()
const nameParts = (name) => String(name || "").trim().split(/\s+/).filter(Boolean)
const firstName = (name) => nameParts(name)[0] || "—"
const restOfName = (name) => nameParts(name).slice(1).join(" ")
const chooseStatus = (val) => { status.value = val }

let debounceTimer = null
function fetchClients(append = false) {
	appendResults = append === true
	clients.submit({
		search: term.value.trim() || undefined,
		status: status.value || undefined,
		cohort: cohort.value || undefined,
		start: appendResults ? clientRows.value.length : 0,
		page_length: 100,
	})
}

watch([term, status, cohort], () => {
	clearTimeout(debounceTimer)
	debounceTimer = setTimeout(() => fetchClients(), 250)
})
watch(() => route.query.status, (value) => {
	if (["Active", "Closed", ""].includes(value) && status.value !== value) status.value = value
})
watch(() => route.query.cohort, (value) => {
	const nextCohort = ["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(value) ? value : ""
	if (cohort.value !== nextCohort) cohort.value = nextCohort
	if (!["Active", "Closed", ""].includes(route.query.status)) status.value = nextCohort ? "" : "Active"
})

function clearCohort() {
	cohort.value = ""
	if (!["Active", "Closed", ""].includes(route.query.status)) status.value = "Active"
	const query = { ...route.query }
	delete query.cohort
	route.replace({ query })
}

onBeforeUnmount(() => clearTimeout(debounceTimer))
onMounted(() => fetchClients())
</script>

<style scoped>
/* ---- Button system ---- */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid transparent; border-radius: 8px; padding: 10px 16px; font-size: 14px; font-weight: 600; line-height: 20px; white-space: nowrap; transition: background 0.15s, border-color 0.15s, color 0.15s, box-shadow 0.15s; }
.btn:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.2); }
.btn:disabled { cursor: not-allowed; }
.btn-sm { padding: 7px 12px; font-size: 13px; line-height: 18px; gap: 6px; }

.btn-primary { background: #c8102e; color: #fff; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.12); }
.btn-primary:hover { background: #a10e24; }

.btn-secondary { border-color: #d9dbe0; background: #fff; color: #33353a; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.04); }
.btn-secondary:hover:not(:disabled) { border-color: #c8102e; color: #a10e24; background: #fff; }
.btn-secondary:disabled { border-color: #e4e6ea; background: #f7f7f8; color: #a0a2a8; box-shadow: none; }

.btn-accent { border-color: #f0c8ce; background: #fff6f7; color: #a10e24; }
.btn-accent:hover { background: #fce8eb; border-color: #e6a9b3; }

/* ---- Segmented control ---- */
.seg { flex: 1; border-radius: 6px; padding: 7px 14px; font-size: 13px; font-weight: 600; color: #62656d; white-space: nowrap; transition: background 0.15s, color 0.15s, box-shadow 0.15s; }
.seg:hover { color: #25272b; }
.seg:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.2); }
.seg-on { background: #fff; color: #a10e24; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.1), 0 0 0 1px #e4e6ea; }

</style>
