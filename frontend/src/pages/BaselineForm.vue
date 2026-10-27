<template>
  <main class="mx-auto max-w-2xl px-4 py-6 md:px-8 md:py-8">
    <router-link :to="{ name: 'ClientProfile', params: { name: clientName } }" class="text-sm text-gp">&larr; Back to the client</router-link>
    <h1 class="mt-1 text-xl font-semibold text-gp-ink">Baseline survey</h1>
    <PageLoader v-if="profile.loading && !profile.data" />

    <p v-else-if="profile.data?.survey" class="mt-4 rounded-lg border border-gp-line bg-white p-4 text-sm text-gp-ink">
      A baseline survey already exists for this client. Only one is allowed, and it is locked once submitted.
    </p>

    <form v-else-if="profile.data" class="mt-4 space-y-5" @submit.prevent="submit">
      <p class="text-sm text-gp-muted">For {{ profile.data.client.full_name }} ({{ profile.data.client.scholar_code }}). You enter this on the client's behalf.</p>

      <section class="space-y-3 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Consent</h2>
        <FormControl label="Does the client consent to the baseline survey?" type="select" :options="consentOptions" v-model="form.consent" />
        <FormControl v-if="form.consent === 'Declined'" label="Reason (optional)" type="textarea" v-model="form.declined_reason" />
        <p v-if="form.consent === 'Declined'" class="text-xs text-gp-muted">Declining is recorded. You can still book and record sessions without baseline data.</p>
      </section>

      <template v-if="form.consent === 'Consented'">
        <section class="space-y-4 rounded-lg border border-gp-line bg-white p-5">
          <h2 class="font-semibold text-gp-ink">Wellbeing</h2>
          <FormControl label="Wellbeing self-rating (1 lowest, 10 highest)" type="select" :options="RATINGS" v-model="form.wellbeing_self_rating" />
          <FormControl label="Recent stress frequency" type="select" :options="STRESS" v-model="form.stress_frequency" />
          <FormControl label="Main concerns" type="textarea" v-model="form.main_concerns" />
          <FormControl label="Support available to the client" type="select" :options="SUPPORT" v-model="form.support_availability" />
          <FormControl label="Coping ability" type="select" :options="COPING" v-model="form.coping_ability" />
          <FormControl label="Coping behaviour" type="textarea" v-model="form.coping_behaviour" />
        </section>
        <section class="space-y-4 rounded-lg border border-gp-line bg-white p-5">
          <h2 class="font-semibold text-gp-ink">Support</h2>
          <FormControl type="checkbox" label="Interested in MHPSS support" v-model="form.interest_in_support" />
          <FormControl label="Preferred support type" type="select" :options="SUPPORT_TYPES" v-model="form.preferred_support_type" />
          <FormControl type="checkbox" label="Willing to take part in follow-up" v-model="form.willingness_for_followup" />
        </section>
        <section class="space-y-4 rounded-lg border border-gp-line bg-white p-5">
          <h2 class="font-semibold text-gp-ink">Family background</h2>
          <FormControl label="Marital status" type="select" :options="MARITAL" v-model="form.marital_status" />
          <FormControl label="Number of dependants" type="number" v-model="form.dependants" />
          <FormControl label="Domestic situation" type="textarea" v-model="form.domestic_situation" />
          <FormControl label="Exposure to conflict or disaster" type="select" :options="EXPOSURE" v-model="form.conflict_exposure" />
          <FormControl v-if="form.conflict_exposure === 'Yes'" label="Details" type="textarea" v-model="form.exposure_details" />
        </section>
      </template>

      <ErrorMessage :message="saver.error" />
      <Button v-if="form.consent" type="submit" variant="solid" class="w-full !bg-gp hover:!bg-gp-light sm:w-auto" :loading="saver.loading">
        {{ form.consent === "Declined" ? "Record the declination" : "Submit survey" }}
      </Button>
      <p v-if="form.consent === 'Consented'" class="text-xs text-gp-muted">Once submitted, the survey is locked. Only the System Administrator can change it.</p>
    </form>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, reactive } from "vue"
import { useRoute, useRouter } from "vue-router"
import { COPING, EXPOSURE, MARITAL, RATINGS, STRESS, SUPPORT, SUPPORT_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name)

const consentOptions = [
	{ label: "Select", value: "" },
	{ label: "Consented", value: "Consented" },
	{ label: "Declined", value: "Declined" },
]
const TEXT = ["declined_reason", "stress_frequency", "main_concerns", "support_availability", "coping_ability",
	"coping_behaviour", "preferred_support_type", "marital_status", "domestic_situation", "conflict_exposure", "exposure_details"]
const form = reactive({
	consent: "", wellbeing_self_rating: "", dependants: "",
	interest_in_support: false, willingness_for_followup: false,
	...Object.fromEntries(TEXT.map((k) => [k, ""])),
})

const profile = createResource({ url: "krcti_mhpss.api.counsellor.client_profile" })
onMounted(() => profile.submit({ name: clientName.value }))

const saver = createResource({
	url: "krcti_mhpss.api.records.record_baseline",
	onSuccess() {
		router.replace({ name: "ClientProfile", params: { name: clientName.value } })
	},
})

function submit() {
	const data = { consent: form.consent }
	if (form.consent === "Declined") {
		data.declined_reason = form.declined_reason
	} else {
		for (const k of TEXT) data[k] = form[k]
		data.wellbeing_self_rating = form.wellbeing_self_rating === "" ? "" : Number(form.wellbeing_self_rating)
		data.dependants = form.dependants === "" ? 0 : Number(form.dependants)
		data.interest_in_support = form.interest_in_support ? 1 : 0
		data.willingness_for_followup = form.willingness_for_followup ? 1 : 0
	}
	saver.submit({ client: clientName.value, data })
}
</script>