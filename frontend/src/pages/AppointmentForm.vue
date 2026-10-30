<template>
	<main class="mx-auto max-w-7xl px-4 py-6 md:px-7 md:py-8">
		<!-- Breadcrumb -->
		<div class="mb-5 text-sm text-[#5B616B]">
			<router-link :to="{ name: 'Appointments' }" class="hover:text-[#A10E24]">Appointments</router-link>
			<span class="px-2">/</span><span class="font-semibold text-[#2B2F36]">{{ isNew ? 'Book an appointment' : 'Edit appointment' }}</span>
		</div>

		<PageLoader v-if="loading" />

		<template v-else>
			<!-- Page header -->
			<div class="mb-5 flex flex-wrap items-start justify-between gap-4">
				<div>
					<h1 class="text-2xl font-semibold leading-8 text-[#2B2F36]">{{ isNew ? 'Book an appointment' : 'Edit appointment' }}</h1>
					<p class="mt-1 text-sm text-[#5B616B]">
						{{ isNew ? 'Choose a client, set the time and decide how you will meet.' : 'Update the details of this session.' }}
					</p>
				</div>
				<div class="flex items-center gap-2 rounded-lg border border-[#E4E6EA] bg-white px-3 py-2 text-sm text-[#5B616B]">
					<CalendarDays :size="16" class="shrink-0" />
					{{ whenLabel || 'Date and time not set' }}
				</div>
			</div>

			<!-- Client banner -->
			<section class="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white px-5 py-4" aria-label="Client">
				<div class="text-sm text-[#2B2F36]">
					<strong class="mr-1">Client:</strong><span>{{ banner.text }}</span>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" :class="banner.pill">{{ banner.label }}</span>
			</section>

			<div class="flex items-start gap-5 max-[800px]:flex-col">
				<!-- Section navigation -->
				<nav class="w-[280px] shrink-0 rounded-xl border border-[#E4E6EA] bg-white p-5 max-[800px]:w-full" aria-label="Appointment sections">
					<div class="mb-2 text-xs text-[#5B616B]">Section {{ step }} of {{ sections.length }} · {{ Math.round((step / sections.length) * 100) }}% complete</div>
					<div class="mb-4 h-2 overflow-hidden rounded-full bg-[#E4E6EA]">
						<div class="h-full rounded-full bg-[#C8102E] transition-all" :style="{ width: `${(step / sections.length) * 100}%` }"></div>
					</div>
					<ol class="space-y-1">
						<li v-for="(section, index) in sections" :key="section.key">
							<button type="button" class="flex min-h-10 w-full items-center gap-2.5 rounded-lg px-2 text-left text-sm transition-colors"
								:class="step === index + 1 ? 'font-semibold text-[#A10E24]' : 'text-[#4A505A] hover:bg-[#F4F5F7]'"
								:aria-current="step === index + 1 ? 'step' : undefined" @click="goTo(index + 1)">
								<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
									:class="isDone(section, index) ? 'bg-[#DCF3E4] text-[#146C3A]' : step === index + 1 ? 'bg-[#C8102E] text-white' : 'bg-[#E4E6EA] text-[#3A3F47]'">
									<Check v-if="isDone(section, index)" :size="14" :stroke-width="2.5" />
									<template v-else>{{ index + 1 }}</template>
								</span>
								{{ section.title }}
							</button>
						</li>
					</ol>
				</nav>

				<!-- Section content -->
				<form class="min-w-0 flex-1 rounded-xl border border-[#E4E6EA] bg-white p-5 md:p-6" @submit.prevent="onSubmit">
					<h2 class="text-lg font-semibold text-[#2B2F36]">{{ currentSection.heading }}</h2>
					<p v-if="currentSection.description" class="mb-6 mt-1 text-sm text-[#5B616B]">{{ currentSection.description }}</p>

					<!-- 1. Client -->
					<div v-if="currentSection.key === 'client'" class="max-w-xl">
						<!-- Editing: fixed client -->
						<div v-if="!isNew" class="flex items-center gap-3 rounded-lg bg-[#F4F5F7] p-4">
							<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-semibold text-[#A10E24]">{{ initials(clientName) }}</span>
							<div class="min-w-0">
								<span class="block text-xs text-[#5B616B]">Client</span>
								<span class="mt-0.5 block truncate text-sm font-medium text-[#2B2F36]">{{ clientLabel }}</span>
							</div>
						</div>

						<!-- Booking: chosen client -->
						<div v-else-if="chosen" class="flex items-center gap-3 rounded-[10px] border border-[#C8102E] bg-[#FFF8F9] p-4">
							<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-semibold text-[#A10E24]">{{ initials(chosen.full_name) }}</span>
							<div class="min-w-0 flex-1">
								<span class="block truncate text-sm font-semibold text-[#2B2F36]">{{ chosen.full_name }}</span>
								<span class="mt-0.5 block truncate text-xs text-[#5B616B]">{{ [chosen.scholar_code, chosen.institution].filter(Boolean).join(' · ') }}</span>
							</div>
							<button v-if="!pinnedClient" type="button" class="inline-flex h-10 shrink-0 items-center rounded-[10px] px-3 text-sm font-semibold text-[#A10E24] transition hover:bg-[#FCE8EB]" @click="chosen = null">Change</button>
						</div>

						<div v-else-if="pinnedClient" class="flex items-center gap-3 rounded-[10px] border border-[#E4E6EA] bg-[#F4F5F7] p-4 text-sm text-[#5B616B]" role="status">
							<Loader2 v-if="search.loading" :size="18" class="shrink-0 animate-spin" />
							<span>{{ search.loading ? 'Loading the selected client…' : 'Could not load this client. Return to the client profile and try again.' }}</span>
						</div>

						<!-- Booking: search -->
						<div v-else>
							<label for="client-search" class="lbl">Find a client <span class="req">*</span></label>
							<div class="relative">
								<Search :size="18" class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5B616B]" />
								<input id="client-search" v-model="term" type="text" autocomplete="off" class="inp !pl-10" placeholder="Search by code, name or phone" @keydown.enter.prevent />
								<Loader2 v-if="search.loading" :size="18" class="absolute right-3.5 top-1/2 -translate-y-1/2 animate-spin text-[#5B616B]" />
							</div>

							<ul v-if="found.length" class="mt-3 space-y-2">
								<li v-for="row in found" :key="row.name">
									<button type="button" class="flex min-h-11 w-full items-center gap-3 rounded-[10px] border border-[#D5D8DE] px-3.5 py-2.5 text-left transition hover:border-[#C8102E]" @click="choose(row)">
										<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#F4F5F7] text-xs font-semibold text-[#5B616B]">{{ initials(row.full_name) }}</span>
										<span class="min-w-0">
											<span class="block truncate text-sm font-semibold text-[#2B2F36]">{{ row.full_name }}</span>
											<span class="block truncate text-xs text-[#5B616B]">{{ [row.scholar_code, row.institution].filter(Boolean).join(' · ') }}</span>
										</span>
									</button>
								</li>
							</ul>
							<p v-else-if="noMatches" class="mt-3 text-sm text-[#5B616B]">No clients match “{{ term.trim() }}”. Check the spelling or try their code or phone number.</p>
							<p v-else class="mt-3 text-sm text-[#5B616B]">Type at least two characters to search.</p>
						</div>
					</div>

					<!-- 2. Schedule -->
					<div v-else-if="currentSection.key === 'schedule'" class="max-w-xl space-y-5">
						<div>
							<span id="dt-label" class="lbl">Date and time <span class="req">*</span></span>
							<div class="relative" data-datetime-picker @keydown.enter.prevent>
								<button id="dt" type="button" class="date-control" :aria-labelledby="'dt-label dt-value'" :aria-expanded="datePickerOpen" aria-haspopup="dialog" @click="toggleDatePicker" @keydown.esc="datePickerOpen = false">
									<span class="flex min-w-0 items-center gap-2.5"><CalendarDays :size="17" class="shrink-0 text-[#A10E24]" /><span id="dt-value" class="truncate" :class="form.date_time ? 'text-[#2B2F36]' : 'text-[#6B717B]'">{{ whenLabel || 'Choose a date and time' }}</span></span>
									<ChevronDown :size="17" class="shrink-0 text-[#5B616B] transition-transform" :class="datePickerOpen ? 'rotate-180' : ''" />
								</button>
								<div v-if="datePickerOpen" class="absolute left-0 top-full z-30 mt-2 w-[min(360px,calc(100vw-3rem))] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]" role="dialog" aria-labelledby="dt-label">
									<div class="flex items-center justify-between border-b border-[#E4E6EA] px-4 py-3">
										<div><p class="text-xs text-[#5B616B]">Choose date</p><p class="mt-0.5 text-sm font-semibold text-[#2B2F36]">{{ pickerMonthLabel }}</p></div>
										<div class="flex items-center gap-1.5"><button type="button" class="picker-nav" aria-label="Previous month" @click="shiftPickerMonth(-1)"><ChevronLeft :size="17" /></button><button type="button" class="h-8 rounded-lg border border-[#E4E6EA] px-2.5 text-xs font-semibold text-[#4A505A] hover:bg-[#F4F5F7]" @click="goPickerToday">Today</button><button type="button" class="picker-nav" aria-label="Next month" @click="shiftPickerMonth(1)"><ChevronRight :size="17" /></button></div>
									</div>
									<div class="p-3.5">
										<div class="grid grid-cols-7 gap-1">
											<span v-for="day in weekdayLabels" :key="day" class="pb-1 text-center text-[11px] font-medium text-[#5B616B]">{{ day }}</span>
											<button v-for="cell in pickerCells" :key="cell.key" type="button" class="picker-day" :class="[!cell.inMonth ? 'picker-day-outside' : '', cell.key === pickerToday ? 'picker-day-today' : '', cell.key === pickerDate ? 'picker-day-selected' : '']" :aria-label="cell.label" :aria-pressed="cell.key === pickerDate" @click="chooseDate(cell.key)">{{ cell.day }}</button>
										</div>
										<div class="mt-3 flex items-center justify-between gap-3 border-t border-[#E4E6EA] pt-3">
											<span class="inline-flex items-center gap-1.5 text-xs font-semibold text-[#4A505A]"><Clock3 :size="15" class="text-[#5B616B]" /> Start time</span>
											<div class="flex shrink-0 items-center gap-1">
												<input v-model="timeHour" aria-label="Hour" type="number" min="0" max="23" inputmode="numeric" class="time-part" />
												<span class="text-sm font-semibold text-[#5B616B]">:</span>
												<input v-model="timeMinute" aria-label="Minute" type="number" min="0" max="59" step="5" inputmode="numeric" class="time-part" />
												<span class="ml-1 whitespace-nowrap text-[11px] font-medium text-[#5B616B]">24h</span>
											</div>
										</div>
									</div>
									<div class="flex items-center justify-between border-t border-[#E4E6EA] bg-[#F4F5F7]/60 px-3.5 py-3">
										<button type="button" class="text-xs font-semibold text-[#5B616B] hover:text-[#A10E24]" @click="clearDateTime">Clear</button>
										<button type="button" class="h-9 rounded-lg bg-[#C8102E] px-3.5 text-xs font-semibold text-white hover:bg-[#A10E24] disabled:cursor-not-allowed disabled:opacity-50" :disabled="!form.date_time" @click="datePickerOpen = false">Done</button>
									</div>
								</div>
							</div>
						</div>

						<div>
							<label for="dur" class="lbl">Duration (minutes)</label>
							<input id="dur" v-model="form.duration_minutes" type="number" min="5" step="5" class="inp" @keydown.enter.prevent />
							<div class="mt-2 flex flex-wrap gap-2">
								<button
									v-for="m in DURATIONS"
									:key="m"
									type="button"
									class="chip"
									:class="Number(form.duration_minutes) === m ? 'chip-on' : ''"
									:aria-pressed="Number(form.duration_minutes) === m"
									@click="form.duration_minutes = m"
								>{{ m }}</button>
							</div>
						</div>
					</div>

					<!-- 3. Session details -->
					<div v-else-if="currentSection.key === 'details'" class="max-w-xl space-y-6">
						<fieldset class="m-0 border-0 p-0">
							<legend class="lbl">Session type <span class="req">*</span></legend>
							<div class="grid gap-2 sm:grid-cols-2">
								<label v-for="o in sessionOptions" :key="o.value" class="opt" :class="form.session_type === o.value ? 'opt-on' : ''">
									<input v-model="form.session_type" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="session_type" :value="o.value" />{{ o.label }}
								</label>
							</div>
						</fieldset>

						<fieldset class="m-0 border-0 p-0">
							<legend class="lbl">Mode of contact <span class="req">*</span></legend>
							<div class="grid gap-2 sm:grid-cols-2">
								<label v-for="o in modeOptions" :key="o.value" class="opt" :class="form.mode_of_contact === o.value ? 'opt-on' : ''">
									<input v-model="form.mode_of_contact" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="mode_of_contact" :value="o.value" />{{ o.label }}
								</label>
							</div>
						</fieldset>

						<div v-if="physical">
							<label for="loc" class="lbl">Physical location</label>
							<div class="relative">
								<MapPin :size="18" class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5B616B]" />
								<input id="loc" v-model="form.location" type="text" class="inp !pl-10" placeholder="e.g. Counselling room, Main campus" @keydown.enter.prevent />
							</div>
						</div>
					</div>

					<!-- 4. Notes -->
					<div v-else-if="currentSection.key === 'notes'" class="max-w-xl">
						<label for="notes" class="lbl">Notes <span class="font-normal text-[#5B616B]">(optional)</span></label>
						<textarea id="notes" v-model="form.notes" rows="6" class="inp"></textarea>
					</div>

					<!-- 5. Review -->
					<div v-else class="grid gap-4 sm:grid-cols-2">
						<div v-for="[label, value, wide] in summary" :key="label" class="rounded-lg bg-[#F4F5F7] p-4" :class="wide ? 'sm:col-span-2' : ''">
							<span class="block text-xs text-[#5B616B]">{{ label }}</span>
							<span class="review-value mt-1 block text-sm font-medium text-[#2B2F36]">{{ value || 'Not set' }}</span>
						</div>
					</div>

					<p v-if="formError" class="mt-5 text-sm text-[#A10E24]" role="alert">{{ formError }}</p>
					<ErrorMessage class="mt-5" :message="saver.error" />

					<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E4E6EA] pt-5">
						<Button type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#2B2F36]" :disabled="step === 1" @click="previous">Previous</Button>
						<Button type="submit" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="saver.loading">
							{{ step === sections.length ? (isNew ? 'Book appointment' : 'Save changes') : 'Next' }}
						</Button>
					</div>
				</form>
			</div>
		</template>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, onUnmounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { CalendarDays, Check, ChevronDown, ChevronLeft, ChevronRight, Clock3, Loader2, MapPin, Search } from "lucide-vue-next"
