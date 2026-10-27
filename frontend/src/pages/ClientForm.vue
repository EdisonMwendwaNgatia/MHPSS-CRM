<template>
  <main class="mx-auto max-w-2xl px-4 py-6 md:px-8 md:py-8">
    <router-link :to="back" class="text-sm text-gp">&larr; Back</router-link>
    <h1 class="mt-1 text-xl font-semibold text-gp-ink">{{ isNew ? "Register a client" : "Edit client details" }}</h1>
    <PageLoader v-if="loading" />

    <form v-else class="mt-4 space-y-5" @submit.prevent="save">
      <section class="space-y-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Client</h2>
        <FormControl label="Scholar/Participant Code" type="text" v-model="form.scholar_code" :disabled="!isNew" placeholder="Issued by the WoC programme" />
        <FormControl label="Full name" type="text" v-model="form.full_name" />
        <FormControl label="Phone number" type="text" v-model="form.phone_number" placeholder="0712 345 678" />
        <div class="grid grid-cols-3 gap-3">
          <FormControl label="Age" type="number" v-model="form.age" />
          <FormControl label="Gender" type="select" :options="GENDERS" v-model="form.gender" />
          <FormControl label="Sex" type="select" :options="GENDERS" v-model="form.sex" />
        </div>
        <FormControl type="checkbox" label="Person with a disability" v-model="form.disability_status" />
        <FormControl v-if="form.disability_status" label="Type of disability" type="text" v-model="form.disability_type" />
        <FormControl type="checkbox" label="Refugee" v-model="form.refugee_status" />
      </section>

      <section class="space-y-4 rounded-lg border border-gp-line bg-white p-5">
        <h2 class="font-semibold text-gp-ink">Education and programme</h2>
        <FormControl label="College or learning institution" type="text" v-model="form.institution" />
        <FormControl label="Course or programme" type="text" v-model="form.course_programme" />
        <div class="grid grid-cols-2 gap-3">
          <FormControl label="Year of study" type="number" v-model="form.year_of_study" />
          <FormControl label="County location" type="text" v-model="form.county_location" />
        </div>
        <FormControl label="WoC programme stream" type="select" :options="STREAMS" v-model="form.programme_stream" />
        <FormControl label="Referral source" type="select" :options="REFERRALS" v-model="form.referral_source" />
        <FormControl v-if="form.referral_source === 'Other'" label="Describe the referral source" type="text" v-model="form.referral_source_other" />
      </section>

      <ErrorMessage :message="saver.error" />
      <Button type="submit" variant="solid" class="w-full !bg-gp hover:!bg-gp-light sm:w-auto" :loading="saver.loading">
        {{ isNew ? "Register client" : "Save changes" }}
      </Button>
    </form>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { GENDERS, REFERRALS, STREAMS } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !clientName.value)
const back = computed(() => (isNew.value ? { name: "Clients" } : { name: "ClientProfile", params: { name: clientName.value } }))

const TEXT = ["scholar_code", "full_name", "phone_number", "gender", "sex", "disability_type", "institution",
	"course_programme", "county_location", "programme_stream", "referral_source", "referral_source_other"]
const NUMBERS = ["age", "year_of_study"]
const CHECKS = ["disability_status", "refugee_status"]

const form = reactive({
	...Object.fromEntries([...TEXT, ...NUMBERS].map((k) => [k, ""])),
	disability_status: false,
	refugee_status: false,
})
const loading = ref(false)

const profile = createResource({
	url: "krcti_mhpss.api.counsellor.client_profile",
	onSuccess(data) {
		const c = data.client
		for (const k of [...TEXT, ...NUMBERS]) form[k] = c[k] ?? ""
		for (const k of CHECKS) form[k] = !!c[k]
		loading.value = false
	},
})

onMounted(() => {
	if (!isNew.value) {
		loading.value = true
		profile.submit({ name: clientName.value })
	}
})

const saver = createResource({
	url: "krcti_mhpss.api.records.save_client",
	onSuccess(result) {
		router.replace({ name: "ClientProfile", params: { name: result.name } })
	},
})
const updater = saver // the template may still mention it

function values() {
	const data = {}
	for (const k of TEXT) data[k] = form[k]
	for (const k of NUMBERS) data[k] = form[k] === "" ? "" : Number(form[k])
	for (const k of CHECKS) data[k] = form[k] ? 1 : 0
	return data
}

function save() {
	const data = values()
	if (!isNew.value) delete data.scholar_code // the code never changes
	saver.submit({ name: clientName.value || undefined, data })
}
</script>