<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1100px]">
      <router-link
        :to="{ name: 'Appointments' }"
        class="inline-flex h-11 items-center gap-2 rounded-[10px] pr-3 text-sm font-medium text-[#5B616B] transition hover:text-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
      >
        <ArrowLeft :size="18" /> Back to appointments
      </router-link>

      <div class="mt-1">
        <h1 class="text-2xl font-semibold leading-8">{{ isNew ? "Book an appointment" : "Edit appointment" }}</h1>
        <p class="mt-0.5 text-[13px] text-[#5B616B]">
          {{ isNew ? "Choose a client, set the time and decide how you will meet." : "Update the details of this session." }}
        </p>
      </div>

      <PageLoader v-if="loading" />

      <div v-else class="mt-6 grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <form class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white" @submit.prevent="save">
          <!-- Client -->
          <section class="px-5 py-6 sm:px-6">
            <h2 class="text-lg font-semibold leading-6">Client</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">{{ isNew ? "Who is this session for?" : "The client cannot be changed once booked." }}</p>

            <div class="mt-4">
              <!-- Editing: fixed client -->
              <div v-if="!isNew" class="flex items-center gap-3 rounded-[10px] border border-[#E4E6EA] bg-[#F4F5F7] px-4 py-3">
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-semibold text-[#A10E24]">{{ initials(clientName) }}</span>
                <p class="min-w-0 truncate text-[15px] font-semibold">{{ clientLabel }}</p>
              </div>

              <!-- Booking: chosen client -->
              <div v-else-if="chosen" class="flex items-center gap-3 rounded-[10px] border border-[#C8102E]/30 bg-[#FCE8EB]/50 px-4 py-3">
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-semibold text-[#A10E24]">{{ initials(chosen.full_name) }}</span>
                <div class="min-w-0 flex-1">
                  <p class="truncate text-[15px] font-semibold">{{ chosen.full_name }}</p>
                  <p class="truncate text-[13px] text-[#5B616B]">{{ [chosen.scholar_code, chosen.institution].filter(Boolean).join(" · ") }}</p>
                </div>
                <button type="button" class="inline-flex h-10 shrink-0 items-center rounded-[10px] px-3 text-sm font-semibold text-[#A10E24] transition hover:bg-[#FCE8EB] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" @click="chosen = null">Change</button>
              </div>

              <!-- Booking: search -->
              <div v-else>
                <label for="client-search" class="lbl">Find a client <span class="text-[#A10E24]">*</span></label>
                <div class="relative">
                  <Search :size="18" class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5B616B]" />
                  <input id="client-search" v-model="term" type="text" autocomplete="off" class="inp !pl-10" placeholder="Search by code, name or phone" />
                  <Loader2 v-if="search.loading" :size="18" class="absolute right-3.5 top-1/2 -translate-y-1/2 animate-spin text-[#5B616B]" />
                </div>

                <ul v-if="found.length" class="mt-2 divide-y divide-[#E4E6EA] overflow-hidden rounded-[10px] border border-[#E4E6EA]">
                  <li v-for="row in found" :key="row.name">
                    <button type="button" class="flex w-full items-center gap-3 px-3.5 py-3 text-left transition hover:bg-[#F4F5F7] focus-visible:bg-[#F4F5F7] focus-visible:outline-none" @click="choose(row)">
                      <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#F4F5F7] text-[13px] font-semibold text-[#5B616B]">{{ initials(row.full_name) }}</span>
                      <span class="min-w-0">
                        <span class="block truncate text-sm font-semibold">{{ row.full_name }}</span>
                        <span class="block truncate text-[13px] text-[#5B616B]">{{ [row.scholar_code, row.institution].filter(Boolean).join(" · ") }}</span>
                      </span>
                    </button>
                  </li>
                </ul>
                <p v-else-if="noMatches" class="mt-2 text-[13px] text-[#5B616B]">No clients match “{{ term.trim() }}”. Check the spelling or try their code or phone number.</p>
                <p v-else class="mt-2 text-[13px] text-[#5B616B]">Type at least two characters to search.</p>
              </div>
            </div>
          </section>

          <!-- Schedule -->
          <section class="border-t border-[#E4E6EA] px-5 py-6 sm:px-6">
            <h2 class="text-lg font-semibold leading-6">Schedule</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">When the session starts and how long it runs.</p>

            <div class="mt-4 grid gap-5 sm:grid-cols-2">
              <div>
                <span id="dt-label" class="lbl">Date and time <span class="text-[#A10E24]">*</span></span>
                <div class="relative" data-datetime-picker>
                  <button id="dt" type="button" class="date-control" :aria-labelledby="'dt-label dt-value'" :aria-expanded="datePickerOpen" aria-haspopup="dialog" @click="toggleDatePicker" @keydown.esc="datePickerOpen = false">
                    <span class="flex min-w-0 items-center gap-2.5"><CalendarDays :size="17" class="shrink-0 text-[#A10E24]" /><span id="dt-value" class="truncate" :class="form.date_time ? 'text-[#2B2F36]' : 'text-[#777C85]'">{{ whenLabel || 'Choose a date and time' }}</span></span>
                    <ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="datePickerOpen ? 'rotate-180' : ''" />
                  </button>
                  <div v-if="datePickerOpen" class="absolute left-0 top-full z-30 mt-2 w-[min(360px,calc(100vw-3rem))] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]" role="dialog" aria-labelledby="dt-label">
                    <div class="flex items-center justify-between border-b border-[#ECEDEF] px-4 py-3">
                      <div><p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#92949A]">Choose date</p><p class="mt-0.5 text-sm font-semibold text-[#25272B]">{{ pickerMonthLabel }}</p></div>
                      <div class="flex items-center gap-1.5"><button type="button" class="picker-nav" aria-label="Previous month" @click="shiftPickerMonth(-1)"><ChevronLeft :size="17" /></button><button type="button" class="rounded-lg border border-[#E4E6EA] px-2.5 py-1.5 text-xs font-semibold text-[#555860] hover:bg-[#F7F7F8]" @click="goPickerToday">Today</button><button type="button" class="picker-nav" aria-label="Next month" @click="shiftPickerMonth(1)"><ChevronRight :size="17" /></button></div>
                    </div>
                    <div class="p-3.5">
                      <div class="grid grid-cols-7 gap-1">
                        <span v-for="day in weekdayLabels" :key="day" class="pb-1 text-center text-[10px] font-semibold uppercase text-[#92949A]">{{ day }}</span>
                        <button v-for="cell in pickerCells" :key="cell.key" type="button" class="picker-day" :class="[!cell.inMonth ? 'picker-day-outside' : '', cell.key === pickerToday ? 'picker-day-today' : '', cell.key === pickerDate ? 'picker-day-selected' : '']" :aria-label="cell.label" :aria-pressed="cell.key === pickerDate" @click="chooseDate(cell.key)">{{ cell.day }}</button>
                      </div>
                      <div class="mt-3 flex items-center justify-between gap-3 border-t border-[#F0F1F3] pt-3">
                        <span class="inline-flex items-center gap-1.5 text-xs font-semibold text-[#555860]"><Clock3 :size="15" class="text-[#92949A]" /> Start time</span>
                        <div class="flex shrink-0 items-center gap-1">
                          <input v-model="timeHour" aria-label="Hour" type="number" min="0" max="23" inputmode="numeric" class="time-part" />
                          <span class="text-sm font-semibold text-[#858891]">:</span>
                          <input v-model="timeMinute" aria-label="Minute" type="number" min="0" max="59" step="5" inputmode="numeric" class="time-part" />
                          <span class="ml-1 whitespace-nowrap text-[10px] font-semibold uppercase tracking-wide text-[#92949A]">24h</span>
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center justify-between border-t border-[#ECEDEF] bg-[#FAFAFB] px-3.5 py-3">
                      <button type="button" class="text-xs font-semibold text-[#737780] hover:text-[#A10E24]" @click="clearDateTime">Clear</button>
                      <button type="button" class="rounded-lg bg-[#C8102E] px-3.5 py-2 text-xs font-semibold text-white hover:bg-[#A10E24] disabled:cursor-not-allowed disabled:opacity-50" :disabled="!form.date_time" @click="datePickerOpen = false">Done</button>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <label for="dur" class="lbl">Duration (minutes)</label>
                <input id="dur" v-model="form.duration_minutes" type="number" min="5" step="5" class="inp" />
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
          </section>

          <!-- Session details -->
          <section class="border-t border-[#E4E6EA] px-5 py-6 sm:px-6">
            <h2 class="text-lg font-semibold leading-6">Session details</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">The kind of session and how you will meet.</p>

            <div class="mt-4 space-y-5">
              <div class="sm:max-w-sm">
                <label id="stype-label" class="lbl">Session type <span class="text-[#A10E24]">*</span></label>
                <div class="relative" data-session-type-menu>
                  <button id="stype" type="button" class="inp flex items-center justify-between text-left focus:border-[#C8102E] focus:outline-none focus:ring-2 focus:ring-[#C8102E]/10" :aria-labelledby="'stype-label stype-value'" :aria-expanded="sessionTypeOpen" aria-haspopup="listbox" @click="sessionTypeOpen = !sessionTypeOpen" @keydown.esc="sessionTypeOpen = false">
                    <span id="stype-value" :class="form.session_type ? 'text-[#2B2F36]' : 'text-[#777C85]'">{{ selectedSessionType?.label || 'Select a session type' }}</span>
                    <ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="sessionTypeOpen ? 'rotate-180' : ''" />
                  </button>
                  <div v-if="sessionTypeOpen" class="absolute left-0 right-0 z-20 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-labelledby="stype-label">
                    <button v-for="o in sessionOptions" :key="o.value" type="button" role="option" :aria-selected="form.session_type === o.value" class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition" :class="form.session_type === o.value ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click="selectSessionType(o.value)">
                      {{ o.label }}
                      <Check v-if="form.session_type === o.value" :size="16" class="text-[#C8102E]" />
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <p id="mode-label" class="lbl">Mode of contact <span class="text-[#A10E24]">*</span></p>
                <div class="flex flex-wrap gap-2" role="radiogroup" aria-labelledby="mode-label">
                  <button
                    v-for="o in modeOptions"
                    :key="o.value"
                    type="button"
                    role="radio"
                    class="chip chip-lg"
                    :class="form.mode_of_contact === o.value ? 'chip-on' : ''"
                    :aria-checked="form.mode_of_contact === o.value"
                    @click="form.mode_of_contact = o.value"
                  >
                    <Check v-if="form.mode_of_contact === o.value" :size="16" /> {{ o.label }}
                  </button>
                </div>
              </div>

              <div v-if="physical" class="sm:max-w-md">
                <label for="loc" class="lbl">Physical location</label>
                <div class="relative">
                  <MapPin :size="18" class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#5B616B]" />
                  <input id="loc" v-model="form.location" type="text" class="inp !pl-10" placeholder="e.g. Counselling room, Main campus" />
                </div>
              </div>
            </div>
          </section>

          <!-- Notes -->
          <section class="border-t border-[#E4E6EA] px-5 py-6 sm:px-6">
            <label for="notes" class="text-lg font-semibold leading-6">Notes <span class="text-sm font-normal text-[#5B616B]">(optional)</span></label>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">Anything to remember before the session.</p>
            <textarea id="notes" v-model="form.notes" rows="4" class="inp mt-4"></textarea>
          </section>

          <!-- Actions -->
          <div class="border-t border-[#E4E6EA] bg-[#F4F5F7]/60 px-5 py-4 sm:px-6">
            <ErrorMessage class="mb-3" :message="saver.error || updater.error" />
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="max-w-sm text-[13px] leading-[18px] text-[#5B616B]">
                <template v-if="!canSubmit">Choose a client, date and time, session type and mode of contact to continue.</template>
              </p>
              <div class="flex gap-2.5">
                <router-link
                  :to="{ name: 'Appointments' }"
                  class="inline-flex h-11 items-center rounded-[10px] border border-[#D5D8DE] bg-white px-[18px] text-sm font-semibold transition hover:bg-[#F4F5F7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
                >Cancel</router-link>
                <button
                  type="submit"
                  class="inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#C8102E] bg-[#C8102E] px-[18px] text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:border-[#E4E6EA] disabled:bg-[#E4E6EA] disabled:text-[#5B616B]"
                  :disabled="busy || !canSubmit"
                >
                  <Loader2 v-if="busy" :size="18" class="animate-spin" />
                  {{ isNew ? "Book appointment" : "Save changes" }}
                </button>
              </div>
            </div>
          </div>
        </form>

        <!-- Live summary -->
        <aside class="hidden rounded-xl border border-[#E4E6EA] bg-white lg:sticky lg:top-6 lg:block" aria-label="Appointment summary">
          <div class="border-b border-[#E4E6EA] px-5 py-4">
            <h2 class="text-lg font-semibold leading-6">Summary</h2>
            <p class="mt-0.5 text-[13px] text-[#5B616B]">Check this before you save</p>
          </div>
          <dl class="px-5 py-1">
            <div v-for="row in summary" :key="row.label" class="border-b border-[#E4E6EA] py-3.5 last:border-b-0">
              <dt class="text-[13px] text-[#5B616B]">{{ row.label }}</dt>
              <dd class="mt-0.5 break-words text-sm leading-5">
                <span v-if="row.value" class="font-semibold">{{ row.value }}</span>
                <span v-else class="italic text-[#6B717B]">Not set</span>
              </dd>
            </div>
          </dl>
        </aside>
      </div>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, onUnmounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, CalendarDays, Check, ChevronDown, ChevronLeft, ChevronRight, Clock3, Loader2, MapPin, Search } from "lucide-vue-next"
import { fromInput, toInput } from "../data/format"
import { MODES, PHYSICAL_MODES, SESSION_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const apptName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !apptName.value)

const DURATIONS = [30, 45, 60, 90]
const form = reactive({ date_time: "", duration_minutes: 60, session_type: "", mode_of_contact: "", location: "", notes: "" })
const physical = computed(() => PHYSICAL_MODES.includes(form.mode_of_contact))
const sessionTypeOpen = ref(false)
const datePickerOpen = ref(false)
const localISO = (date) => new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const pickerToday = localISO(new Date())
const pickerMonth = ref(`${pickerToday.slice(0, 7)}-01`)
const weekdayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const loading = ref(false)
const clientLabel = ref("")
const clientId = ref("")

// Options may be plain strings or { label, value } objects
const asOptions = (list) => (list || []).map((o) => (typeof o === "string" ? { label: o, value: o } : { label: o.label ?? o.value, value: o.value ?? o.label }))
const sessionOptions = computed(() => asOptions(SESSION_TYPES))
const modeOptions = computed(() => asOptions(MODES))
const selectedSessionType = computed(() => sessionOptions.value.find((option) => option.value === form.session_type))
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

function selectSessionType(value) {
	form.session_type = value
	sessionTypeOpen.value = false
}

function closeSessionTypeMenu(event) {
	if (!event.target.closest("[data-session-type-menu]")) sessionTypeOpen.value = false
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
onMounted(() => document.addEventListener("click", closeSessionTypeMenu))
onUnmounted(() => document.removeEventListener("click", closeSessionTypeMenu))
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
const updater = saver // the template may still mention it
const busy = computed(() => saver.loading || updater.loading)
const canSubmit = computed(() => !!(clientId.value && form.date_time && form.session_type && form.mode_of_contact))

function save() {
	if (!canSubmit.value) return
	saver.submit({ name: apptName.value || undefined, client: clientId.value, data: toValues() })
}

// Live summary
const whenLabel = computed(() => {
	if (!form.date_time) return ""
	const d = new Date(form.date_time)
	return Number.isNaN(d.getTime())
		? ""
		: d.toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
})
const summary = computed(() => [
	{ label: "Client", value: isNew.value ? chosen.value?.full_name : clientLabel.value },
	{ label: "When", value: whenLabel.value },
	{ label: "Duration", value: form.duration_minutes ? `${Number(form.duration_minutes) || 60} minutes` : "" },
	{ label: "Session type", value: form.session_type },
	{ label: "Mode of contact", value: form.mode_of_contact },
	...(physical.value ? [{ label: "Location", value: form.location }] : []),
])
</script>

<style scoped>
.lbl {
	display: block;
	margin-bottom: 6px;
	font-size: 14px;
	font-weight: 500;
	line-height: 20px;
}
.inp {
	display: block;
	width: 100%;
	height: 44px;
	border: 1px solid #d5d8de;
	border-radius: 10px;
	background: #fff;
	padding: 0 12px;
	font: 14px Inter, system-ui, sans-serif;
	color: #2b2f36;
	transition: border-color 0.15s, box-shadow 0.15s;
}
.inp::placeholder { color: #6b717b; }
.inp:hover { border-color: #b9bdc5; }
.inp:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.15); }
.date-control {
	display: flex;
	width: 100%;
	height: 44px;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	border: 1px solid #d5d8de;
	border-radius: 10px;
	background: #fff;
	padding: 0 12px;
	font: 14px Inter, system-ui, sans-serif;
	text-align: left;
	transition: border-color .15s, box-shadow .15s;
}
.date-control:hover { border-color: #b9bdc5; }
.date-control:focus-visible { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, .15); }
.picker-nav {
	display: inline-flex;
	height: 32px;
	width: 32px;
	align-items: center;
	justify-content: center;
	border: 1px solid #e4e6ea;
	border-radius: 9px;
	background: #fff;
	color: #555860;
	transition: background .15s, border-color .15s;
}
.picker-nav:hover { border-color: #d5d8de; background: #f7f7f8; }
.picker-day {
	display: grid;
	height: 34px;
	width: 34px;
	place-items: center;
	justify-self: center;
	border: 1px solid transparent;
	border-radius: 9px;
	color: #3c3f45;
	font-size: 12px;
	font-weight: 600;
	transition: background .15s, border-color .15s, color .15s;
}
.picker-day:hover { background: #f7f7f8; }
.picker-day-outside { color: #c2c4c9; }
.picker-day-today { border-color: #f3c3cb; color: #a10e24; }
.picker-day-selected { border-color: #c8102e; background: #c8102e; color: white; }
.picker-day-selected:hover { background: #a10e24; }
.time-part {
	box-sizing: border-box;
	width: 48px;
	min-width: 48px;
	height: 34px;
	border: 1px solid #d9dbe0;
	border-radius: 8px;
	background: white;
	text-align: center;
	padding: 0 2px;
	font-size: 14px;
	font-weight: 600;
	font-variant-numeric: tabular-nums;
	color: #33353a;
}
.time-part:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 2px rgba(200, 16, 46, .12); }
.time-part::-webkit-inner-spin-button, .time-part::-webkit-outer-spin-button { margin: 0; appearance: none; }
textarea.inp { height: auto; min-height: 112px; padding: 10px 12px; line-height: 20px; resize: vertical; }

.chip {
	display: inline-flex;
	height: 36px;
	align-items: center;
	gap: 6px;
	border-radius: 18px;
	border: 1px solid #d5d8de;
	background: #fff;
	padding: 0 14px;
	font-size: 13px;
	font-weight: 600;
	color: #2b2f36;
	transition: background 0.15s, border-color 0.15s;
}
.chip:hover { background: #f4f5f7; }
.chip:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.4); }
.chip-lg { height: 44px; border-radius: 10px; padding: 0 18px; font-size: 14px; }
.chip-on, .chip-on:hover { border-color: #c8102e; background: #fce8eb; color: #a10e24; }
</style>