import { fromInput, toInput } from "../data/format"
import { MODES, PHYSICAL_MODES, SESSION_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const apptName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !apptName.value)

const DURATIONS = [30, 45, 60, 90]
const form = reactive({ date_time: "", duration_minutes: 60, session_type: route.query.type === "Follow-Up" ? "Follow-Up" : "", mode_of_contact: "", location: "", notes: "" })
const physical = computed(() => PHYSICAL_MODES.includes(form.mode_of_contact))
const datePickerOpen = ref(false)
const localISO = (date) => new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const pickerToday = localISO(new Date())
const pickerMonth = ref(`${pickerToday.slice(0, 7)}-01`)
const weekdayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const loading = ref(false)
const clientLabel = ref("")
const clientId = ref("")
const pinnedClient = computed(() => isNew.value && Boolean(route.query.client))

// Options may be plain strings or { label, value } objects
const asOptions = (list) => (list || []).map((o) => (typeof o === "string" ? { label: o, value: o } : { label: o.label ?? o.value, value: o.value ?? o.label }))
const sessionOptions = computed(() => asOptions(SESSION_TYPES))
const modeOptions = computed(() => asOptions(MODES).filter((option) => option.value))
const pickerDate = computed(() => form.date_time?.slice(0, 10) || "")
const pickerTime = computed(() => form.date_time?.slice(11, 16) || "")
const pickerMonthLabel = computed(() => new Date(`${pickerMonth.value}T00:00:00`).toLocaleDateString("en-GB", { month: "long", year: "numeric" }))
const pickerCells = computed(() => {
	const first = new Date(`${pickerMonth.value}T00:00:00`)
	const offset = (first.getDay() + 6) % 7
	const start = shiftDate(pickerMonth.value, -offset)
	return Array.from({ length: 42 }, (_, index) => {
		const key = shiftDate(start, index)
		const date = new Date(`${key}T00:00:00`)
		return {
			key,
			day: date.getDate(),
			label: date.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" }),
			inMonth: key.slice(0, 7) === pickerMonth.value.slice(0, 7),
		}
	})
})
const timeHour = computed({
	get: () => pickerTime.value ? pickerTime.value.slice(0, 2) : "09",
	set: (value) => setTimePart("hour", value),
})
const timeMinute = computed({
	get: () => pickerTime.value ? pickerTime.value.slice(3, 5) : "00",
	set: (value) => setTimePart("minute", value),
})

