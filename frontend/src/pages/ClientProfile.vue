<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <router-link
        :to="{ name: 'Clients' }"
        class="inline-flex h-11 items-center gap-2 rounded-[10px] pr-3 text-sm font-medium text-[#5B616B] transition hover:text-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
      >
        <ArrowLeft :size="18" /> Back to clients
      </router-link>

      <PageLoader v-if="profile.loading && !profile.data" />

      <div v-else-if="profile.error && !profile.data" class="mt-2 rounded-xl border border-[#E4E6EA] bg-white p-10 text-center">
        <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#FBE0E4] text-[#A10E24]"><UserRoundX :size="22" /></span>
        <h1 class="mt-4 text-lg font-semibold">Client record unavailable</h1>
        <p class="mx-auto mt-1 max-w-sm text-[13px] leading-5 text-[#5B616B]">This client could not be found, or you don’t have access to the record.</p>
      </div>

      <template v-else-if="profile.data">
        <!-- Identity header -->
        <section class="mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
          <div class="flex flex-col justify-between gap-5 p-5 sm:flex-row sm:items-center sm:p-6">
            <div class="flex min-w-0 items-center gap-4">
              <span class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xl font-semibold text-[#A10E24]">{{ initials(c.full_name) }}</span>
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-x-3 gap-y-1.5">
                  <h1 class="text-2xl font-semibold leading-8">{{ c.full_name }}</h1>
                  <Badge :label="c.case_status" :theme="caseTheme(c.case_status)" />
                </div>
                <p class="mt-0.5 text-[13px] text-[#5B616B]">
                  <span class="font-semibold text-[#2B2F36]">{{ c.scholar_code }}</span>
                  <span class="mx-2 text-[#D5D8DE]">|</span>Record ID {{ c.name }}
                </p>
                <p class="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-[#5B616B]">
                  <span class="inline-flex items-center gap-1.5"><Phone :size="15" class="text-[#5B616B]" />{{ c.phone_number || 'No phone recorded' }}</span>
                  <span v-if="c.institution" class="inline-flex items-center gap-1.5"><Building2 :size="15" class="text-[#5B616B]" />{{ c.institution }}</span>
                </p>
              </div>
            </div>

            <div class="flex flex-wrap gap-2.5 sm:justify-end">
              <router-link
                v-if="c.case_status !== 'Closed' && !hasScheduledAppointment"
                :to="{ name: 'AppointmentNew', query: { client: c.name } }"
                class="inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#C8102E] bg-[#C8102E] px-[18px] text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40 focus-visible:ring-offset-2"
              >
                <CalendarPlus :size="18" /> Book appointment
              </router-link>
              <span v-else-if="c.case_status !== 'Closed' && hasScheduledAppointment" class="inline-flex h-11 items-center rounded-[10px] bg-[#FDECC8] px-3.5 text-[13px] font-medium text-[#8A4B00]">
                Complete or cancel the scheduled appointment first
              </span>
              <router-link
                v-if="c.case_status !== 'Closed' || role === 'admin'"
                :to="{ name: 'ClientEdit', params: { name: c.name } }"
                class="inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#D5D8DE] bg-white px-[18px] text-sm font-semibold text-[#2B2F36] transition hover:bg-[#F4F5F7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
              >
                <Pencil :size="18" /> Edit details
              </router-link>
            </div>
          </div>

          <!-- At-a-glance strip -->
          <dl class="grid grid-cols-2 border-t border-[#E4E6EA] bg-[#F4F5F7]/60 lg:grid-cols-4">
            <div
              v-for="(item, i) in glance"
              :key="item.label"
              class="px-5 py-3.5 sm:px-6"
              :class="[i % 2 === 1 ? 'border-l border-[#E4E6EA]' : '', i > 1 ? 'border-t border-[#E4E6EA] lg:border-t-0' : '', i > 0 ? 'lg:border-l lg:border-[#E4E6EA]' : '']"
            >
              <dt class="text-[13px] text-[#5B616B]">{{ item.label }}</dt>
              <dd class="mt-0.5 text-[15px] font-semibold" :class="item.class">{{ item.value }}</dd>
            </div>
          </dl>
        </section>

        <div class="mt-5 grid items-start gap-5 xl:grid-cols-[minmax(0,1.5fr)_minmax(340px,0.9fr)]">
          <!-- Client information -->
          <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
            <div class="border-b border-[#E4E6EA] px-5 py-4 sm:px-6">
              <h2 class="text-lg font-semibold leading-6">Client information</h2>
              <p class="mt-0.5 text-[13px] text-[#5B616B]">Personal, education and programme details</p>
            </div>

            <div class="divide-y divide-[#E4E6EA]">
              <div v-for="group in detailGroups" :key="group.title" class="grid gap-x-8 gap-y-4 px-5 py-6 sm:px-6 lg:grid-cols-[190px_minmax(0,1fr)]">
                <div class="flex items-center gap-3 lg:items-start">
                  <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><component :is="group.icon" :size="19" /></span>
                  <div class="min-w-0">
                    <h3 class="text-sm font-semibold leading-5">{{ group.title }}</h3>
                    <p class="text-[13px] leading-[18px] text-[#5B616B]">{{ group.hint }}</p>
                  </div>
                </div>
                <dl class="grid grid-cols-2 gap-x-6 gap-y-5">
                  <div v-for="f in group.fields" :key="f.label" class="min-w-0" :class="f.wide ? 'col-span-2' : 'col-span-2 sm:col-span-1'">
                    <dt class="text-[13px] text-[#5B616B]">{{ f.label }}</dt>
                    <dd class="mt-0.5 break-words text-[15px] leading-6">
                      <span v-if="f.value" class="font-medium">{{ f.value }}</span>
                      <span v-else class="italic text-[#6B717B]">Not recorded</span>
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </section>

          <div class="space-y-5">
            <!-- Case management -->
            <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
              <div class="border-b border-[#E4E6EA] px-5 py-4">
                <h2 class="text-lg font-semibold leading-6">Case management</h2>
                <p class="mt-0.5 text-[13px] text-[#5B616B]">{{ c.case_status === 'Closed' ? 'This case is available in read-only mode.' : 'Update this client’s current case status' }}</p>
              </div>
              <div class="p-5">
                <div class="flex items-center justify-between gap-3 rounded-lg bg-[#F4F5F7] px-4 py-3">
                  <span class="text-sm font-medium text-[#5B616B]">Current status</span>
                  <Badge :label="c.case_status" :theme="caseTheme(c.case_status)" />
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                  <Button v-if="c.case_status === 'Active'" :loading="status.loading" @click="setStatus('Follow-Up Pending')">Mark follow-up pending</Button>
                  <Button v-if="c.case_status === 'Follow-Up Pending'" :loading="status.loading" @click="setStatus('Active')">Mark active</Button>
                  <Button v-if="canClose" theme="red" :loading="status.loading" @click="close">Close this case</Button>
                  <Button v-if="c.case_status === 'Closed' && role === 'admin'" :loading="status.loading" @click="setStatus('Active')">Re-open the case</Button>
                </div>
                <p v-if="!canClose && c.case_status !== 'Closed'" class="mt-4 flex items-start gap-2 rounded-lg bg-[#E0EAFD] px-3.5 py-3 text-[13px] leading-[18px] text-[#1B4DB1]">
                  <Info :size="16" class="mt-px shrink-0" />A case can be closed after a completed Termination session.
                </p>
                <ErrorMessage class="mt-3" :message="status.error" />
              </div>
            </section>

            <!-- Baseline survey -->
            <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
              <div class="flex items-center justify-between gap-3 border-b border-[#E4E6EA] px-5 py-4">
                <div>
                  <h2 class="text-lg font-semibold leading-6">Baseline survey</h2>
                  <p class="mt-0.5 text-[13px] text-[#5B616B]">Initial wellbeing and support needs</p>
                </div>
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><ClipboardList :size="19" /></span>
              </div>

              <div v-if="!s" class="p-5">
                <p class="text-sm text-[#5B616B]">No baseline survey recorded for this client yet.</p>
                <router-link
                  v-if="c.case_status !== 'Closed'"
                  :to="{ name: 'Baseline', params: { name: c.name } }"
                  class="mt-4 inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#D5D8DE] bg-white px-[18px] text-sm font-semibold text-[#2B2F36] transition hover:bg-[#F4F5F7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
                >
                  <ClipboardList :size="18" /> Record baseline survey
                </router-link>
              </div>

              <div v-else class="p-5">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="inline-flex items-center gap-1.5 rounded-xl bg-[#DCF3E4] px-2.5 py-1 text-xs font-semibold text-[#146C3A]"><ShieldCheck :size="14" /> Recorded</span>
                  <span class="text-[13px] text-[#5B616B]">{{ fmtDateTime(s.completed_on) }}</span>
                </div>
                <p class="mt-3 flex items-start gap-2 text-[13px] leading-[18px] text-[#5B616B]"><LockKeyhole :size="15" class="mt-px shrink-0" />Confidential survey responses are read-only after submission.</p>
                <dl class="mt-4 grid gap-x-6 sm:grid-cols-2">
                  <div
                    v-for="[label, value] in survey"
                    :key="label"
                    class="border-t border-[#E4E6EA] py-3.5"
                    :class="label === 'Main concerns' || label === 'Conflict or disaster exposure' ? 'sm:col-span-2' : ''"
                  >
                    <dt class="text-[13px] text-[#5B616B]">{{ label }}</dt>
                    <dd class="mt-0.5 whitespace-pre-line break-words text-sm leading-5 font-medium">
                      <span v-if="value">{{ value }}</span>
                      <span v-else class="font-normal italic text-[#6B717B]">Not recorded</span>
                    </dd>
                  </div>
                </dl>
              </div>
            </section>
          </div>
        </div>

        <!-- Session history -->
        <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
          <div class="flex items-center justify-between gap-3 border-b border-[#E4E6EA] px-5 py-4 sm:px-6">
            <div>
              <h2 class="text-lg font-semibold leading-6">Session history</h2>
              <p class="mt-0.5 text-[13px] text-[#5B616B]">{{ history.length }} recorded appointment{{ history.length === 1 ? '' : 's' }}</p>
            </div>
            <router-link
              v-if="c.case_status !== 'Closed' && !hasScheduledAppointment"
              :to="{ name: 'AppointmentNew', query: { client: c.name } }"
              class="inline-flex h-11 items-center gap-1.5 rounded-[10px] px-2 text-sm font-semibold text-[#A10E24] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
            >
              <CalendarPlus :size="17" /> Add session
            </router-link>
            <p v-if="c.case_status !== 'Closed' && hasScheduledAppointment" class="text-[13px] text-[#8A4B00]">
              Complete or cancel the scheduled appointment before adding another.
            </p>
          </div>

          <ul v-if="history.length" class="divide-y divide-[#E4E6EA]">
            <li v-for="a in history" :key="a.name">
              <router-link
                :to="{ name: a.status === 'Completed' || c.case_status === 'Closed' || (a.status === 'Scheduled' && (a.referral_history?.length || (a.counsellor_id !== c.assigned_counsellor && a.counsellor_id !== me.data?.user))) ? 'SessionRecord' : 'AppointmentEdit', params: { name: a.name } }"
                class="group flex items-center gap-4 px-5 py-4 transition hover:bg-[#F4F5F7]/70 focus-visible:bg-[#F4F5F7]/70 focus-visible:outline-none sm:px-6"
              >
                <span
                  class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                  :class="a.status === 'Completed' ? 'bg-[#DCF3E4] text-[#146C3A]' : a.overdue ? 'bg-[#FBE0E4] text-[#A10E24]' : 'bg-[#E0EAFD] text-[#1B4DB1]'"
                ><ClipboardCheck :size="19" /></span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold">{{ a.session_type }}</span>
                  <span class="mt-0.5 block text-[13px] text-[#5B616B]">
                    {{ fmtDateTime(a.date_time) }}<span v-if="a.mode_of_contact"> &middot; {{ a.mode_of_contact }}</span><span v-if="a.location"> &middot; {{ a.location }}</span>
                  </span>
                  <span v-for="referral in a.referral_history || []" :key="referral.name || referral.referred_on" class="mt-1 block text-xs text-[#3767A6]">
                    Referred from {{ referral.from_name }} to {{ referral.to_name }} · {{ fmtDateTime(referral.referred_on) }} — {{ referral.reason }}
                  </span>
                </span>
                <Badge :label="apptLabel(a)" :theme="apptTheme(a)" />
                <ChevronRight :size="18" class="hidden shrink-0 text-[#5B616B] transition group-hover:translate-x-0.5 group-hover:text-[#A10E24] sm:block" />
              </router-link>
            </li>
          </ul>

          <div v-else class="px-5 py-14 text-center">
            <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#5B616B]"><CalendarDays :size="22" /></span>
            <p class="mt-3 text-sm font-semibold">No sessions recorded yet</p>
            <p class="mx-auto mt-1 max-w-sm text-[13px] leading-5 text-[#5B616B]">Schedule an appointment to begin this client’s session history.</p>
            <router-link
              v-if="c.case_status !== 'Closed' && !hasScheduledAppointment"
              :to="{ name: 'AppointmentNew', query: { client: c.name } }"
              class="mt-5 inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#C8102E] bg-[#C8102E] px-[18px] text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40 focus-visible:ring-offset-2"
            >
              <CalendarPlus :size="18" /> Book appointment
            </router-link>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import {
	ArrowLeft, Building2, CalendarDays, CalendarPlus, ChevronRight, ClipboardCheck, ClipboardList,
	GraduationCap, Info, LockKeyhole, MapPin, Pencil, Phone, ShieldCheck, UserRound, UserRoundX,
} from "lucide-vue-next"
import { apptLabel, apptTheme, caseTheme, fmtDateTime } from "../data/format"
import { me } from "../data/me"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const clientName = computed(() => props.name || route.params.name)
const role = computed(() => me.data?.role)

const profile = createResource({ url: "krcti_mhpss.api.counsellor.client_profile" })
const load = () => profile.submit({ name: clientName.value })
onMounted(load)

const c = computed(() => profile.data?.client || {})
const s = computed(() => profile.data?.survey)
const history = computed(() => [...(profile.data?.appointments || [])].reverse())
const hasScheduledAppointment = computed(() => (profile.data?.appointments || []).some((appointment) => appointment.status === "Scheduled"))
const canClose = computed(
	() => c.value.case_status !== "Closed" &&
		(profile.data?.appointments || []).some((a) => a.session_type === "Termination" && a.status === "Completed"),
)

const initials = (fullName) => (fullName || "Client").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase()
const yes = (v) => (v ? "Yes" : "No")

// At-a-glance strip under the header
const glance = computed(() => {
	const list = history.value
	const completed = list.filter((a) => a.status === "Completed").length
	const survey = s.value
	const baseline = !survey ? "Not yet recorded" : survey.consent === "Declined" ? "Consent declined" : "Recorded"
	return [
		{ label: "Sessions recorded", value: list.length },
		{ label: "Sessions completed", value: completed },
		{ label: "Latest session", value: list.length ? fmtDateTime(list[0].date_time) : "None yet" },
		{ label: "Baseline survey", value: baseline, class: !survey ? "text-[#8A4B00]" : survey.consent === "Declined" ? "text-[#5B616B]" : "text-[#146C3A]" },
	]
})

// Client information, grouped so the record reads like a profile sheet rather than a wall of tiles
const detailGroups = computed(() => [
	{
		title: "Personal",
		hint: "Identity and circumstances",
		icon: UserRound,
		fields: [
			{ label: "Age", value: c.value.age },
			{ label: "Gender", value: c.value.gender },
			{ label: "Refugee status", value: yes(c.value.refugee_status) },
			{ label: "Disability", value: c.value.disability_status ? ["Yes", c.value.disability_type].filter(Boolean).join(": ") : "No", wide: true },
		],
	},
	{
		title: "Education",
		hint: "Institution and studies",
		icon: GraduationCap,
		fields: [
			{ label: "Institution", value: c.value.institution, wide: true },
			{ label: "Course / programme", value: c.value.course_programme, wide: true },
			{ label: "Year of study", value: c.value.year_of_study },
		],
	},
	{
		title: "Programme",
		hint: "Location and enrolment",
		icon: MapPin,
		fields: [
			{ label: "County", value: c.value.county_location },
			{ label: "Programme stream", value: c.value.programme_stream },
			{ label: "Registered by", value: c.value.registered_by_name || c.value.registered_by, wide: true },
			{ label: "Current case owner", value: c.value.assigned_counsellor_name || c.value.assigned_counsellor, wide: true },
			{ label: "Referral source", value: [c.value.referral_source, c.value.referral_source_other].filter(Boolean).join(": "), wide: true },
		],
	},
])

const survey = computed(() => {
	const x = s.value
	if (!x) return []
	if (x.consent === "Declined") return [["Consent", "Declined"], ["Reason", x.declined_reason || "Not recorded"]]
	return [
		["Consent", x.consent], ["Wellbeing self-rating", x.wellbeing_self_rating ? `${x.wellbeing_self_rating} / 10` : "Not recorded"], ["Recent stress", x.stress_frequency],
		["Main concerns", [x.main_concerns, x.main_concerns_other ? `Other: ${x.main_concerns_other}` : ""].filter(Boolean).join("; ")], ["Support available", x.support_availability], ["Coping ability", x.coping_ability],
		["Coping behaviour", x.coping_behaviour === "Other" ? `Other: ${x.coping_behaviour_other || "Not specified"}` : x.coping_behaviour], ["Interested in support", yes(x.interest_in_support)],
		["Support that would be most helpful", x.preferred_support_type], ["Willing to follow up", yes(x.willingness_for_followup)],
		["Marital status", x.marital_status], ["Dependants", x.dependants], ["Domestic situation", x.domestic_situation],
		["Conflict or disaster exposure", [x.conflict_exposure, x.exposure_details].filter(Boolean).join(": ")],
	]
})

const status = createResource({ url: "krcti_mhpss.api.records.set_case_status", onSuccess: load })
const setStatus = (value) => status.submit({ name: clientName.value, status: value })
function close() {
	if (window.confirm("Close this case? It becomes read-only. Only the System Administrator can re-open it.")) setStatus("Closed")
}
</script>
