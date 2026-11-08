<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- Header -->
			<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
				<div>
					<p class="text-sm font-medium text-[#737780]">Programme oversight</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Session management</h1>
					<p class="mt-1 text-sm text-[#737780]">Review appointments and recorded activity for a counsellor.</p>
				</div>
			</div>

			<!-- Counsellor selector -->
			<section class="mt-6 rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
				<div class="grid gap-4 md:grid-cols-[minmax(0,420px)_minmax(0,1fr)] md:items-end">
					<div class="block">
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Counsellor</span>
						<div class="relative" data-counsellor-menu>
							<button type="button" class="flex h-11 w-full items-center justify-between gap-3 rounded-lg border border-[#D9DBE0] bg-white px-3.5 text-left text-sm font-medium text-[#33353A] shadow-[0_1px_2px_rgba(20,25,35,0.03)] outline-none transition hover:border-[#BFC2C8] focus:border-[#C8102E] focus:ring-2 focus:ring-[#C8102E]/10" :aria-expanded="counsellorMenuOpen" aria-haspopup="listbox" @click="toggleCounsellorMenu">
								<span v-if="activeCounsellor" class="flex min-w-0 items-center gap-2.5">
									<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-[10px] font-bold text-[#B30F2A]">{{ initials(activeCounsellor.full_name) }}</span>
									<span class="truncate">{{ activeCounsellor.full_name }}</span>
								</span>
								<span v-else class="text-[#A0A2A8]">Choose a counsellor</span>
								<ChevronDown :size="16" class="shrink-0 text-[#737780] transition-transform" :class="counsellorMenuOpen ? 'rotate-180' : ''" />
							</button>
							<div v-if="counsellorMenuOpen" class="absolute left-0 right-0 z-30 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-label="Select counsellor">
								<div class="border-b border-[#ECEDEF] p-2">
									<span class="flex h-9 items-center gap-2 rounded-lg bg-[#F4F5F7] px-3">
										<Search :size="15" class="shrink-0 text-[#858891]" />
										<input ref="counsellorSearchRef" v-model="counsellorTerm" type="search" placeholder="Search counsellors" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
									</span>
								</div>
								<div class="max-h-72 overflow-y-auto p-1.5">
									<button v-for="person in filteredCounsellors" :key="person.name" type="button" role="option" :aria-selected="selectedCounsellor === person.name" class="flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition" :class="selectedCounsellor === person.name ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click="chooseCounsellor(person.name)">
										<span class="flex min-w-0 items-center gap-2.5">
											<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-bold" :class="selectedCounsellor === person.name ? 'bg-white text-[#B30F2A]' : 'bg-[#F4F5F7] text-[#62656D]'">{{ initials(person.full_name) }}</span>
											<span class="truncate">{{ person.full_name }}</span>
											<span v-if="!person.enabled" class="shrink-0 rounded-full bg-[#F4F5F7] px-2 py-0.5 text-[10px] font-semibold text-[#737780]">Inactive</span>
										</span>
										<Check v-if="selectedCounsellor === person.name" :size="16" class="shrink-0 text-[#C8102E]" />
									</button>
									<p v-if="!filteredCounsellors.length" class="px-3 py-6 text-center text-sm text-[#858891]">No counsellors found.</p>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeCounsellor" class="flex items-center gap-3 md:justify-end">
						<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials(activeCounsellor.full_name) }}</span>
						<div class="min-w-0">
							<p class="truncate text-sm font-semibold text-[#33353A]">{{ activeCounsellor.full_name }}</p>
							<p class="mt-0.5 text-xs text-[#858891]">{{ allSessions.length }} appointments loaded</p>
						</div>
						<span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="activeCounsellor.enabled ? 'bg-[#DCF3E4] text-[#146C3A]' : 'bg-[#E4E6EA] text-[#3A3F47]'">{{ activeCounsellor.enabled ? 'Active' : 'Inactive' }}</span>
					</div>
					<p v-else class="text-xs text-[#858891] md:text-right">Select a counsellor to load their appointments and activity.</p>
				</div>
				<ErrorMessage class="mt-3" :message="counsellors.error" />
			</section>

			<template v-if="selectedCounsellor">
				<!-- Summary cards -->
				<section class="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Appointment summary">
					<button v-for="card in cards" :key="card.key" type="button" class="group rounded-xl border bg-white p-4 text-left shadow-[0_1px_2px_rgba(20,25,35,0.03)] transition hover:border-[#BFC2C8]" :class="selectedStatus === card.key ? 'border-[#C8102E] ring-2 ring-[#C8102E]/10' : 'border-[#E4E6EA]'" :aria-pressed="selectedStatus === card.key" @click="selectedStatus = card.key">
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs font-semibold text-[#555860]">{{ card.label }}</span>
							<span class="flex h-8 w-8 items-center justify-center rounded-full" :class="card.tone"><component :is="card.icon" :size="16" /></span>
						</div>
						<span class="mt-3 block text-[28px] font-semibold leading-none tabular-nums text-[#25272B]">{{ card.value }}</span>
					</button>
				</section>

				<!-- Search & tools -->
				<section class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
					<label class="block">
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Search appointments</span>
						<span class="flex h-11 items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10">
							<Search :size="17" class="shrink-0 text-[#858891]" />
							<input v-model="term" type="search" placeholder="Appointment ID, client, participant code or session type" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
							<button v-if="term" type="button" class="shrink-0 text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="term = ''">Clear</button>
						</span>
					</label>
				</section>

				<ErrorMessage class="mt-4" :message="sessions.error || manageSession.error" />

				<!-- Appointments -->
				<section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<div class="flex flex-wrap items-center justify-between gap-3 border-b border-[#ECEDEF] px-5 py-4">
						<div>
							<h2 class="text-base font-semibold text-[#25272B]">{{ searching ? 'Search results' : statusTitle }}</h2>
							<p class="mt-0.5 text-xs text-[#858891]">Grouped by client and identified by their APT number.</p>
						</div>
						<div class="flex flex-wrap items-center gap-2">
							<LoaderCircle v-if="sessions.loading" :size="16" class="animate-spin text-[#858891]" />
							<button v-if="sessionGroups.length > 1" type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-[#D9DBE0] bg-white px-3 py-1.5 text-xs font-semibold text-[#44474E] transition hover:bg-[#F7F7F8]" @click="allCollapsed ? expandAll() : collapseAll()">
								<ChevronsUpDown :size="14" /> {{ allCollapsed ? 'Expand all' : 'Collapse all' }}
							</button>
							<span class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ filteredSessions.length }} {{ searching ? 'found' : 'records' }}</span>
						</div>
					</div>

					<div v-if="sessions.loading && !allSessions.length" class="px-5 py-10"><PageLoader /></div>
					<div v-else-if="!filteredSessions.length" class="px-5 py-14 text-center">
						<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><CalendarClock :size="22" /></span>
						<p class="mt-3 text-sm font-semibold text-[#33353A]">{{ searching ? 'No matching appointments' : 'No appointments found' }}</p>
						<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ searching ? 'Try another appointment ID, client name or participant code.' : 'No appointments match this status for the selected counsellor.' }}</p>
					</div>

					<div v-else class="overflow-x-auto">
						<table class="w-full min-w-[760px] text-left text-sm">
							<thead>
								<tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]">
									<th class="px-5 py-3">Appointment</th>
									<th class="px-4 py-3">Date &amp; time</th>
									<th class="px-4 py-3">Session</th>
									<th class="px-4 py-3">Status</th>
									<th class="px-5 py-3 text-right">Action</th>
								</tr>
							</thead>
							<template v-for="group in sessionGroups" :key="group.client_id || group.client_name">
								<tbody class="divide-y divide-[#F0F1F3] border-t border-[#ECEDEF]">
									<tr class="bg-[#FAFAFB]">
										<th colspan="5" class="p-0 text-left font-normal">
											<div class="flex items-center gap-3 px-5 py-3">
												<button type="button" class="flex min-w-0 flex-1 items-center gap-3 text-left" :aria-expanded="!isCollapsed(group)" @click="toggleClient(group)">
													<ChevronRight :size="16" class="shrink-0 text-[#858891] transition-transform" :class="isCollapsed(group) ? '' : 'rotate-90'" />
													<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-[11px] font-bold text-[#B30F2A]">{{ initials(group.client_name) }}</span>
													<span class="min-w-0">
														<span class="block truncate text-sm font-semibold text-[#33353A]">{{ group.client_name || 'Client' }}</span>
														<span class="mt-0.5 block truncate text-xs text-[#858891]">{{ group.scholar_code || group.client_id }}</span>
													</span>
													<span class="ml-1 shrink-0 rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-[#62656D] ring-1 ring-[#E4E6EA]">{{ group.appointments.length }} appointment{{ group.appointments.length === 1 ? '' : 's' }}</span>
												</button>
												<router-link v-if="group.client_id" :to="{ name: 'ProgrammeClientDetail', params: { name: group.client_id } }" class="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-[#D9DBE0] bg-white px-3 py-1.5 text-xs font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8]">
													<ExternalLink :size="13" /> View record
												</router-link>
											</div>
										</th>
									</tr>
									<tr v-for="row in group.appointments" v-show="!isCollapsed(group)" :key="row.name" class="transition hover:bg-[#FCFCFD]">
										<td class="whitespace-nowrap py-3.5 pl-[68px] pr-4 text-sm font-semibold text-[#33353A]">{{ row.name }}</td>
										<td class="whitespace-nowrap px-4 py-3.5 text-sm text-[#555860]">{{ dateTime(row.date_time) }}</td>
										<td class="px-4 py-3.5 text-sm text-[#555860]">
											{{ row.session_type || '—' }}
											<span v-if="row.mode_of_contact" class="mt-0.5 block text-xs text-[#858891]">{{ row.mode_of_contact }}</span>
										</td>
										<td class="px-4 py-3.5"><Badge :label="row.overdue && row.status === 'Scheduled' ? 'Overdue' : row.status" :theme="row.overdue && row.status === 'Scheduled' ? 'red' : statusTheme(row.status)" /></td>
										<td class="px-5 py-3.5 text-right">
											<button v-if="row.status === 'Scheduled'" type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 py-2 text-sm font-semibold text-[#33353A] shadow-sm transition hover:border-[#C8102E] hover:text-[#A10E24]" @click="openSession(row)">
												<SlidersHorizontal :size="15" /> Manage
											</button>
											<span v-else class="text-xs text-[#A0A2A8]">—</span>
										</td>
									</tr>
								</tbody>
							</template>
						</table>
					</div>

					<div v-if="allSessions.length" class="flex flex-wrap items-center justify-between gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
						<p class="text-xs text-[#737780]">Showing {{ filteredSessions.length }} of {{ allSessions.length }} appointments across {{ sessionGroups.length }} client{{ sessionGroups.length === 1 ? '' : 's' }}</p>
						<p class="text-xs text-[#858891]">Only scheduled appointments can be managed.</p>
					</div>
				</section>

				<!-- Activity -->
				<section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#ECEDEF] px-5 py-4">
						<div>
							<h2 class="text-base font-semibold text-[#25272B]">Counsellor activity</h2>
							<p class="mt-0.5 text-xs text-[#858891]">Appointment, client and account activity recorded for this counsellor.</p>
						</div>
						<div class="flex items-center gap-2">
							<LoaderCircle v-if="activity.loading" :size="16" class="animate-spin text-[#858891]" />
							<span v-if="activityTotal" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ activityRows.length }} of {{ activityTotal }}</span>
						</div>
					</div>
					<ActivityTable :rows="activityRows" :loading="activity.loading" />
					<div v-if="activityTotal > activityRows.length" class="flex justify-center border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
						<button type="button" class="inline-flex items-center gap-2 rounded-lg border border-[#D9DBE0] bg-white px-4 py-2 text-sm font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8] disabled:cursor-wait disabled:opacity-60" :disabled="activity.loading" @click="loadMoreActivity">
							<LoaderCircle v-if="activity.loading" :size="15" class="animate-spin" /> Load more activity
						</button>
					</div>
					<ErrorMessage v-if="activity.error" class="px-5 pb-4" :message="activity.error" />
				</section>
			</template>

			<!-- Empty state -->
			<section v-else class="mt-5 rounded-xl border border-dashed border-[#D5D8DE] bg-white px-5 py-16 text-center">
				<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><UsersRound :size="22" /></span>
				<p class="mt-3 text-sm font-semibold text-[#33353A]">No counsellor selected</p>
				<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">Choose a counsellor above to load all of their appointments and activity.</p>
			</section>
		</div>

		<!-- Manage appointment modal -->
		<div v-if="selectedSession" class="fixed inset-0 z-50 flex items-center justify-center bg-[#1F232D]/40 p-4 backdrop-blur-[2px]" @click.self="closeSession">
			<form class="w-full max-w-lg overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_24px_60px_rgba(31,35,45,0.25)]" role="dialog" aria-modal="true" aria-labelledby="manage-title" @submit.prevent="submitSessionAction">
				<div class="flex items-start justify-between gap-4 border-b border-[#ECEDEF] px-5 py-4">
					<div>
						<h2 id="manage-title" class="text-base font-semibold text-[#25272B]">Manage appointment</h2>
						<p class="mt-0.5 text-xs text-[#858891]">Reassign this session to another counsellor or cancel it.</p>
					</div>
					<button type="button" class="rounded-lg p-1.5 text-[#858891] transition hover:bg-[#F4F5F7] hover:text-[#33353A]" aria-label="Close" @click="closeSession"><X :size="18" /></button>
				</div>

				<div class="space-y-5 px-5 py-5">
					<div class="flex items-center gap-3 rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-3.5">
						<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials(selectedSession.client_name) }}</span>
						<div class="min-w-0">
							<p class="truncate text-sm font-semibold text-[#33353A]">{{ selectedSession.client_name || selectedSession.scholar_code }}</p>
							<p class="mt-0.5 truncate text-xs text-[#858891]">{{ selectedSession.name }} · {{ dateTime(selectedSession.date_time) }}<span v-if="selectedSession.scholar_code"> · {{ selectedSession.scholar_code }}</span></p>
						</div>
					</div>

					<div>
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Action</span>
						<div class="grid grid-cols-2 gap-2 rounded-xl bg-[#F4F5F7] p-1">
							<button type="button" class="flex h-10 items-center justify-center gap-2 rounded-lg text-sm font-semibold transition" :class="sessionAction === 'reassign' ? 'bg-white text-[#A10E24] shadow-sm ring-1 ring-[#E4E6EA]' : 'text-[#62656D] hover:text-[#33353A]'" @click="sessionAction = 'reassign'"><ArrowRightLeft :size="15" /> Reassign</button>
							<button type="button" class="flex h-10 items-center justify-center gap-2 rounded-lg text-sm font-semibold transition" :class="sessionAction === 'cancel' ? 'bg-white text-[#A10E24] shadow-sm ring-1 ring-[#E4E6EA]' : 'text-[#62656D] hover:text-[#33353A]'" @click="sessionAction = 'cancel'"><Ban :size="15" /> Cancel</button>
						</div>
					</div>

					<label v-if="sessionAction === 'reassign'" class="block">
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">New counsellor <span class="text-[#A10E24]">*</span></span>
						<select v-model="targetCounsellor" class="field" required>
							<option value="">Choose counsellor</option>
							<option v-for="person in counsellors.data || []" :key="person.name" :value="person.name" :disabled="!person.enabled || person.name === selectedSession.counsellor_id">{{ person.full_name }}{{ person.enabled ? '' : ' (inactive)' }}{{ person.name === selectedSession.counsellor_id ? ' (current)' : '' }}</option>
						</select>
					</label>
					<div v-else class="flex items-start gap-3 rounded-lg border border-[#F0C8CE] bg-[#FFF6F7] px-3.5 py-3 text-sm text-[#A10E24]" role="alert">
						<AlertTriangle :size="17" class="mt-0.5 shrink-0" />
						<p>Cancelling removes this appointment from the schedule. A reason is required for the audit trail.</p>
					</div>

					<label class="block">
						<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Reason for this change <span class="text-[#A10E24]">*</span></span>
						<textarea v-model="actionReason" class="field" rows="3" required minlength="3" maxlength="2000" placeholder="Briefly explain why this change is needed" />
						<span class="mt-1 block text-right text-[11px] text-[#A0A2A8]">{{ actionReason.length }}/2000</span>
					</label>

					<ErrorMessage :message="manageSession.error" />
				</div>

				<div class="flex items-center justify-end gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3.5">
					<button type="button" class="secondary" @click="closeSession">Close</button>
					<button type="submit" class="primary" :disabled="manageSession.loading">
						<LoaderCircle v-if="manageSession.loading" :size="15" class="mr-2 animate-spin" />
						{{ sessionAction === 'reassign' ? 'Reassign appointment' : 'Cancel appointment' }}
					</button>
				</div>
			</form>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue"
import { AlertTriangle, ArrowRightLeft, Ban, CalendarClock, Check, ChevronDown, ChevronRight, ChevronsUpDown, ClipboardCheck, ExternalLink, Layers, LoaderCircle, Search, SlidersHorizontal, UsersRound, X } from "lucide-vue-next"
import ActivityTable from "../components/ActivityTable.vue"
import { fmtDateTime } from "../data/format"
import { useRoute } from "vue-router"

const route = useRoute()
const selectedCounsellor = ref("")
const selectedStatus = ref("all")
const selectedSession = ref(null)
const collapsedClients = ref(new Set())
const sessionAction = ref("reassign")
const targetCounsellor = ref("")
const actionReason = ref("")
const activityRows = ref([])
const activityTotal = ref(0)
const loadedCounsellor = ref("")
const term = ref("")
const counsellorTerm = ref("")
const counsellorMenuOpen = ref(false)
const counsellorSearchRef = ref(null)
let activityStart = 0

const dateTime = (value) => value ? fmtDateTime(value) : "—"
const initials = (fullName) => (fullName || "Client").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase()

const counsellors = createResource({ url: "krcti_mhpss.api.oversight.programme_counsellors" })
const sessions = createResource({ url: "krcti_mhpss.api.oversight.programme_sessions", onSuccess() { loadedCounsellor.value = selectedCounsellor.value } })
const activity = createResource({
	url: "krcti_mhpss.api.oversight.programme_counsellor_activity",
	onSuccess(result) {
		const next = result.logs || []
		activityRows.value = activityStart ? [...activityRows.value, ...next] : next
		activityTotal.value = result.total || 0
		activityStart += next.length
	},
})
const manageSession = createResource({
	url: "krcti_mhpss.api.oversight.programme_manage_session",
	onSuccess() { selectedSession.value = null; loadAppointments() },
})

// ---- Counsellor dropdown ----
const activeCounsellor = computed(() => (counsellors.data || []).find((person) => person.name === selectedCounsellor.value) || null)
const filteredCounsellors = computed(() => {
	const q = counsellorTerm.value.trim().toLowerCase()
	const list = counsellors.data || []
	return q ? list.filter((person) => (person.full_name || "").toLowerCase().includes(q)) : list
})
function toggleCounsellorMenu() {
	counsellorMenuOpen.value = !counsellorMenuOpen.value
	if (counsellorMenuOpen.value) {
		counsellorTerm.value = ""
		nextTick(() => counsellorSearchRef.value?.focus())
	}
}
function chooseCounsellor(name) {
	selectedCounsellor.value = name
	counsellorMenuOpen.value = false
}
function onOutsideClick(event) {
	if (!event.target.closest("[data-counsellor-menu]")) counsellorMenuOpen.value = false
}
function onKeydown(event) {
	if (event.key !== "Escape") return
	if (selectedSession.value) closeSession()
	else counsellorMenuOpen.value = false
}

// ---- Sessions ----
const allSessions = computed(() => loadedCounsellor.value === selectedCounsellor.value ? (sessions.data || []) : [])
const searching = computed(() => term.value.trim().length > 0)
const statusTitle = computed(() => ({ all: "All appointments", scheduled: "Pending / scheduled", completed: "Completed appointments", cancelled: "Cancelled appointments" })[selectedStatus.value])

const filteredSessions = computed(() => {
	let rows = allSessions.value
	if (selectedStatus.value === "scheduled") rows = rows.filter((row) => row.status === "Scheduled")
	else if (selectedStatus.value === "completed") rows = rows.filter((row) => row.status === "Completed")
	else if (selectedStatus.value === "cancelled") rows = rows.filter((row) => row.status === "Cancelled")
	const q = term.value.trim().toLowerCase()
	if (!q) return rows
	return rows.filter((row) => [row.name, row.client_name, row.client_id, row.scholar_code, row.session_type, row.mode_of_contact]
		.some((value) => (value || "").toLowerCase().includes(q)))
})
const sessionGroups = computed(() => {
	const groups = new Map()
	for (const row of filteredSessions.value) {
		const key = row.client_id || row.client_name || row.name
		if (!groups.has(key)) {
			groups.set(key, {
				client_id: row.client_id,
				client_name: row.client_name,
				scholar_code: row.scholar_code,
				appointments: [],
			})
		}
		groups.get(key).appointments.push(row)
	}
	return [...groups.values()].sort((a, b) => (a.scholar_code || a.client_name || "").localeCompare(b.scholar_code || b.client_name || ""))
})
const cards = computed(() => [
	{ key: "all", label: "All appointments", value: allSessions.value.length, icon: Layers, tone: "bg-[#F4F5F7] text-[#62656D]" },
	{ key: "scheduled", label: "Pending / scheduled", value: allSessions.value.filter((row) => row.status === "Scheduled").length, icon: CalendarClock, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
	{ key: "completed", label: "Completed", value: allSessions.value.filter((row) => row.status === "Completed").length, icon: ClipboardCheck, tone: "bg-[#DCF3E4] text-[#146C3A]" },
	{ key: "cancelled", label: "Cancelled", value: allSessions.value.filter((row) => row.status === "Cancelled").length, icon: Ban, tone: "bg-[#E4E6EA] text-[#3A3F47]" },
])
const statusTheme = (status) => ({ Scheduled: "blue", Completed: "green", Cancelled: "gray" })[status] || "gray"

// ---- Group collapse ----
const groupKey = (group) => group.client_id || group.client_name
const isCollapsed = (group) => collapsedClients.value.has(groupKey(group))
const allCollapsed = computed(() => sessionGroups.value.length > 0 && sessionGroups.value.every((group) => isCollapsed(group)))
function toggleClient(group) {
	const next = new Set(collapsedClients.value)
	const key = groupKey(group)
	if (next.has(key)) next.delete(key)
	else next.add(key)
	collapsedClients.value = next
}
function collapseAll() { collapsedClients.value = new Set(sessionGroups.value.map(groupKey)) }
function expandAll() { collapsedClients.value = new Set() }

// ---- Loading ----
function loadAppointments() {
	if (selectedCounsellor.value) sessions.submit({ counsellor: selectedCounsellor.value })
}
function loadActivity(start = 0) {
	if (!selectedCounsellor.value) return
	activityStart = start
	activity.submit({ user: selectedCounsellor.value, start, page_length: 100 })
}
function loadMoreActivity() { loadActivity(activityStart) }
watch(selectedCounsellor, (user) => {
	activityRows.value = []
	activityTotal.value = 0
	selectedStatus.value = "all"
	term.value = ""
	collapsedClients.value = new Set()
	if (user) {
		sessions.submit({ counsellor: user })
		loadActivity()
	} else {
		loadedCounsellor.value = ""
	}
})
onMounted(() => {
	counsellors.submit()
	document.addEventListener("click", onOutsideClick)
	document.addEventListener("keydown", onKeydown)
})
watch([() => route.query.counsellor, () => counsellors.data], ([requested, people]) => {
	if (!requested || !people) return
	const match = people.find((person) => person.name === requested)
	if (match) chooseCounsellor(match.name)
}, { immediate: true })
onUnmounted(() => {
	document.removeEventListener("click", onOutsideClick)
	document.removeEventListener("keydown", onKeydown)
})

// ---- Manage modal ----
function openSession(row) {
	selectedSession.value = row
	targetCounsellor.value = ""
	actionReason.value = ""
	sessionAction.value = "reassign"
}
function closeSession() { selectedSession.value = null }
function submitSessionAction() {
	manageSession.submit({ name: selectedSession.value.name, action: sessionAction.value, counsellor: targetCounsellor.value, reason: actionReason.value })
}
</script>

<style scoped>
.field { display: block; width: 100%; min-height: 44px; border: 1px solid #d9dbe0; border-radius: 10px; background: #fff; padding: 10px 12px; font-family: inherit; font-size: 14px; line-height: 20px; color: #33353a; transition: border-color 0.15s, box-shadow 0.15s; }
.field::placeholder { color: #a0a2a8; }
.field:hover { border-color: #bfc2c8; }
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }
textarea.field { resize: vertical; }

.primary, .secondary { display: inline-flex; min-height: 42px; align-items: center; justify-content: center; border-radius: 10px; padding: 0 16px; font-size: 14px; font-weight: 600; transition: background 0.15s, border-color 0.15s; }
.primary { background: #c8102e; color: #fff; }
.primary:hover:not(:disabled) { background: #a10e24; }
.primary:disabled { opacity: 0.6; cursor: wait; }
.secondary { border: 1px solid #d9dbe0; background: #fff; color: #33353a; }
.secondary:hover { background: #f7f7f8; }
</style>