function shiftDate(value, amount) {
	const date = new Date(`${value}T00:00:00`)
	date.setDate(date.getDate() + amount)
	return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
}
function shiftPickerMonth(amount) {
	const date = new Date(`${pickerMonth.value}T00:00:00`)
	date.setMonth(date.getMonth() + amount)
	pickerMonth.value = `${localISO(date).slice(0, 7)}-01`
}
function toggleDatePicker() {
	if (!datePickerOpen.value) {
		pickerMonth.value = `${(pickerDate.value || pickerToday).slice(0, 7)}-01`
	}
	datePickerOpen.value = !datePickerOpen.value
}
function chooseDate(value) {
	const time = pickerTime.value || "09:00"
	form.date_time = `${value}T${time}`
}
function goPickerToday() {
	pickerMonth.value = `${pickerToday.slice(0, 7)}-01`
	chooseDate(pickerToday)
}
function setTimePart(part, value) {
	const date = pickerDate.value || pickerToday
	const [oldHour = "09", oldMinute = "00"] = pickerTime.value.split(":")
	const parsed = Number.parseInt(value, 10)
	const limit = part === "hour" ? 23 : 59
	const bounded = Number.isNaN(parsed) ? 0 : Math.max(0, Math.min(limit, parsed))
	const hour = part === "hour" ? String(bounded).padStart(2, "0") : oldHour
	const minute = part === "minute" ? String(bounded).padStart(2, "0") : oldMinute
	form.date_time = `${date}T${hour}:${minute}`
}
function clearDateTime() {
	form.date_time = ""
	datePickerOpen.value = false
}
function closeDatePicker(event) {
	if (!event.target.closest("[data-datetime-picker]")) datePickerOpen.value = false
}

