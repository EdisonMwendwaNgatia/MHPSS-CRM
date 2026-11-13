<template>
	<main class="mx-auto max-w-7xl px-4 py-6 md:px-7 md:py-8">
		<div class="mb-5 text-sm text-[#5B616B]">
			<router-link v-if="!isPublic && !isProgrammeFill" :to="{ name: 'Clients' }" class="hover:text-[#A10E24]">Clients</router-link>
			<router-link v-else-if="isProgrammeFill" :to="{ name: 'ProgrammeClientDetail', params: { name: clientName } }" class="hover:text-[#A10E24]">Programme client</router-link>
			<span class="px-2">/</span>
			<router-link v-if="!isPublic && !isProgrammeFill" :to="{ name: 'ClientProfile', params: { name: clientName } }" class="hover:text-[#A10E24]">
				{{ profile.data?.client?.scholar_code || 'Client' }}
			</router-link>
			<span v-else class="font-semibold text-[#2B2F36]">{{ profile.data?.client?.scholar_code || 'Client' }}</span>
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
					{{ isPublic ? 'Secure one-time form · submission locks this cycle' : isProgrammeFill ? `Programme Manager entry · cycle ${profile.data.cycle}` : 'Confidential · counsellor access only' }}
				</div>
			</div>

			<div v-if="profile.data.survey" class="rounded-xl border border-[#E4E6EA] bg-white p-6">
				<div class="mb-3 inline-flex rounded-full bg-[#E0EAFD] px-3 py-1 text-xs font-semibold text-[#1B4DB1]">Read only</div>
				<h2 class="text-lg font-semibold text-[#2B2F36]">{{ isPublic ? 'Thank you — your baseline survey was submitted' : 'Baseline survey already recorded' }}</h2>
				<p class="mt-1 text-sm text-[#5B616B]">This form cycle has been submitted and is locked.</p>
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
					<ErrorMessage class="mt-4" :message="activeSaver.error" />
					<div class="mt-5 flex justify-end">
						<Button type="button" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="activeSaver.loading" @click="submit">
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
							<p v-if="fieldErrors.wellbeing_self_rating" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.wellbeing_self_rating }}</p>
						</div>
						<div v-else-if="step === 3" class="max-w-xl">
							<fieldset class="mb-6 border-0 p-0">
								<legend class="mb-3 text-sm font-medium text-[#2B2F36]">How often has the client felt stressed recently?</legend>
								<label v-for="option in STRESS.filter((item) => item.value)" :key="option.value" class="mb-2 flex min-h-11 cursor-pointer items-center gap-3 rounded-[10px] border border-[#D5D8DE] px-3.5 text-sm hover:border-[#C8102E]">
									<input v-model="form.stress_frequency" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" :value="option.value" />{{ option.label }}
								</label>
							</fieldset>
							<p v-if="fieldErrors.stress_frequency" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.stress_frequency }}</p>
						</div>
						<div v-else-if="step === 4" class="max-w-xl">
							<fieldset class="border-0 p-0">
								<legend class="mb-3 text-sm font-medium text-[#2B2F36]">Presenting concerns <span class="font-normal text-[#5B616B]">(select all that apply)</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="concern in mainConcernOptions" :key="concern" class="flex min-h-11 cursor-pointer items-center gap-3 rounded-[10px] border border-[#D5D8DE] px-3.5 text-sm transition hover:border-[#C8102E]" :class="selectedMainConcerns.includes(concern) ? 'border-[#C8102E] bg-[#FFF8F9]' : 'bg-white'">
										<input v-model="selectedMainConcerns" class="h-[18px] w-[18px] accent-[#C8102E]" type="checkbox" :value="concern" @change="syncConcernDetails" />
										{{ concern }}
									</label>
								</div>
							</fieldset>
							<p v-if="fieldErrors.main_concerns" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.main_concerns }}</p>
							<FormControl v-if="selectedMainConcerns.includes('Other')" label="Describe the other concern" type="textarea" v-model="form.main_concerns_other" />
							<p v-if="fieldErrors.main_concerns_other" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.main_concerns_other }}</p>
						</div>
						<div v-else-if="step === 5" class="max-w-xl space-y-5">
							<FormControl label="Support available to the client" type="select" :options="SUPPORT" v-model="form.support_availability" />
							<p v-if="fieldErrors.support_availability" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.support_availability }}</p>
							<FormControl label="What type of support will be more helpful?" type="select" :options="SUPPORT_TYPES" v-model="form.preferred_support_type" />
							<p v-if="fieldErrors.preferred_support_type" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.preferred_support_type }}</p>
						</div>
						<div v-else-if="step === 6" class="max-w-xl space-y-5">
							<FormControl label="Coping ability" type="select" :options="COPING" v-model="form.coping_ability" />
							<p v-if="fieldErrors.coping_ability" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.coping_ability }}</p>
							<FormControl label="Coping behaviour" type="select" :options="COPING_BEHAVIOURS" v-model="form.coping_behaviour" @update:model-value="formError = ''" />
							<p v-if="fieldErrors.coping_behaviour" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.coping_behaviour }}</p>
							<FormControl v-if="form.coping_behaviour === 'Other'" label="Specify the coping mechanism" type="textarea" v-model="form.coping_behaviour_other" />
							<p v-if="fieldErrors.coping_behaviour_other" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.coping_behaviour_other }}</p>
						</div>
						<div v-else-if="step === 7" class="max-w-xl space-y-5">
							<FormControl type="checkbox" label="Interested in MHPSS support" v-model="form.interest_in_support" />
							<FormControl type="checkbox" label="Willing to take part in follow-up" v-model="form.willingness_for_followup" />
						</div>
						<div v-else class="max-w-xl space-y-5">
							<FormControl label="Marital status" type="select" :options="MARITAL" v-model="form.marital_status" />
							<p v-if="fieldErrors.marital_status" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.marital_status }}</p>
							<FormControl label="Number of dependants" type="number" v-model="form.dependants" />
							<p v-if="fieldErrors.dependants" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.dependants }}</p>
							<FormControl label="Domestic situation" type="textarea" v-model="form.domestic_situation" />
							<p v-if="fieldErrors.domestic_situation" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.domestic_situation }}</p>
							<FormControl label="Exposure to conflict or disaster" type="select" :options="EXPOSURE" v-model="form.conflict_exposure" />
							<p v-if="fieldErrors.conflict_exposure" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.conflict_exposure }}</p>
							<FormControl v-if="form.conflict_exposure === 'Yes'" label="Exposure details" type="textarea" v-model="form.exposure_details" />
						</div>

						<p v-if="formError" class="mt-5 text-sm text-[#A10E24]" role="alert">{{ formError }}</p>
						<ErrorMessage class="mt-5" :message="activeSaver.error" />
						<p v-if="step === sections.length" class="mt-5 text-xs text-[#5B616B]">This form cycle can be submitted once. Review your answers carefully before continuing.</p>
						<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E4E6EA] pt-5">
							<Button type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#2B2F36]" :disabled="step === 1" @click="previous">Previous</Button>
							<Button type="submit" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="activeSaver.loading">
								{{ step === sections.length ? 'Submit survey' : 'Next' }}
							</Button>
						</div>
					</form>
				</div>
			</template>
		</template>
		<ErrorMessage v-if="!profile.loading && !profile.data" :message="profile.error || programmeContext.error || publicContext.error || 'The baseline form could not be loaded.'" />
		<div v-if="confirmOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-[#17191D]/45 p-4" @click.self="confirmOpen = false">
			<section class="w-full max-w-md rounded-xl bg-white p-5 shadow-xl" role="alertdialog" aria-modal="true" aria-labelledby="submit-confirm-title">
				<h2 id="submit-confirm-title" class="text-lg font-semibold text-[#25272B]">Submit baseline survey?</h2>
				<p class="mt-2 text-sm leading-6 text-[#555860]">You can submit this form only once for this cycle. Please review your answers carefully. After submission, the form will be locked and cannot be edited.</p>
				<div class="mt-5 flex justify-end gap-2">
					<Button type="button" class="!h-10 !rounded-lg !border-[#D5D8DE] !bg-white !text-[#33353A]" @click="confirmOpen = false">Review answers</Button>
					<Button type="button" variant="solid" class="!h-10 !rounded-lg !bg-[#C8102E] px-4 hover:!bg-[#A10E24]" :loading="activeSaver.loading" @click="confirmSubmit">Confirm submit</Button>
				</div>
			</section>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { COPING, COPING_BEHAVIOURS, EXPOSURE, MARITAL, RATINGS, STRESS, SUPPORT, SUPPORT_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name)
