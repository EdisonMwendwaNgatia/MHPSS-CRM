<template>
	<main class="mx-auto max-w-7xl px-4 py-6 md:px-7 md:py-8">
		<div class="mb-5 text-sm text-[#5B616B]">
			<router-link :to="{ name: 'Clients' }" class="hover:text-[#A10E24]">Clients</router-link>
			<span class="px-2">/</span>
			<router-link :to="{ name: 'ClientProfile', params: { name: clientName } }" class="hover:text-[#A10E24]">
				{{ profile.data?.client?.scholar_code || 'Client' }}
			</router-link>
			<span class="px-2">/</span><span class="font-semibold text-[#2B2F36]">Baseline Survey</span>
		</div>

		<PageLoader v-if="profile.loading && !profile.data" />
		<template v-else-if="profile.data">
			<div class="mb-5 flex flex-wrap items-start justify-between gap-4">
				<div>
					<h1 class="text-2xl font-semibold leading-8 text-[#2B2F36]">Baseline Survey</h1>
					<p class="mt-1 text-sm text-[#5B616B]">
						{{ profile.data.client.scholar_code }} · {{ profile.data.client.full_name }}
						<span v-if="profile.data.client.assigned_counsellor">· Counsellor: {{ profile.data.client.assigned_counsellor }}</span>
					</p>
				</div>
				<div class="flex items-center gap-2 rounded-lg border border-[#E4E6EA] bg-white px-3 py-2 text-sm text-[#5B616B]">
					<svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
						<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>
					</svg>
					Confidential · counsellor access only
				</div>
			</div>

			<div v-if="profile.data.survey" class="rounded-xl border border-[#E4E6EA] bg-white p-6">
				<div class="mb-3 inline-flex rounded-full bg-[#E0EAFD] px-3 py-1 text-xs font-semibold text-[#1B4DB1]">Read only</div>
				<h2 class="text-lg font-semibold text-[#2B2F36]">Baseline survey already recorded</h2>
				<p class="mt-1 text-sm text-[#5B616B]">Only one baseline survey is allowed for this client, and it is locked once submitted.</p>
				<div class="mt-5 grid gap-3 sm:grid-cols-2">
					<div class="rounded-lg bg-[#F4F5F7] p-4 text-sm"><span class="block text-xs text-[#5B616B]">Consent</span><span class="mt-1 block font-medium">{{ profile.data.survey.consent }}</span></div>
					<div v-if="profile.data.survey.wellbeing_self_rating" class="rounded-lg bg-[#F4F5F7] p-4 text-sm"><span class="block text-xs text-[#5B616B]">Wellbeing self-rating</span><span class="mt-1 block font-medium">{{ profile.data.survey.wellbeing_self_rating }} / 10</span></div>
				</div>
			</div>

			<template v-else>
				<section class="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white px-5 py-4" aria-label="Survey consent">
					<div class="text-sm text-[#2B2F36]">
						<strong class="mr-1">Consent:</strong>
						<span v-if="form.consent === 'Consented'">The client has agreed to take part in the baseline survey.</span>
						<span v-else-if="form.consent === 'Declined'">The client has declined to take part in the baseline survey.</span>
						<span v-else>Please record the client’s consent before continuing.</span>
					</div>
					<div class="flex flex-wrap items-center gap-3">
						<span v-if="form.consent === 'Consented'" class="rounded-full bg-[#DCF3E4] px-3 py-1 text-xs font-semibold text-[#146C3A]">Consent confirmed</span>
						<span v-else-if="form.consent === 'Declined'" class="rounded-full bg-[#FDECC8] px-3 py-1 text-xs font-semibold text-[#8A4B00]">Consent declined</span>
						<FormControl v-if="!form.consent" label="Consent decision" type="select" :options="consentOptions" v-model="form.consent" />
						<button v-else type="button" class="text-sm font-semibold text-[#A10E24] hover:underline" @click="changeConsent">
							{{ form.consent === 'Consented' ? 'Client declines instead' : 'Change consent' }}
						</button>
					</div>
				</section>

				<section v-if="form.consent === 'Declined'" class="rounded-xl border border-[#E4E6EA] bg-white p-5 md:p-6">
					<h2 class="text-lg font-semibold text-[#2B2F36]">Record declined consent</h2>
					<p class="mb-5 mt-1 text-sm text-[#5B616B]">Declining is recorded. The client can still receive and record support sessions.</p>
					<FormControl label="Reason (optional)" type="textarea" v-model="form.declined_reason" />
					<ErrorMessage class="mt-4" :message="saver.error" />
					<div class="mt-5 flex justify-end">
						<Button type="button" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="saver.loading" @click="submit">
							Record the declination
						</Button>
					</div>
				</section>

				<div v-else-if="form.consent === 'Consented'" class="flex items-start gap-5 max-[800px]:flex-col">
					<nav class="w-[280px] shrink-0 rounded-xl border border-[#E4E6EA] bg-white p-5 max-[800px]:w-full" aria-label="Survey sections">
						<div class="mb-2 text-xs text-[#5B616B]">Section {{ step }} of {{ sections.length }} · {{ Math.round((step / sections.length) * 100) }}% complete</div>
						<div class="mb-4 h-2 overflow-hidden rounded-full bg-[#E4E6EA]">
							<div class="h-full rounded-full bg-[#C8102E] transition-all" :style="{ width: `${(step / sections.length) * 100}%` }"></div>
						</div>
						<ol class="space-y-1">
							<li v-for="(section, index) in sections" :key="section.title">
								<button type="button" class="flex min-h-10 w-full items-center gap-2.5 rounded-lg px-2 text-left text-sm transition-colors"
									:class="step === index + 1 ? 'font-semibold text-[#A10E24]' : 'text-[#4A505A] hover:bg-[#F4F5F7]'"
									:aria-current="step === index + 1 ? 'step' : undefined" @click="goTo(index + 1)">
									<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
										:class="index + 1 < step ? 'bg-[#DCF3E4] text-[#146C3A]' : step === index + 1 ? 'bg-[#C8102E] text-white' : 'bg-[#E4E6EA] text-[#3A3F47]'">
										<svg v-if="index + 1 < step" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg>
										<template v-else>{{ index + 1 }}</template>
									</span>
									{{ section.title }}
								</button>
							</li>
						</ol>
					</nav>

					<form class="min-w-0 flex-1 rounded-xl border border-[#E4E6EA] bg-white p-5 md:p-6" @submit.prevent="step === sections.length ? submit() : next()">
						<h2 class="text-lg font-semibold text-[#2B2F36]">{{ currentSection.heading }}</h2>
						<p v-if="currentSection.description" class="mb-6 mt-1 text-sm text-[#5B616B]">{{ currentSection.description }}</p>

						<div v-if="step === 1" class="grid gap-4 sm:grid-cols-2">
							<div v-for="item in clientSummary" :key="item.label" class="rounded-lg bg-[#F4F5F7] p-4">
								<span class="block text-xs text-[#5B616B]">{{ item.label }}</span>
								<span class="mt-1 block text-sm font-medium text-[#2B2F36]">{{ item.value || 'Not recorded' }}</span>
							</div>
						</div>
						<div v-else-if="step === 2" class="max-w-xl">
							<FormControl label="Wellbeing self-rating (1 lowest, 10 highest)" type="select" :options="RATINGS" v-model="form.wellbeing_self_rating" />
						</div>
						<div v-else-if="step === 3" class="max-w-xl">
							<fieldset class="mb-6 border-0 p-0">
								<legend class="mb-3 text-sm font-medium text-[#2B2F36]">How often has the client felt stressed recently?</legend>
								<label v-for="option in STRESS.filter((item) => item.value)" :key="option.value" class="mb-2 flex min-h-11 cursor-pointer items-center gap-3 rounded-[10px] border border-[#D5D8DE] px-3.5 text-sm hover:border-[#C8102E]">
									<input v-model="form.stress_frequency" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" :value="option.value" />{{ option.label }}
								</label>
							</fieldset>
						</div>
						<div v-else-if="step === 4" class="max-w-xl">
							<FormControl label="Main concerns" type="textarea" v-model="form.main_concerns" />
						</div>
						<div v-else-if="step === 5" class="max-w-xl">
							<FormControl label="Support available to the client" type="select" :options="SUPPORT" v-model="form.support_availability" />
						</div>
						<div v-else-if="step === 6" class="max-w-xl space-y-5">
							<FormControl label="Coping ability" type="select" :options="COPING" v-model="form.coping_ability" />
							<FormControl label="Coping behaviour" type="textarea" v-model="form.coping_behaviour" />
						</div>
						<div v-else-if="step === 7" class="max-w-xl space-y-5">
							<FormControl type="checkbox" label="Interested in MHPSS support" v-model="form.interest_in_support" />
							<FormControl label="Preferred support type" type="select" :options="SUPPORT_TYPES" v-model="form.preferred_support_type" />
							<FormControl type="checkbox" label="Willing to take part in follow-up" v-model="form.willingness_for_followup" />
						</div>
						<div v-else class="max-w-xl space-y-5">
							<FormControl label="Marital status" type="select" :options="MARITAL" v-model="form.marital_status" />
							<FormControl label="Number of dependants" type="number" v-model="form.dependants" />
							<FormControl label="Domestic situation" type="textarea" v-model="form.domestic_situation" />
							<FormControl label="Exposure to conflict or disaster" type="select" :options="EXPOSURE" v-model="form.conflict_exposure" />
							<FormControl v-if="form.conflict_exposure === 'Yes'" label="Exposure details" type="textarea" v-model="form.exposure_details" />
						</div>

						<ErrorMessage class="mt-5" :message="saver.error" />
						<p v-if="step === sections.length" class="mt-5 text-xs text-[#5B616B]">Once submitted, the survey is locked. Only a System Manager can change it.</p>
						<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E4E6EA] pt-5">
							<Button type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#2B2F36]" :disabled="step === 1" @click="previous">Previous</Button>
							<Button type="submit" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="saver.loading">
								{{ step === sections.length ? 'Submit survey' : 'Next' }}
							</Button>
						</div>
					</form>
				</div>
			</template>
		</template>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { COPING, EXPOSURE, MARITAL, RATINGS, STRESS, SUPPORT, SUPPORT_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name)
