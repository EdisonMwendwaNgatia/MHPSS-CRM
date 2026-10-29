<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1200px]">
      <!-- Page header -->
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold leading-8">Appointments</h1>
          <p class="mt-0.5 text-[13px] text-[#5B616B]">Your sessions for the selected date range, grouped by day</p>
        </div>
        <router-link
          :to="{ name: 'AppointmentNew' }"
          class="inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#C8102E] bg-[#C8102E] px-[18px] text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40 focus-visible:ring-offset-2"
        >
          <CalendarPlus :size="18" /> Book an appointment
        </router-link>
      </div>

      <!-- Overdue alert -->
      <div v-if="data?.overdue_total" class="mt-5 flex items-start gap-3 rounded-xl bg-[#FBE0E4] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
        <AlertCircle :size="20" class="mt-px shrink-0" />
        <p>
          <span class="font-semibold">{{ data.overdue_total }} appointment{{ data.overdue_total === 1 ? " has" : "s have" }} passed without being completed.</span>
          Complete or cancel {{ data.overdue_total === 1 ? "it" : "them" }} to keep your records up to date.
        </p>
      </div>

      <!-- Summary for this period -->
      <section v-if="data" class="mt-5 grid grid-cols-2 gap-4 lg:grid-cols-4" aria-label="Summary for this period">
        <button v-for="t in tiles" :key="t.filter" type="button" class="flex items-center gap-3.5 rounded-xl border bg-white p-4 text-left transition hover:-translate-y-0.5 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" :class="activeFilter === t.filter ? 'border-[#C8102E] ring-1 ring-[#C8102E]/20' : 'border-[#E4E6EA]'" :aria-pressed="activeFilter === t.filter" @click="activeFilter = t.filter">
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px]" :class="t.tile"><component :is="t.icon" :size="20" /></span>
          <div class="min-w-0">
            <p class="truncate text-[13px] text-[#5B616B]">{{ t.label }}</p>
            <p class="text-[28px] font-semibold leading-[34px]">{{ t.value }}</p>
          </div>
        </button>
      </section>

      <!-- Date range -->
      <section class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-4 sm:p-5" aria-label="Appointment date range">
        <div class="flex flex-wrap items-end gap-x-4 gap-y-4">
          <div class="w-full sm:w-44">
            <label for="appointments-from" class="text-sm font-medium">From</label>
            <input id="appointments-from" v-model="from" type="date" :max="to" class="range-field mt-1.5" :class="invalidRange ? 'range-field-error' : ''" :aria-invalid="invalidRange" />
          </div>
          <div class="w-full sm:w-44">
            <label for="appointments-to" class="text-sm font-medium">To</label>
            <input id="appointments-to" v-model="to" type="date" :min="from" class="range-field mt-1.5" :class="invalidRange ? 'range-field-error' : ''" :aria-invalid="invalidRange" />
          </div>
          <div class="flex flex-wrap gap-2 sm:ml-auto" role="group" aria-label="Quick appointment ranges">
            <button v-for="preset in presets" :key="preset.label" type="button" class="range-preset" :class="isActivePreset(preset) ? 'range-preset-active' : ''" :aria-pressed="isActivePreset(preset)" @click="applyPreset(preset)">{{ preset.label }}</button>
          </div>
          <button type="button" data-calendar-toggle class="inline-flex h-11 shrink-0 items-center gap-2 rounded-[10px] border border-[#D5D8DE] bg-white px-4 text-sm font-semibold transition hover:bg-[#F4F5F7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" :aria-expanded="calendarOpen" @click="toggleCalendar">
            <CalendarDays :size="18" /> {{ calendarOpen ? 'Hide calendar' : 'Calendar' }} <ChevronDown :size="16" class="transition-transform" :class="calendarOpen ? 'rotate-180' : ''" />
          </button>
        </div>
        <p v-if="invalidRange" class="mt-3 flex items-center gap-1.5 text-[13px] text-[#A10E24]" role="alert"><AlertCircle :size="15" />Choose a valid range of no more than 120 days.</p>
        <p v-else class="mt-3 text-xs text-[#737780]">{{ fmtDate(from) }} <span class="px-1">to</span> {{ fmtDate(to) }} · {{ rangeDayCount }} days</p>
      </section>

      <section v-if="calendarOpen" class="mt-4 w-full max-w-[440px] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_8px_28px_rgba(31,35,45,0.06)]" aria-label="Appointment calendar" data-appointment-calendar>
        <div class="flex items-center justify-between gap-3 border-b border-[#ECEDEF] px-4 py-3.5">
          <div><p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#92949A]">Monthly calendar</p><h2 class="mt-0.5 text-base font-semibold text-[#25272B]">{{ monthLabel }}</h2><p class="mt-0.5 text-xs text-[#737780]">{{ monthCountLabel }}</p></div>
          <div class="flex items-center gap-2">
            <button type="button" class="month-btn" aria-label="Previous month" @click="shiftMonth(-1)"><ChevronLeft :size="16" /></button>
            <button type="button" class="rounded-lg border border-[#E4E6EA] px-2.5 py-1.5 text-xs font-semibold text-[#555860] transition hover:bg-[#F7F7F8]" @click="goMonthToday">Today</button>
            <button type="button" class="month-btn" aria-label="Next month" @click="shiftMonth(1)"><ChevronRight :size="16" /></button>
          </div>
        </div>
        <div class="p-3.5">
          <div class="grid grid-cols-7 gap-1">
            <div v-for="label in weekdayLabels" :key="label" class="pb-1.5 text-center text-[10px] font-semibold uppercase tracking-wide text-[#92949A]">{{ label }}</div>
            <button v-for="cell in calendarCells" :key="cell.key" type="button" class="calendar-day" :class="[
              !cell.inMonth ? 'calendar-outside' : '',
              cell.key === todayKey ? 'calendar-today' : '',
              cell.key === selectedDay ? 'calendar-selected' : '',
              cell.count ? 'calendar-has-appointments' : '',
            ]" :aria-label="`${cell.label}${cell.count ? `, ${cell.count} appointment${cell.count === 1 ? '' : 's'}` : ', no appointments'}`" :aria-pressed="cell.key === selectedDay" @click="selectDay(cell.key)">
              <span class="calendar-number">{{ cell.day }}</span>
              <span v-if="cell.count" class="calendar-count" :class="cell.key === selectedDay ? 'calendar-count-selected' : ''">{{ cell.count }}</span>
            </button>
          </div>
          <div class="mt-2 flex items-center gap-4 border-t border-[#F0F1F3] pt-3 text-[11px] text-[#737780]">
            <span class="inline-flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-[#C8102E]"></span>Appointments</span>
            <span class="inline-flex items-center gap-1.5"><span class="h-2 w-2 rounded-full border border-[#C8102E] bg-white"></span>Today</span>
            <span class="ml-auto text-right text-[#92949A]">Select a date for its 14-day schedule</span>
          </div>
        </div>
      </section>

      <ErrorMessage class="mt-4" :message="list.error || action.error" />
      <PageLoader v-if="(list.loading && !data) || (calendarOpen && monthList.loading && !monthList.data)" />

      <!-- Empty state -->
      <div v-else-if="data && !filteredAppointments.length" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white px-5 py-14 text-center">
        <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#5B616B]"><CalendarDays :size="22" /></span>
        <p class="mt-3 text-sm font-semibold">{{ activeFilter === 'all' ? 'Nothing booked in this period' : `No ${activeFilter} appointments in this period` }}</p>
        <p class="mx-auto mt-1 max-w-sm text-[13px] leading-5 text-[#5B616B]">{{ activeFilter === 'all' ? 'Adjust the date range or book a new appointment.' : 'Choose another summary card or adjust the date range.' }}</p>
      </div>

      <!-- Days -->
      <div class="mt-6 space-y-6 transition-opacity" :class="list.loading && data ? 'opacity-60' : ''">
        <section v-for="day in days" :key="day.key" :aria-label="fmtDate(day.key)">
          <div class="mb-2.5 flex items-center justify-between gap-3 px-1">
            <div class="flex items-center gap-2.5">
              <h2 class="text-lg font-semibold leading-6">{{ weekday(day.key) }}</h2>
              <span v-if="day.key === todayKey" class="rounded-xl bg-[#FCE8EB] px-2.5 py-1 text-xs font-semibold text-[#A10E24]">Today</span>
              <span class="text-sm text-[#5B616B]">{{ fmtDate(day.key) }}</span>
            </div>
            <span class="text-[13px] text-[#5B616B]">{{ day.rows.length }} appointment{{ day.rows.length === 1 ? "" : "s" }}</span>
          </div>

          <ul class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
            <li
              v-for="a in day.rows"
              :key="a.name"
              class="grid gap-x-4 gap-y-3 border-l-4 px-4 py-4 border-t border-t-[#E4E6EA] first:border-t-0 sm:grid-cols-[76px_minmax(0,1fr)_auto] sm:px-5"
              :class="[tone(a).bar, a.status === 'Cancelled' ? 'bg-[#F4F5F7]/50' : '']"
            >
              <p class="text-[15px] font-semibold tabular-nums leading-6" :class="tone(a).time">{{ fmtTime(a.date_time) }}</p>

              <div class="min-w-0">
                <router-link
                  :to="{ name: 'ClientProfile', params: { name: a.client_id } }"
                  class="rounded text-[15px] font-semibold leading-6 hover:text-[#A10E24] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
                  :class="a.status === 'Cancelled' ? 'text-[#5B616B] line-through' : ''"
                >{{ a.client_name }}</router-link>
                <p class="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[13px] text-[#5B616B]">
                  <span>{{ a.session_type }}</span>
                  <span class="text-[#D5D8DE]" aria-hidden="true">|</span>
                  <span>{{ a.mode_of_contact }}</span>
                  <template v-if="a.location">
                    <span class="text-[#D5D8DE]" aria-hidden="true">|</span>
                    <span class="inline-flex items-center gap-1"><MapPin :size="13" />{{ a.location }}</span>
                  </template>
                </p>
                <p v-if="a.referral_history?.length" class="mt-1 text-xs font-medium text-[#3767A6]">{{ a.counsellor_id === me.data?.user ? `Referred from ${a.referral_history[a.referral_history.length - 1].from_name}` : `Referred to ${a.referral_history[a.referral_history.length - 1].to_name}` }}</p>
              </div>

              <div class="sm:justify-self-end"><Badge :label="apptLabel(a)" :theme="apptTheme(a)" /></div>

              <div v-if="a.status === 'Scheduled'" class="flex flex-wrap gap-2 sm:col-span-2 sm:col-start-2">
                <router-link :to="{ name: 'SessionRecord', params: { name: a.name } }" class="act act-primary">
                  <ClipboardList :size="17" /> In-session
                </router-link>
                <router-link :to="{ name: 'AppointmentEdit', params: { name: a.name } }" class="act">
                  <Pencil :size="16" /> Edit
                </router-link>
                <button type="button" class="act" @click="openReferral(a)"><Share2 :size="16" /> Refer to counsellor</button>
                <button type="button" class="act act-danger" :disabled="action.loading" @click="cancel(a)">
                  <XCircle :size="17" /> Cancel
                </button>
              </div>
              <div v-else-if="a.status === 'Completed'" class="flex flex-wrap gap-2 sm:col-span-2 sm:col-start-2">
                <router-link :to="{ name: 'SessionRecord', params: { name: a.name } }" class="act">
                  <ClipboardList :size="17" /> View session record
                </router-link>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </div>
    <div v-if="referralAppointment" class="fixed inset-0 z-50 flex items-center justify-center bg-[#20242B]/40 p-4" @click.self="closeReferral">
      <section class="w-full max-w-[520px] overflow-hidden rounded-2xl border border-[#E4E6EA] bg-white shadow-[0_20px_60px_rgba(31,35,45,0.2)]" role="dialog" aria-modal="true" aria-labelledby="referral-title">
        <div class="border-b border-[#ECEDEF] px-5 py-4 sm:px-6"><h2 id="referral-title" class="text-lg font-semibold">Refer appointment</h2><p class="mt-1 text-sm text-[#5B616B]">Transfer {{ referralAppointment.client_name }}’s scheduled session to another counsellor. The client’s case owner and original referral source remain recorded.</p></div>
        <form class="space-y-4 p-5 sm:p-6" @submit.prevent="submitReferral">
          <div>
            <label for="referral-counsellor" class="mb-1.5 block text-sm font-medium">Receiving counsellor <span class="text-[#A10E24]">*</span></label>
            <div class="relative">
              <button id="referral-counsellor" type="button" class="range-field flex items-center justify-between text-left" :class="referralTo ? '' : 'text-[#858891]'" :aria-expanded="referralSelectOpen" aria-haspopup="listbox" @click="referralSelectOpen = !referralSelectOpen">
                {{ referralOptions.data?.find((user) => user.name === referralTo)?.full_name || (referralOptions.loading ? 'Loading counsellors…' : 'Select a counsellor') }}
                <ChevronDown :size="16" class="shrink-0 text-[#737780] transition-transform" :class="referralSelectOpen ? 'rotate-180' : ''" />
              </button>
              <div v-if="referralSelectOpen" class="absolute left-0 right-0 top-full z-20 mt-1 max-h-56 overflow-y-auto rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-labelledby="referral-counsellor">
                <button v-for="user in referralOptions.data || []" :key="user.name" type="button" role="option" :aria-selected="referralTo === user.name" class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition hover:bg-[#F4F5F7]" :class="referralTo === user.name ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : ''" @click="referralTo = user.name; referralSelectOpen = false">{{ user.full_name }}<CheckCircle2 v-if="referralTo === user.name" :size="16" /></button>
                <p v-if="!referralOptions.loading && !referralOptions.data?.length" class="px-3 py-3 text-sm text-[#737780]">No other active counsellors are available.</p>
              </div>
            </div>
            <p v-if="!referralOptions.loading && !referralOptions.data?.length" class="mt-1.5 text-xs text-[#737780]">No other active counsellors are available.</p>
          </div>
          <div>
            <label for="referral-reason" class="mb-1.5 block text-sm font-medium">Reason for referral <span class="text-[#A10E24]">*</span></label>
            <textarea id="referral-reason" v-model="referralReason" class="range-field !h-auto min-h-[100px] py-3" maxlength="2000" required placeholder="Record why this appointment is being handed over."></textarea>
          </div>
          <ErrorMessage v-if="referAction.error" :message="referAction.error" />
          <div class="flex justify-end gap-2 border-t border-[#ECEDEF] pt-4">
            <button type="button" class="inline-flex h-10 items-center rounded-[10px] border border-[#D5D8DE] px-4 text-sm font-semibold hover:bg-[#F4F5F7]" @click="closeReferral">Cancel</button>
            <button type="submit" :disabled="referAction.loading || referralOptions.loading || !referralOptions.data?.length" class="inline-flex h-10 items-center gap-2 rounded-[10px] bg-[#C8102E] px-4 text-sm font-semibold text-white hover:bg-[#A10E24] disabled:opacity-50"><Loader2 v-if="referAction.loading" :size="16" class="animate-spin" /><Share2 v-else :size="16" /> Transfer appointment</button>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import {
	AlertCircle, CalendarClock, CalendarDays, CalendarPlus, CheckCircle2, ChevronDown, ChevronLeft, ChevronRight,
	ClipboardList, Loader2, MapPin, Pencil, Share2, XCircle,
} from "lucide-vue-next"
import { apptLabel, apptTheme, dayKey, fmtDate, fmtTime } from "../data/format"
import { me } from "../data/me"

const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const addDays = (value, n) => {
	const d = new Date(`${value}T00:00:00`)
	d.setDate(d.getDate() + n)
	return iso(d)
}

const todayKey = iso(new Date())
const from = ref(todayKey)
const to = ref(addDays(todayKey, 13))
const calendarOpen = ref(false)
const selectedDay = ref(todayKey)
const visibleMonth = ref(`${todayKey.slice(0, 7)}-01`)
const activeFilter = ref("all")
const weekdayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

const list = createResource({ url: "krcti_mhpss.api.counsellor.my_appointments" })
const monthList = createResource({ url: "krcti_mhpss.api.counsellor.my_appointments" })
const referralOptions = createResource({ url: "krcti_mhpss.api.records.referral_counsellors" })
const referralAppointment = ref(null)
const referralTo = ref("")
const referralReason = ref("")
const referralSelectOpen = ref(false)
const data = computed(() => list.data)
const filteredAppointments = computed(() => {
	const rows = data.value?.appointments || []
	if (activeFilter.value === "upcoming") return rows.filter((a) => a.status === "Scheduled" && !a.overdue)
	if (activeFilter.value === "completed") return rows.filter((a) => a.status === "Completed")
	if (activeFilter.value === "overdue") return rows.filter((a) => a.status === "Scheduled" && a.overdue)
	return rows
})
const load = () => list.submit({ date_from: from.value, date_to: to.value })
onMounted(load)
watch([from, to], () => {
	if (invalidRange.value) return
	selectedDay.value = from.value
	if (calendarOpen.value) visibleMonth.value = `${from.value.slice(0, 7)}-01`
	load()
})
onMounted(() => document.addEventListener("click", closeCalendarOutside))
onUnmounted(() => document.removeEventListener("click", closeCalendarOutside))

function closeCalendarOutside(event) {
	if (calendarOpen.value && !event.target.closest("[data-appointment-calendar]") && !event.target.closest("[data-calendar-toggle]")) {
		calendarOpen.value = false
	}
}

const monthStart = computed(() => visibleMonth.value)
const monthEnd = computed(() => addDays(addMonths(monthStart.value, 1), -1))
const rangeDayCount = computed(() => {
	if (!from.value || !to.value || from.value > to.value) return 0
	return Math.round((new Date(`${to.value}T00:00:00`) - new Date(`${from.value}T00:00:00`)) / 86400000) + 1
})
const invalidRange = computed(() => !from.value || !to.value || from.value > to.value || rangeDayCount.value > 120)
const presets = [
	{ label: "Today", range: () => [todayKey, todayKey] },
	{ label: "Next 14 days", range: () => [todayKey, addDays(todayKey, 13)] },
	{ label: "Next 30 days", range: () => [todayKey, addDays(todayKey, 29)] },
	{ label: "This month", range: () => [`${todayKey.slice(0, 7)}-01`, addDays(addMonths(`${todayKey.slice(0, 7)}-01`, 1), -1)] },
]
const applyPreset = (preset) => {
	[from.value, to.value] = preset.range()
}
const isActivePreset = (preset) => {
	const [start, end] = preset.range()
	return from.value === start && to.value === end
}
const monthLabel = computed(() => new Date(`${monthStart.value}T00:00:00`).toLocaleDateString("en-GB", { month: "long", year: "numeric" }))
const monthCountLabel = computed(() => {
	if (monthList.loading && !monthList.data) return "Loading appointments…"
	const count = monthList.data?.appointments?.length || 0
	return `${count} appointment${count === 1 ? "" : "s"} this month`
})
const monthCounts = computed(() => {
	const counts = {}
	for (const row of monthList.data?.appointments || []) {
		const key = dayKey(row.date_time)
		counts[key] = (counts[key] || 0) + 1
	}
	return counts
})
const calendarCells = computed(() => {
	const first = new Date(`${monthStart.value}T00:00:00`)
	const mondayOffset = (first.getDay() + 6) % 7
	const start = addDays(monthStart.value, -mondayOffset)
	return Array.from({ length: 42 }, (_, index) => {
		const key = addDays(start, index)
		const date = new Date(`${key}T00:00:00`)
		return {
			key,
			day: date.getDate(),
			label: date.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" }),
			inMonth: key.slice(0, 7) === monthStart.value.slice(0, 7),
			count: monthCounts.value[key] || 0,
		}
	})
})

function loadMonth() {
	monthList.submit({ date_from: monthStart.value, date_to: monthEnd.value })
}
function toggleCalendar() {
	calendarOpen.value = !calendarOpen.value
	if (calendarOpen.value) loadMonth()
}
function shiftMonth(amount) {
	visibleMonth.value = addMonths(monthStart.value, amount)
	loadMonth()
}
function goMonthToday() {
	visibleMonth.value = `${todayKey.slice(0, 7)}-01`
	selectedDay.value = todayKey
	loadMonth()
}
function selectDay(key) {
	selectedDay.value = key
	if (key.slice(0, 7) !== monthStart.value.slice(0, 7)) {
		visibleMonth.value = `${key.slice(0, 7)}-01`
		loadMonth()
	}
	from.value = key
	to.value = addDays(key, 13)
}

function addMonths(value, amount) {
	const date = new Date(`${value}T00:00:00`)
	date.setDate(1)
	date.setMonth(date.getMonth() + amount)
	return iso(date)
}

const days = computed(() => {
	const groups = {}
	for (const a of filteredAppointments.value) (groups[dayKey(a.date_time)] ||= []).push(a)
	return Object.keys(groups).sort().map((key) => ({ key, rows: groups[key] }))
})

const weekday = (key) => new Date(`${key}T00:00:00`).toLocaleDateString("en-GB", { weekday: "long" })

// Status drives the left accent bar and the time colour
const TONES = {
	green: { bar: "border-l-[#146C3A]", time: "text-[#146C3A]" },
	red: { bar: "border-l-[#C8102E]", time: "text-[#A10E24]" },
	blue: { bar: "border-l-[#1B4DB1]", time: "text-[#2B2F36]" },
	grey: { bar: "border-l-[#D5D8DE]", time: "text-[#5B616B]" },
}
const tone = (a) => TONES[a.status === "Completed" ? "green" : a.status === "Cancelled" ? "grey" : a.overdue ? "red" : "blue"]

// Period summary
const tiles = computed(() => {
	const rows = data.value?.appointments || []
	const completed = rows.filter((a) => a.status === "Completed").length
	const overdue = rows.filter((a) => a.status === "Scheduled" && a.overdue).length
	const upcoming = rows.filter((a) => a.status === "Scheduled" && !a.overdue).length
	return [
		{ label: "In this period", value: rows.length, filter: "all", icon: ClipboardList, tile: "bg-[#FCE8EB] text-[#A10E24]" },
		{ label: "Upcoming", value: upcoming, filter: "upcoming", icon: CalendarClock, tile: "bg-[#E0EAFD] text-[#1B4DB1]" },
		{ label: "Completed", value: completed, filter: "completed", icon: CheckCircle2, tile: "bg-[#DCF3E4] text-[#146C3A]" },
		{ label: "Overdue", value: overdue, filter: "overdue", icon: AlertCircle, tile: "bg-[#FBE0E4] text-[#A10E24]" },
	]
})

const action = createResource({ url: "krcti_mhpss.api.records.set_appointment_status", onSuccess: load })
const referAction = createResource({
	url: "krcti_mhpss.api.records.refer_appointment",
	onSuccess() { closeReferral(); load() },
})
function openReferral(appointment) {
	referralAppointment.value = appointment
	referralTo.value = ""
	referralReason.value = ""
	referralSelectOpen.value = false
	if (!referralOptions.data) referralOptions.submit()
}
function closeReferral() {
	referralAppointment.value = null
	referralTo.value = ""
	referralReason.value = ""
	referralSelectOpen.value = false
}
function submitReferral() {
	if (!referralAppointment.value || !referralTo.value || !referralReason.value.trim()) return
	referAction.submit({ name: referralAppointment.value.name, to_counsellor: referralTo.value, reason: referralReason.value.trim() })
}
const setStatus = (a, status) => action.submit({ name: a.name, status })
function cancel(a) {
	if (window.confirm(`Cancel the appointment with ${a.client_name}?`)) setStatus(a, "Cancelled")
}
</script>

<style scoped>
.range-field {
	display: block;
	height: 44px;
	width: 100%;
	border: 1px solid #d5d8de;
	border-radius: 8px;
	background: #fff;
	padding: 0 12px;
	font: 14px Inter, system-ui, sans-serif;
	color: #2b2f36;
}
.range-field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 2px rgba(200, 16, 46, .25); }
.range-field-error { border-color: #a10e24; }
.range-preset {
	display: inline-flex;
	height: 44px;
	align-items: center;
	border: 1px solid #d5d8de;
	border-radius: 10px;
	background: #fff;
	padding: 0 14px;
	font-size: 13px;
	font-weight: 600;
	color: #3c3f45;
	transition: background .15s, border-color .15s, color .15s;
}
.range-preset:hover { background: #f4f5f7; }
.range-preset-active, .range-preset-active:hover { border-color: #c8102e; background: #fce8eb; color: #a10e24; }
.month-btn {
	display: inline-flex;
	height: 40px;
	width: 40px;
	align-items: center;
	justify-content: center;
	border: 1px solid #e4e6ea;
	border-radius: 10px;
	background: #fff;
	color: #555860;
	transition: background .15s, border-color .15s, color .15s;
}
.month-btn:hover { background: #f7f7f8; border-color: #d5d8de; color: #25272b; }

/* Grid centring keeps the date number exactly in the middle of the tile.
   The count badge is absolutely positioned, so it never shifts the number. */
.calendar-day {
	position: relative;
	display: grid;
	place-items: center;
	min-height: 42px;
	min-width: 0;
	border: 1px solid transparent;
	border-radius: 9px;
	padding: 0;
	color: #3c3f45;
	transition: background .15s, border-color .15s;
}
.calendar-day:hover { background: #f7f7f8; }
.calendar-day:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.4); }
.calendar-number { display: grid; height: 26px; width: 26px; place-items: center; border-radius: 999px; font-size: 12px; font-weight: 600; line-height: 1; }
.calendar-count { position: absolute; right: 3px; top: 3px; display: grid; min-width: 14px; height: 14px; place-items: center; border-radius: 999px; background: #fce8eb; padding: 0 3px; color: #a10e24; font-size: 9px; font-weight: 700; line-height: 1; }
.calendar-count-selected { background: #c8102e; color: white; }
.calendar-outside { color: #c2c4c9; }
.calendar-today .calendar-number { border: 1.5px solid #c8102e; color: #a10e24; }
.calendar-selected { border-color: #f3c3cb; background: #fff7f8; }
.calendar-selected:hover { background: #fff1f3; }
.calendar-selected .calendar-number { background: #c8102e; color: white; }
.calendar-has-appointments:not(.calendar-selected) .calendar-number { background: #fce8eb; color: #a10e24; }

.nav-btn {
	display: inline-flex;
	height: 44px;
	width: 44px;
	align-items: center;
	justify-content: center;
	border-radius: 10px;
	border: 1px solid #d5d8de;
	background: #fff;
	color: #2b2f36;
	transition: background 0.15s;
}
.nav-btn:hover { background: #f4f5f7; }
.nav-btn:focus-visible,
.act:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.4); }

.act {
	display: inline-flex;
	height: 40px;
	align-items: center;
	gap: 8px;
	border-radius: 10px;
	border: 1px solid #d5d8de;
	background: #fff;
	padding: 0 16px;
	font-size: 14px;
	font-weight: 600;
	color: #2b2f36;
	transition: background 0.15s;
}
.act:hover { background: #f4f5f7; }
.act:disabled { cursor: wait; opacity: 0.6; }
.act-primary { border-color: #c8102e; background: #c8102e; color: #fff; }
.act-primary:hover { border-color: #a10e24; background: #a10e24; }
.act-danger { color: #a10e24; }
.act-danger:hover { background: #fce8eb; border-color: #f3c3cb; }
</style>