const token = computed(() => String(route.params.token || ""))
const isPublic = computed(() => !!token.value)
const isProgrammeFill = computed(() => route.name === "ProgrammeBaseline")
const step = ref(1)
const formError = ref("")
const confirmOpen = ref(false)
const surveyId = ref("")
const fieldErrors = reactive({})

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
const mainConcernOptions = [
	"Academic pressure", "Financial challenges", "Family issues", "Relationships",
	"Loneliness", "Health Concerns", "Substance/Gambling", "Other",
]
const currentSection = computed(() => sections[step.value - 1])
const consentOptions = [
	{ label: "Select consent decision", value: "" },
	{ label: "Client consented", value: "Consented" },
	{ label: "Client declined", value: "Declined" },
]
const form = reactive({
	consent: "", wellbeing_self_rating: "", dependants: "", interest_in_support: false, willingness_for_followup: false,
	declined_reason: "", stress_frequency: "", main_concerns: "", main_concerns_other: "", support_availability: "", coping_ability: "",
	coping_behaviour: "", coping_behaviour_other: "", preferred_support_type: "", marital_status: "", domestic_situation: "", conflict_exposure: "", exposure_details: "",
})
const selectedMainConcerns = ref([])

const profile = createResource({ url: "krcti_mhpss.api.counsellor.client_profile" })
const programmeContext = createResource({
	url: "krcti_mhpss.api.baseline_workflow.programme_baseline_context",
	onSuccess(data) { surveyId.value = data.survey_id; profile.data = { client: data.client, survey: null, cycle: data.cycle }; profile.loading = false },
	onError() { profile.loading = false },
})
const publicContext = createResource({
	url: "krcti_mhpss.api.baseline_workflow.public_baseline_context",
	onSuccess(data) { surveyId.value = data.survey_id; profile.data = { client: data.client, survey: null, cycle: data.cycle }; profile.loading = false },
	onError() { profile.loading = false },
})
const counsellorSaver = createResource({
	url: "krcti_mhpss.api.records.record_baseline",
	onSuccess() {
		router.replace({ name: "ClientProfile", params: { name: clientName.value } })
	},
})
const programmeSaver = createResource({
	url: "krcti_mhpss.api.baseline_workflow.programme_baseline_submit",
	onSuccess() { router.replace({ name: "ProgrammeClientDetail", params: { name: clientName.value } }) },
})
const publicSaver = createResource({
	url: "krcti_mhpss.api.baseline_workflow.public_baseline_submit",
	onSuccess() { profile.data = { ...profile.data, survey: { consent: form.consent, status: form.consent === "Declined" ? "Declined" : "Completed" } }; confirmOpen.value = false },
})
const activeSaver = computed(() => isPublic.value ? publicSaver : isProgrammeFill.value ? programmeSaver : counsellorSaver)