const step = ref(1)

const sections = [
	{ title: "Student information", heading: "Student information", description: "Confirm the client record before beginning the survey." },
	{ title: "Wellbeing", heading: "Section 2: Wellbeing", description: "Record the client’s current self-rating." },
	{ title: "Stress frequency", heading: "Section 3: Stress frequency", description: "How often has the client felt stressed recently?" },
	{ title: "Concerns", heading: "Section 4: Concerns", description: "Record the concerns shared by the client." },
	{ title: "Support systems", heading: "Section 5: Support systems", description: "Record the support currently available to the client." },
	{ title: "Coping mechanisms", heading: "Section 6: Coping mechanisms", description: "Record how the client is coping and the strategies they use." },
	{ title: "Interest in MHPSS support", heading: "Section 7: Interest in MHPSS support", description: "Record the client’s support preferences and follow-up consent." },
	{ title: "Family background", heading: "Section 8: Family background", description: "Record the family and home context shared by the client." },
]
const currentSection = computed(() => sections[step.value - 1])
const consentOptions = [
	{ label: "Select consent decision", value: "" },
	{ label: "Client consented", value: "Consented" },
	{ label: "Client declined", value: "Declined" },
]
const form = reactive({
	consent: "", wellbeing_self_rating: "", dependants: "", interest_in_support: false, willingness_for_followup: false,
	declined_reason: "", stress_frequency: "", main_concerns: "", support_availability: "", coping_ability: "",
	coping_behaviour: "", preferred_support_type: "", marital_status: "", domestic_situation: "", conflict_exposure: "", exposure_details: "",
})

