<template>
  <main class="mx-auto max-w-3xl px-4 py-6 md:px-8 md:py-8">
    <router-link :to="{ name: 'Clients' }" class="text-sm text-gp">&larr; Clients</router-link>
    <PageLoader v-if="profile.loading && !profile.data" />
    <p v-else-if="profile.error && !profile.data" class="mt-4 rounded-lg border border-gp-line bg-white p-4 text-sm">This client could not be found.</p>

    <template v-else-if="profile.data">
      <div class="mt-2 flex flex-wrap items-center gap-2">
        <h1 class="text-xl font-semibold text-gp-ink">{{ c.full_name }}</h1>
        <Badge :label="c.case_status" :theme="caseTheme(c.case_status)" />
      </div>
      <p class="text-sm text-gp-muted">{{ c.scholar_code }} &middot; {{ c.name }}</p>

      <div class="mt-3 flex flex-wrap gap-2">
        <router-link :to="{ name: 'AppointmentNew', query: { client: c.name } }" class="rounded-md bg-gp px-3 py-2 text-sm font-medium text-white hover:bg-gp-light">Book an appointment</router-link>
        <router-link v-if="c.case_status !== 'Closed' || role === 'admin'" :to="{ name: 'ClientEdit', params: { name: c.name } }" class="rounded-md border border-gp-line bg-white px-3 py-2 text-sm font-medium text-gp hover:border-gp">Edit details</router-link>
        <router-link v-if="!s && c.case_status !== 'Closed'" :to="{ name: 'Baseline', params: { name: c.name } }" class="rounded-md border border-gp-line bg-white px-3 py-2 text-sm font-medium text-gp hover:border-gp">Record baseline survey</router-link>
      </div>

      <section class="mt-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Details</h2>
        <dl class="mt-3 grid gap-x-4 gap-y-3 text-sm sm:grid-cols-2">
          <div v-for="[label, value] in details" :key="label">
            <dt class="text-gp-muted">{{ label }}</dt>
            <dd class="text-gp-ink">{{ value }}</dd>
          </div>
        </dl>
      </section>

      <section class="mt-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Case</h2>
        <div class="mt-3 flex flex-wrap gap-2">
          <Button v-if="c.case_status === 'Active'" :loading="status.loading" @click="setStatus('Follow-Up Pending')">Mark follow-up pending</Button>
          <Button v-if="c.case_status === 'Follow-Up Pending'" :loading="status.loading" @click="setStatus('Active')">Mark active</Button>
          <Button v-if="canClose" theme="red" :loading="status.loading" @click="close">Close this case</Button>
          <Button v-if="c.case_status === 'Closed' && role === 'admin'" :loading="status.loading" @click="setStatus('Active')">Re-open the case</Button>
        </div>
        <p v-if="!canClose && c.case_status !== 'Closed'" class="mt-2 text-xs text-gp-muted">A case can be closed after a completed Termination session.</p>
        <ErrorMessage class="mt-2" :message="status.error" />
      </section>

      <section class="mt-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Baseline survey</h2>
        <p v-if="!s" class="mt-2 text-sm text-gp-muted">Not recorded yet.</p>
        <template v-else>
          <p class="mt-1 text-xs text-gp-muted">Read-only. Recorded {{ fmtDateTime(s.completed_on) }}.</p>
          <dl class="mt-3 grid gap-x-4 gap-y-3 text-sm sm:grid-cols-2">
            <div v-for="[label, value] in survey" :key="label">
              <dt class="text-gp-muted">{{ label }}</dt>
              <dd class="whitespace-pre-line text-gp-ink">{{ value }}</dd>
            </div>
          </dl>
        </template>
      </section>

      <section class="mt-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Sessions</h2>
        <p v-if="!profile.data.appointments.length" class="mt-2 text-sm text-gp-muted">No sessions yet.</p>
        <ol v-else class="mt-3 space-y-3">
          <li v-for="a in history" :key="a.name" class="flex items-start justify-between gap-3 text-sm">
            <router-link :to="{ name: 'AppointmentEdit', params: { name: a.name } }" class="min-w-0">
              <span class="block font-medium text-gp-ink">{{ fmtDateTime(a.date_time) }}</span>
              <span class="block text-xs text-gp-muted">{{ a.session_type }} &middot; {{ a.mode_of_contact }}<span v-if="a.location"> &middot; {{ a.location }}</span></span>
            </router-link>
            <Badge :label="apptLabel(a)" :theme="apptTheme(a)" />
          </li>
        </ol>
      </section>
    </template>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted } from "vue"
import { useRoute } from "vue-router"
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
// Oldest first, so the history reads in the order it happened.
const history = computed(() => [...(profile.data?.appointments || [])].reverse())
const canClose = computed(
	() => c.value.case_status !== "Closed" &&
		(profile.data?.appointments || []).some((a) => a.session_type === "Termination" && a.status === "Completed"),
)

const yes = (v) => (v ? "Yes" : "No")
const details = computed(() => [
	["Phone", c.value.phone_number], ["Age", c.value.age], ["Gender", c.value.gender], ["Sex", c.value.sex],
	["Disability", c.value.disability_status ? `Yes: ${c.value.disability_type}` : "No"], ["Refugee", yes(c.value.refugee_status)],
	["Institution", c.value.institution], ["Course", c.value.course_programme], ["Year of study", c.value.year_of_study],
	["County", c.value.county_location], ["Programme stream", c.value.programme_stream],
	["Referral source", [c.value.referral_source, c.value.referral_source_other].filter(Boolean).join(": ")],
])
const survey = computed(() => {
	const x = s.value
	if (!x) return []
	if (x.consent === "Declined") return [["Consent", "Declined"], ["Reason", x.declined_reason || "-"]]
	return [
		["Consent", x.consent], ["Wellbeing self-rating", `${x.wellbeing_self_rating} / 10`], ["Recent stress", x.stress_frequency],
		["Main concerns", x.main_concerns], ["Support available", x.support_availability], ["Coping ability", x.coping_ability],
		["Coping behaviour", x.coping_behaviour], ["Interested in support", yes(x.interest_in_support)],
		["Preferred support", x.preferred_support_type], ["Willing to follow up", yes(x.willingness_for_followup)],
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