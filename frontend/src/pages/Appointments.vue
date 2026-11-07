<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <!-- Page header -->
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p class="text-sm font-medium text-[#737780]">Booked Appointments</p>
          <h1 class="mt-1 text-2xl font-semibold leading-8 sm:text-[28px]">Appointments</h1>
          <p class="mt-0.5 text-[13px] text-[#5B616B]">View appointments by period, status, or date</p>
        </div>
      </div>

      <!-- Overdue alert -->
      <div v-if="data?.overdue_total" class="mt-5 flex items-start gap-3 rounded-xl bg-[#FBE0E4] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
        <AlertCircle :size="20" class="mt-px shrink-0" />
        <p>
          <span class="font-semibold">{{ data.overdue_total }} appointment{{ data.overdue_total === 1 ? " has" : "s have" }} passed without being completed.</span>
          Record the session once it has taken place to keep the case history up to date.
        </p>
      </div>

      <!-- Summary for this period -->
      <section v-if="data" class="mt-5 grid grid-cols-2 gap-4 lg:grid-cols-4" aria-label="Summary for this period">
        <button v-for="t in tiles" :key="t.filter" type="button" class="flex items-center gap-3.5 rounded-xl border bg-white p-4 text-left transition hover:-translate-y-0.5 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" :class="activeFilter === t.filter ? 'border-[#C8102E] ring-1 ring-[#C8102E]/20' : 'border-[#E4E6EA]'" :aria-pressed="activeFilter === t.filter" @click="selectFilter(t.filter)">
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px]" :class="t.tile"><component :is="t.icon" :size="20" /></span>
          <div class="min-w-0">
            <p class="truncate text-[13px] text-[#5B616B]">{{ t.label }}</p>
            <p class="text-[28px] font-semibold leading-[34px]">{{ t.value }}</p>
          </div>
        </button>
      </section>



      <!-- Calendar toggle -->
      <button type="button" class="mt-4 flex w-full items-center gap-3 rounded-xl border border-[#E4E6EA] bg-white p-4 text-left transition hover:border-[#D5D8DE] hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" :aria-expanded="calendarOpen" @click="toggleCalendar">
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-[#FCE8EB] text-[#A10E24]"><CalendarDays :size="19" /></span>
        <span class="min-w-0 flex-1"><span class="block text-sm font-semibold text-[#2B2F36]">Appointment calendar</span><span class="mt-0.5 block text-xs text-[#737780]">{{ calendarOpen ? 'Hide weekly calendar' : 'Open the weekly calendar' }}</span></span>
        <ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="calendarOpen ? 'rotate-180' : ''" />
      </button>

      <!-- Weekly calendar -->
      <section v-if="calendarOpen" class="mt-4 w-full overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_8px_28px_rgba(31,35,45,0.06)]" aria-label="Weekly appointment calendar">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[#ECEDEF] px-4 py-4 sm:px-6">
          <div>
            <h2 class="text-xl font-semibold tracking-tight text-[#25272B]">{{ weekLabel }}</h2>
            <p class="mt-0.5 text-xs text-[#737780]">{{ weekCountLabel }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button type="button" class="month-btn" aria-label="Previous week" @click="shiftWeek(-1)"><ChevronLeft :size="16" /></button>
            <button type="button" class="rounded-lg border border-[#E4E6EA] px-3 py-2 text-xs font-semibold text-[#555860] transition hover:bg-[#F7F7F8]" @click="goToday">Today</button>
            <button type="button" class="month-btn" aria-label="Next week" @click="shiftWeek(1)"><ChevronRight :size="16" /></button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <div class="min-w-[880px]">
            <!-- Day headers -->
            <div class="grid grid-cols-[64px_repeat(7,minmax(0,1fr))] border-b border-[#ECEDEF] bg-[#FAFAFB]">
              <div></div>
              <button v-for="col in weekColumns" :key="col.key" type="button" class="week-head" :class="col.key === selectedDay ? 'week-head-selected' : ''" :aria-pressed="col.key === selectedDay" :aria-label="`${col.long}${col.events.length ? `, ${col.events.length} appointment${col.events.length === 1 ? '' : 's'}` : ', no appointments'}`" @click="selectDay(col.key)">
                <span class="text-[13px] font-medium text-[#5B616B]">{{ col.short }}</span>
                <span class="week-num" :class="col.isToday ? 'week-num-today' : ''">{{ col.num }}</span>
                <span v-if="col.events.length" class="hidden text-[11px] text-[#92949A] lg:inline">{{ col.events.length }}</span>
              </button>
            </div>

            <!-- Time grid -->
            <div class="max-h-[680px] overflow-y-auto">
              <div class="grid grid-cols-[64px_repeat(7,minmax(0,1fr))] pt-3">
                <div>
                  <div v-for="h in hours" :key="h" class="pr-3 text-right text-[11px] font-medium text-[#92949A]" :style="{ height: HOUR_H + 'px' }">
                    <span class="relative -top-2">{{ hourLabel(h) }}</span>
                  </div>
                </div>

                <div v-for="col in weekColumns" :key="col.key" class="week-col relative border-l border-[#F0F1F3]" :class="col.isToday ? 'bg-[#FFFBFB]' : ''" :style="{ height: hours.length * HOUR_H + 'px' }">
                  <div v-if="col.isToday && nowTop !== null" class="pointer-events-none absolute left-0 right-0 z-10 flex items-center" :style="{ top: nowTop + 'px' }" aria-hidden="true">
                    <span class="-ml-1 h-2 w-2 rounded-full bg-[#C8102E]"></span>
                    <span class="h-px flex-1 bg-[#C8102E]"></span>
                  </div>

                  <component :is="ev.a.status === 'Cancelled' ? 'div' : RouterLink" v-for="ev in col.events" :key="ev.a.name" v-bind="eventBind(ev.a)" class="ev" :class="`ev-${ev.tone}`" :style="ev.style" :title="`${ev.a.client_name} · ${ev.a.session_type || ''} · ${ev.range}`">
                    <span class="flex items-start justify-between gap-1">
                      <span class="truncate text-xs font-semibold leading-4" :class="ev.a.status === 'Cancelled' ? 'line-through' : ''">{{ ev.a.client_name }}</span>
                      <component :is="toneIcon[ev.tone]" :size="13" class="mt-0.5 shrink-0" />
                    </span>
                    <span class="block truncate text-[11px] leading-4 opacity-80">{{ ev.range }}</span>
                    <span v-if="ev.lanes === 1 && ev.height >= 64 && ev.a.status !== 'Cancelled'" class="mt-1 inline-block text-[11px] font-semibold underline underline-offset-2">See details</span>
                  </component>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-[#F0F1F3] px-4 py-3.5 text-xs text-[#737780] sm:px-6">
          <span class="inline-flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-[3px] bg-[#1B4DB1]"></span>Upcoming</span>
          <span class="inline-flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-[3px] bg-[#146C3A]"></span>Completed</span>
          <span class="inline-flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-[3px] bg-[#C8102E]"></span>Overdue</span>
          <span class="inline-flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-[3px] bg-[#B5B8BF]"></span>Cancelled</span>
          <span class="text-[#92949A] sm:ml-auto">Select a day to list its next 14 days below</span>
        </div>
      </section>

      <ErrorMessage class="mt-4" :message="list.error || referAction.error" />
      <PageLoader v-if="(list.loading && !data) || (calendarOpen && weekList.loading && !weekList.data)" />

      <!-- Empty state -->
      <div v-else-if="data && !filteredAppointments.length" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white px-5 py-14 text-center">
        <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#5B616B]"><CalendarDays :size="22" /></span>
        <p class="mt-3 text-sm font-semibold">{{ activeFilter === 'all' ? 'Nothing booked in this period' : `No ${activeFilter} appointments` }}</p>
        <p class="mx-auto mt-1 max-w-sm text-[13px] leading-5 text-[#5B616B]">{{ activeFilter === 'all' ? 'Adjust the date range or book a new appointment.' : 'Choose another summary card to view its appointments.' }}</p>
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

    <!-- Referral dialog -->
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
import { RouterLink, useRoute } from "vue-router"
import {
	AlertCircle, CalendarClock, CalendarDays, CheckCircle2, ChevronDown, ChevronLeft, ChevronRight,
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
const mondayOf = (value) => {
	const d = new Date(`${value}T00:00:00`)
	d.setDate(d.getDate() - ((d.getDay() + 6) % 7))
	return iso(d)
}

const todayKey = iso(new Date())
const route = useRoute()
const from = ref(todayKey)
const to = ref(addDays(todayKey, 13))
const calendarOpen = ref(false)
const selectedDay = ref(todayKey)
const weekStart = ref(mondayOf(todayKey))
const allowedFilters = ["all", "upcoming", "completed", "overdue"]
const activeFilter = ref(allowedFilters.includes(route.query.filter) ? route.query.filter : "all")

const list = createResource({ url: "krcti_mhpss.api.counsellor.my_appointments" })
const weekList = createResource({ url: "krcti_mhpss.api.counsellor.my_appointments" })
const referralOptions = createResource({ url: "krcti_mhpss.api.records.referral_counsellors" })
const referralAppointment = ref(null)
const referralTo = ref("")
const referralReason = ref("")
const referralSelectOpen = ref(false)
const data = computed(() => list.data)
const filteredAppointments = computed(() => data.value?.appointments || [])
const load = () => list.submit({ date_from: from.value, date_to: to.value, view: activeFilter.value === "all" ? "period" : activeFilter.value })
function selectFilter(filter) {
	activeFilter.value = filter
	if (filter === "overdue") calendarOpen.value = false
	load()
}
onMounted(load)
watch(() => route.query.filter, (filter) => {
	selectFilter(allowedFilters.includes(filter) ? filter : "all")
})
watch([from, to], () => {
	if (invalidRange.value) return
	load()
})

/* ---------- Date range ---------- */
const rangeDayCount = computed(() => {
	if (!from.value || !to.value || from.value > to.value) return 0
	return Math.round((new Date(`${to.value}T00:00:00`) - new Date(`${from.value}T00:00:00`)) / 86400000) + 1
})
const invalidRange = computed(() => !from.value || !to.value || from.value > to.value || rangeDayCount.value > 120)
function addMonths(value, amount) {
	const date = new Date(`${value}T00:00:00`)
	date.setDate(1)
	date.setMonth(date.getMonth() + amount)
	return iso(date)
}
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

/* ---------- Weekly calendar ---------- */
// HOUR_H must match background-size in .week-col below.
const HOUR_H = 80
const DEFAULT_MINUTES = 60 // used when an appointment has no duration field
const toneIcon = { upcoming: CalendarClock, completed: CheckCircle2, overdue: AlertCircle, cancelled: XCircle }

const weekAppointments = computed(() => weekList.data?.appointments || [])
const parseDate = (value) => new Date(String(value).replace(" ", "T"))
const minutesOf = (value) => {
	const d = parseDate(value)
	return d.getHours() * 60 + d.getMinutes()
}
const durationOf = (a) => Number(a.duration || a.duration_minutes) || DEFAULT_MINUTES
const hourLabel = (h) => `${h % 12 || 12} ${h < 12 ? "AM" : "PM"}`
const clock = (mins) => {
	const h = Math.floor(mins / 60) % 24
	const m = mins % 60
	return `${h % 12 || 12}${m ? `:${String(m).padStart(2, "0")}` : ""} ${h < 12 ? "AM" : "PM"}`
}
const eventTone = (a) => (a.status === "Completed" ? "completed" : a.status === "Cancelled" ? "cancelled" : a.overdue ? "overdue" : "upcoming")
const eventBind = (a) => (a.status === "Cancelled" ? {} : { to: { name: "SessionRecord", params: { name: a.name } } })

// The grid shows 8 AM to 6 PM by default and grows to fit earlier or later sessions.
const hourBounds = computed(() => {
	let start = 8
	let end = 18
	for (const a of weekAppointments.value) {
		const s = minutesOf(a.date_time)
		start = Math.min(start, Math.floor(s / 60))
		end = Math.max(end, Math.ceil((s + durationOf(a)) / 60))
	}
	return [Math.max(0, start), Math.min(24, end)]
})
const hours = computed(() => Array.from({ length: hourBounds.value[1] - hourBounds.value[0] }, (_, i) => hourBounds.value[0] + i))

// Side-by-side lanes for sessions that overlap in time
function layoutDay(rows) {
	const base = hourBounds.value[0] * 60
	const items = rows
		.map((a) => {
			const start = minutesOf(a.date_time)
			return { a, start, end: start + durationOf(a), tone: eventTone(a), lane: 0, lanes: 1 }
		})
		.sort((x, y) => x.start - y.start || x.end - y.end)
	const out = []
	let cluster = []
	let clusterEnd = -1
	const flush = () => {
		const laneEnds = []
		for (const it of cluster) {
			let i = laneEnds.findIndex((end) => end <= it.start)
			if (i === -1) { i = laneEnds.length; laneEnds.push(0) }
			laneEnds[i] = it.end
			it.lane = i
		}
		for (const it of cluster) it.lanes = laneEnds.length
		out.push(...cluster)
		cluster = []
		clusterEnd = -1
	}
	for (const it of items) {
		if (cluster.length && it.start >= clusterEnd) flush()
		cluster.push(it)
		clusterEnd = Math.max(clusterEnd, it.end)
	}
	if (cluster.length) flush()
	return out.map((it) => {
		const height = Math.max(((it.end - it.start) / 60) * HOUR_H - 4, 36)
		return {
			...it,
			height,
			range: `${clock(it.start)} – ${clock(it.end)}`,
			style: {
				top: `${((it.start - base) / 60) * HOUR_H + 2}px`,
				height: `${height}px`,
				left: `calc(${(it.lane / it.lanes) * 100}% + 3px)`,
				width: `calc(${100 / it.lanes}% - 6px)`,
			},
		}
	})
}

const weekColumns = computed(() =>
	Array.from({ length: 7 }, (_, i) => {
		const key = addDays(weekStart.value, i)
		const date = new Date(`${key}T00:00:00`)
		return {
			key,
			short: date.toLocaleDateString("en-GB", { weekday: "short" }),
			long: date.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" }),
			num: date.getDate(),
			isToday: key === todayKey,
			events: layoutDay(weekAppointments.value.filter((a) => dayKey(a.date_time) === key)),
		}
	})
)

const weekLabel = computed(() => {
	const a = new Date(`${weekStart.value}T00:00:00`)
	const b = new Date(`${addDays(weekStart.value, 6)}T00:00:00`)
	const f = (d, o) => d.toLocaleDateString("en-GB", o)
	return a.getMonth() === b.getMonth()
		? `${a.getDate()} – ${f(b, { day: "numeric", month: "long", year: "numeric" })}`
		: `${f(a, { day: "numeric", month: "short" })} – ${f(b, { day: "numeric", month: "short", year: "numeric" })}`
})
const weekCountLabel = computed(() => {
	if (weekList.loading && !weekList.data) return "Loading appointments…"
	const count = weekAppointments.value.length
	return `${count} appointment${count === 1 ? "" : "s"} this week`
})

// Current-time marker for today's column
const nowMinutes = ref(new Date().getHours() * 60 + new Date().getMinutes())
let clockTimer = null
onMounted(() => {
	clockTimer = setInterval(() => {
		const n = new Date()
		nowMinutes.value = n.getHours() * 60 + n.getMinutes()
	}, 60000)
})
onUnmounted(() => clearInterval(clockTimer))
const nowTop = computed(() => {
	const base = hourBounds.value[0] * 60
	const top = ((nowMinutes.value - base) / 60) * HOUR_H
	return top >= 0 && top <= hours.value.length * HOUR_H ? top : null
})

function loadWeek() {
	weekList.submit({ date_from: weekStart.value, date_to: addDays(weekStart.value, 6) })
}
function toggleCalendar() {
	calendarOpen.value = !calendarOpen.value
	if (calendarOpen.value) loadWeek()
}
function shiftWeek(amount) {
	weekStart.value = addDays(weekStart.value, amount * 7)
	loadWeek()
}
function goToday() {
	weekStart.value = mondayOf(todayKey)
	selectedDay.value = todayKey
	loadWeek()
}
function selectDay(key) {
	selectedDay.value = key
	activeFilter.value = "all"
	if (mondayOf(key) !== weekStart.value) {
		weekStart.value = mondayOf(key)
		loadWeek()
	}
	from.value = key
	to.value = addDays(key, 13)
}

/* ---------- Day list ---------- */
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
	const summary = data.value?.summary || {}
	const completed = summary.completed || 0
	const overdue = summary.overdue || 0
	const upcoming = summary.upcoming || 0
	return [
		{ label: "In this period", value: rows.length, filter: "all", icon: ClipboardList, tile: "bg-[#FCE8EB] text-[#A10E24]" },
		{ label: "Upcoming", value: upcoming, filter: "upcoming", icon: CalendarClock, tile: "bg-[#E0EAFD] text-[#1B4DB1]" },
		{ label: "Completed", value: completed, filter: "completed", icon: CheckCircle2, tile: "bg-[#DCF3E4] text-[#146C3A]" },
		{ label: "Overdue", value: overdue, filter: "overdue", icon: AlertCircle, tile: "bg-[#FBE0E4] text-[#A10E24]" },
	]
})

/* ---------- Referral ---------- */
const referAction = createResource({
	url: "krcti_mhpss.api.records.refer_appointment",
	onSuccess() { closeReferral(); load(); if (calendarOpen.value) loadWeek() },
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

/* Day headers */
.week-head {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	height: 52px;
	border-left: 1px solid #f0f1f3;
	transition: background .15s;
}
.week-head:hover { background: #f4f5f7; }
.week-head:focus-visible { outline: none; box-shadow: inset 0 0 0 2px rgba(200, 16, 46, .4); }
.week-head-selected { background: #fff; box-shadow: inset 0 -2px 0 #c8102e; }
.week-num {
	display: grid;
	height: 28px;
	min-width: 28px;
	place-items: center;
	border-radius: 999px;
	font-size: 14px;
	font-weight: 600;
	color: #2b2f36;
}
.week-num-today { background: #c8102e; color: #fff; }

/* Hour lines. The 80px size must equal HOUR_H in the script. */
.week-col {
	background-image: linear-gradient(to bottom, #eceef1 1px, transparent 1px);
	background-size: 100% 80px;
}

/* Appointment cards */
.ev {
	position: absolute;
	display: block;
	overflow: hidden;
	border-radius: 10px;
	border-left: 4px solid var(--ev-bar);
	background: var(--ev-bg);
	padding: 6px 8px;
	color: var(--ev-text);
	transition: box-shadow .15s, transform .15s;
}
a.ev:hover { box-shadow: 0 6px 16px rgba(31, 35, 45, .12); transform: translateY(-1px); z-index: 5; }
a.ev:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, .4); }
.ev-upcoming { --ev-bar: #1b4db1; --ev-bg: #e8effd; --ev-text: #173f93; }
.ev-completed { --ev-bar: #146c3a; --ev-bg: #e2f4e8; --ev-text: #0f5a30; }
.ev-overdue { --ev-bar: #c8102e; --ev-bg: #fce6ea; --ev-text: #a10e24; }
.ev-cancelled { --ev-bar: #b5b8bf; --ev-bg: #f1f2f4; --ev-text: #6b707a; }

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
.act:focus-visible { outline: none; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.4); }
.act:disabled { cursor: wait; opacity: 0.6; }
.act-primary { border-color: #c8102e; background: #c8102e; color: #fff; }
.act-primary:hover { border-color: #a10e24; background: #a10e24; }
</style>