const initials = (full) => (full || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()
const clientName = computed(() => clientLabel.value.split(" (")[0])

// Choosing a client when booking
const term = ref("")
const chosen = ref(null)
const found = ref([])
const search = createResource({
	url: "krcti_mhpss.api.counsellor.search_clients",
	onSuccess(rows) {
		found.value = rows
	},
})
const noMatches = computed(() => !!search.data && !search.loading && !found.value.length && term.value.trim().length >= 2)
let timer = null
watch(term, (value) => {
	clearTimeout(timer)
	if (chosen.value || value.trim().length < 2) return (found.value = [])
	timer = setTimeout(() => search.submit({ term: value.trim() }), 300)
})
onBeforeUnmount(() => clearTimeout(timer))
function choose(row) {
	chosen.value = row
	clientId.value = row.name
	found.value = []
}

// Editing
const existing = createResource({
	url: "krcti_mhpss.api.records.appointment_detail",
	onSuccess(doc) {
		clientId.value = doc.client_id
		clientLabel.value = `${doc.client_name} (${doc.scholar_code})`
		Object.assign(form, {
			date_time: toInput(doc.date_time), duration_minutes: doc.duration_minutes, session_type: doc.session_type,
			mode_of_contact: doc.mode_of_contact, location: doc.location || "", notes: doc.notes || "",
		})
		loading.value = false
	},
})

onMounted(() => {
	if (!isNew.value) {
		loading.value = true
		existing.submit({ name: apptName.value })
	} else if (route.query.client) {
		search.submit({ term: String(route.query.client) })
		const stop = watch(found, (rows) => {
			const match = rows.find((r) => r.name === route.query.client)
			if (match) {
				choose(match)
				stop()
			}
		})
	}
})
onMounted(() => document.addEventListener("click", closeDatePicker))
onUnmounted(() => document.removeEventListener("click", closeDatePicker))

const toValues = () => ({
	date_time: fromInput(form.date_time),
	duration_minutes: Number(form.duration_minutes) || 60,
	session_type: form.session_type,
	mode_of_contact: form.mode_of_contact,
	location: physical.value ? form.location : "",
	notes: form.notes,
})

const saver = createResource({
	url: "krcti_mhpss.api.records.save_appointment",
	onSuccess() {
		router.replace({ name: "Appointments" })
	},
})
const canSubmit = computed(() => !!(clientId.value && form.date_time && form.session_type && form.mode_of_contact))

function save() {
	if (!canSubmit.value) return
	saver.submit({ name: apptName.value || undefined, client: clientId.value, data: toValues() })
}

// ---- Wizard ----
const step = ref(1)
const formError = ref("")
const visited = ref(new Set([1]))

const sections = computed(() => [
	{ key: "client", title: "Client", heading: "Client", description: isNew.value ? "Choose the client this session is for." : "The client cannot be changed once booked." },
	{ key: "schedule", title: "Schedule", heading: "Section 2: Schedule", description: "Set when the session starts and how long it runs." },
	{ key: "details", title: "Session details", heading: "Section 3: Session details", description: "Choose the kind of session and how you will meet." },
	{ key: "notes", title: "Notes", heading: "Section 4: Notes", description: "Anything to remember before the session. This is optional." },
	{ key: "review", title: "Review", heading: "Section 5: Review and confirm", description: `Check these details, then ${isNew.value ? "book the appointment" : "save your changes"}.` },
])
const currentSection = computed(() => sections.value[step.value - 1])

const complete = (key) => {
	if (key === "client") return !!clientId.value
	if (key === "schedule") return !!form.date_time
	if (key === "details") return !!(form.session_type && form.mode_of_contact)
	return true
}
const isDone = (section, index) => {
	const n = index + 1
	if (n === step.value || section.key === "review") return false
	return (visited.value.has(n) || !isNew.value) && complete(section.key)
}

watch(step, (value) => {
	visited.value = new Set([...visited.value, value])
	formError.value = ""
	datePickerOpen.value = false
})

function goTo(target) {
	step.value = target
}
function next() {
	if (step.value < sections.value.length) step.value += 1
}
function previous() {
	if (step.value > 1) step.value -= 1
}
function onSubmit() {
	if (step.value < sections.value.length) return next()
	submit()
}
function submit() {
	formError.value = ""
	const missing = sections.value.findIndex((section) => !complete(section.key))
	if (missing !== -1) {
		step.value = missing + 1
		formError.value = {
			client: "Choose a client before saving.",
			schedule: "Choose a date and time before saving.",
			details: "Choose a session type and mode of contact before saving.",
		}[sections.value[missing].key]
		return
	}
	save()
}

// ---- Display helpers ----
const whenLabel = computed(() => {
	if (!form.date_time) return ""
	const d = new Date(form.date_time)
	return Number.isNaN(d.getTime())
		? ""
		: d.toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
})
const clientDisplay = computed(() => (isNew.value ? chosen.value?.full_name : clientLabel.value))
const sessionTypeLabel = computed(() => sessionOptions.value.find((o) => o.value === form.session_type)?.label || form.session_type)
const modeLabel = computed(() => modeOptions.value.find((o) => o.value === form.mode_of_contact)?.label || form.mode_of_contact)

const summary = computed(() => [
	["Client", clientDisplay.value],
	["When", whenLabel.value],
	["Duration", form.duration_minutes ? `${Number(form.duration_minutes) || 60} minutes` : ""],
	["Session type", sessionTypeLabel.value],
	["Mode of contact", modeLabel.value],
	...(physical.value ? [["Location", form.location]] : []),
	...(form.notes ? [["Notes", form.notes, true]] : []),
])

const TONES = {
	green: "bg-[#DCF3E4] text-[#146C3A]",
	amber: "bg-[#FDECC8] text-[#8A4B00]",
	gray: "bg-[#E4E6EA] text-[#3A3F47]",
}
const banner = computed(() => {
	if (!isNew.value) return { text: `${clientLabel.value || "This client"}. The client cannot be changed once booked.`, label: "Client fixed", pill: TONES.gray }
	if (chosen.value) return { text: [chosen.value.full_name, chosen.value.scholar_code].filter(Boolean).join(" · "), label: "Client selected", pill: TONES.green }
	return { text: "Choose the client this session is for.", label: "Client needed", pill: TONES.amber }
})
</script>

<style scoped>
/* No font-family is set here: the page inherits the app font, like the baseline survey. */

.lbl { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; line-height: 20px; color: #2b2f36; }
.req { color: #a10e24; }

.inp { display: block; width: 100%; height: 44px; border: 1px solid #d5d8de; border-radius: 10px; background: #fff; padding: 0 12px; font-family: inherit; font-size: 14px; color: #2b2f36; transition: border-color 0.15s, box-shadow 0.15s; }
.inp::placeholder { color: #6b717b; }
.inp:hover { border-color: #b5bac3; }
.inp:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }
textarea.inp { height: auto; min-height: 120px; padding: 10px 12px; line-height: 20px; resize: vertical; }

.date-control { display: flex; width: 100%; height: 44px; align-items: center; justify-content: space-between; gap: 12px; border: 1px solid #d5d8de; border-radius: 10px; background: #fff; padding: 0 12px; font-family: inherit; font-size: 14px; text-align: left; transition: border-color 0.15s, box-shadow 0.15s; }
.date-control:hover { border-color: #b5bac3; }
.date-control:focus-visible { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }

/* Radio option cards (same pattern as the baseline survey) */
.opt { display: flex; min-height: 44px; cursor: pointer; align-items: center; gap: 12px; border: 1px solid #d5d8de; border-radius: 10px; background: #fff; padding: 0 14px; font-size: 14px; color: #2b2f36; transition: border-color 0.15s, background 0.15s; }
.opt:hover { border-color: #c8102e; }
.opt-on { border-color: #c8102e; background: #fff8f9; }

/* Date picker */
.picker-nav { display: inline-flex; height: 32px; width: 32px; align-items: center; justify-content: center; border: 1px solid #e4e6ea; border-radius: 8px; background: #fff; color: #4a505a; transition: background 0.15s; }
.picker-nav:hover { background: #f4f5f7; }
.picker-day { display: grid; height: 34px; width: 34px; place-items: center; justify-self: center; border: 1px solid transparent; border-radius: 8px; color: #2b2f36; font-size: 12px; font-weight: 600; transition: background 0.15s, color 0.15s; }
.picker-day:hover { background: #f4f5f7; }
.picker-day-outside { color: #b5bac3; }
.picker-day-today { border-color: #f3c3cb; color: #a10e24; }
.picker-day-selected, .picker-day-selected:hover { border-color: #c8102e; background: #c8102e; color: #fff; }
.time-part { box-sizing: border-box; width: 48px; min-width: 48px; height: 34px; border: 1px solid #d5d8de; border-radius: 8px; background: #fff; padding: 0 2px; text-align: center; font-family: inherit; font-size: 14px; font-weight: 600; font-variant-numeric: tabular-nums; color: #2b2f36; }
.time-part:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.12); }
.time-part::-webkit-inner-spin-button, .time-part::-webkit-outer-spin-button { margin: 0; appearance: none; }

/* Duration chips */
.chip { display: inline-flex; height: 36px; align-items: center; border: 1px solid #d5d8de; border-radius: 18px; background: #fff; padding: 0 14px; font-size: 13px; font-weight: 600; color: #2b2f36; transition: background 0.15s, border-color 0.15s; }
.chip:hover { background: #f4f5f7; }
.chip:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.4); }
.chip-on, .chip-on:hover { border-color: #c8102e; background: #fce8eb; color: #a10e24; }

.review-value { white-space: pre-line; overflow-wrap: anywhere; }
</style>