const profile = createResource({ url: "krcti_mhpss.api.counsellor.client_profile" })
onMounted(() => profile.submit({ name: clientName.value }))

const saver = createResource({
	url: "krcti_mhpss.api.records.record_baseline",
	onSuccess() {
		router.replace({ name: "ClientProfile", params: { name: clientName.value } })
	},
})

const clientSummary = computed(() => {
	const client = profile.data?.client || {}
	return [
		{ label: "Participant code", value: client.scholar_code },
		{ label: "Full name", value: client.full_name },
		{ label: "Institution", value: client.institution },
		{ label: "Course / programme", value: client.course_programme },
		{ label: "Year of study", value: client.year_of_study },
		{ label: "Programme stream", value: client.programme_stream },
	]
})

function goTo(target) {
	if (target <= step.value || target === step.value + 1) step.value = target
}
function next() {
	if (step.value < sections.length) step.value += 1
}
function previous() {
	if (step.value > 1) step.value -= 1
}
function changeConsent() {
	form.consent = form.consent === "Consented" ? "Declined" : ""
}
function submit() {
	const data = { consent: form.consent }
	if (form.consent === "Declined") {
		data.declined_reason = form.declined_reason
	} else {
		for (const key of ["stress_frequency", "main_concerns", "support_availability", "coping_ability", "coping_behaviour", "preferred_support_type", "marital_status", "domestic_situation", "conflict_exposure", "exposure_details"]) {
			data[key] = form[key]
		}
		data.wellbeing_self_rating = form.wellbeing_self_rating === "" ? "" : Number(form.wellbeing_self_rating)
		data.dependants = form.dependants === "" ? 0 : Number(form.dependants)
		data.interest_in_support = form.interest_in_support ? 1 : 0
		data.willingness_for_followup = form.willingness_for_followup ? 1 : 0
	}
	saver.submit({ client: clientName.value, data })
}
</script>