onMounted(() => {
	if (isPublic.value) { profile.loading = true; publicContext.submit({ token: token.value }) }
	else if (isProgrammeFill.value) { profile.loading = true; programmeContext.submit({ client: clientName.value, survey: route.query.survey }) }
	else profile.submit({ name: clientName.value })
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
function syncConcernDetails() {
	formError.value = ""
	if (!selectedMainConcerns.value.includes("Other")) form.main_concerns_other = ""
}
function changeConsent() {
	form.consent = form.consent === "Consented" ? "Declined" : ""
}
function submit() {
	formError.value = ""
	for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
	if (!form.consent) { formError.value = "Record the client’s consent before submitting."; return }
	if (form.consent === "Consented") {
		const required = ["wellbeing_self_rating", "stress_frequency", "support_availability", "coping_ability", "preferred_support_type", "coping_behaviour", "marital_status", "domestic_situation", "conflict_exposure"]
		const missing = required.filter((key) => form[key] === "" || form[key] === null || form[key] === undefined)
		for (const key of missing) fieldErrors[key] = "This answer is required."
		if (!selectedMainConcerns.value.length) fieldErrors.main_concerns = "Select at least one concern."
		if (missing.length || fieldErrors.main_concerns) {
			formError.value = "Complete the highlighted answers before submitting."
			step.value = sectionForField(missing[0] || "main_concerns")
			return
		}
		const rating = Number(form.wellbeing_self_rating)
		if (!Number.isInteger(rating) || rating < 1 || rating > 10) { fieldErrors.wellbeing_self_rating = "Choose a rating from 1 to 10."; step.value = 2; formError.value = "Correct the highlighted answer."; return }
		if (form.dependants !== "" && (!Number.isInteger(Number(form.dependants)) || Number(form.dependants) < 0)) { fieldErrors.dependants = "Enter a whole number of zero or more."; step.value = 8; formError.value = "Correct the highlighted answer."; return }
		const textFields = ["main_concerns", "main_concerns_other", "coping_behaviour_other", "domestic_situation", "exposure_details"]
		const tooLong = textFields.find((key) => String(form[key] || "").length > 2000)
		if (tooLong) { fieldErrors[tooLong] = "Keep this answer to 2000 characters or fewer."; step.value = sectionForField(tooLong); formError.value = "Correct the highlighted answer."; return }
	}
	if (form.consent === "Consented" && form.coping_behaviour === "Other" && !form.coping_behaviour_other.trim()) {
		step.value = 6
		fieldErrors.coping_behaviour_other = "Describe the other coping mechanism."
		formError.value = "Describe the other coping mechanism before submitting."
		return
	}
	if (form.consent === "Consented" && selectedMainConcerns.value.includes("Other") && !form.main_concerns_other.trim()) {
		step.value = 4
		fieldErrors.main_concerns_other = "Describe the other concern."
		formError.value = "Describe the other concern before submitting."
		return
	}
	confirmOpen.value = true
}
function sectionForField(field) {
	if (field === "wellbeing_self_rating") return 2
	if (field === "stress_frequency") return 3
	if (["main_concerns", "main_concerns_other"].includes(field)) return 4
	if (["support_availability", "preferred_support_type"].includes(field)) return 5
	if (["coping_ability", "coping_behaviour", "coping_behaviour_other"].includes(field)) return 6
	if (["interest_in_support", "willingness_for_followup"].includes(field)) return 7
	return 8
}
function confirmSubmit() {
	const data = { consent: form.consent }
	if (form.consent === "Declined") {
		data.declined_reason = form.declined_reason
	} else {
		for (const key of ["stress_frequency", "main_concerns_other", "support_availability", "coping_ability", "coping_behaviour", "coping_behaviour_other", "preferred_support_type", "marital_status", "domestic_situation", "conflict_exposure", "exposure_details"]) {
			data[key] = form[key]
		}
		data.main_concerns = selectedMainConcerns.value.join(", ")
		data.wellbeing_self_rating = form.wellbeing_self_rating === "" ? "" : Number(form.wellbeing_self_rating)
		data.dependants = form.dependants === "" ? 0 : Number(form.dependants)
		data.interest_in_support = form.interest_in_support ? 1 : 0
		data.willingness_for_followup = form.willingness_for_followup ? 1 : 0
	}
	if (isPublic.value) publicSaver.submit({ token: token.value, data })
	else if (isProgrammeFill.value) programmeSaver.submit({ survey: surveyId.value, data })
	else counsellorSaver.submit({ client: clientName.value, data })
}
</script>
