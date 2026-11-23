<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 text-[#25272B] sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- Breadcrumb -->
			<div class="mb-5 text-sm text-[#737780]">
				<router-link :to="isNew ? back : { name: 'Clients' }" class="hover:text-[#A10E24]">{{ isNew ? (isProgrammeManager ? 'Programme clients' : 'Clients') : 'Clients' }}</router-link>
				<span class="px-2">/</span><span class="font-semibold text-[#25272B]">{{ isNew ? 'Register client' : 'Edit client' }}</span>
			</div>

			<!-- Header -->
			<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
				<div>
					<p class="text-sm font-medium text-[#737780]">{{ isNew ? 'New registration' : 'Client record' }}</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">{{ isNew ? 'Register a client' : 'Edit client details' }}</h1>
					<p class="mt-1 max-w-2xl text-sm text-[#737780]">
						{{ isNew ? (isProgrammeManager ? 'Register a participant. Complete and verify their baseline before assigning a counsellor.' : 'Add a participant to your caseload. You can record their baseline survey afterwards.') : `Update the record for ${form.full_name || 'this client'}.` }}
					</p>
				</div>
				<router-link :to="back" class="btn btn-secondary self-start sm:self-auto"><ArrowLeft :size="16" /> {{ isNew ? 'Back to clients' : 'Back to client' }}</router-link>
			</div>

			<div v-if="loading" class="mt-6 rounded-xl border border-[#E4E6EA] bg-white px-5 py-12"><PageLoader /></div>

			<form v-else class="mt-6 grid items-start gap-5 lg:grid-cols-[300px_minmax(0,1fr)]" novalidate @submit.prevent="save">
				<!-- ============ Sidebar ============ -->
				<aside class="space-y-5 lg:sticky lg:top-[92px]" aria-label="Registration progress">
					<section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
						<div class="flex items-center gap-3 border-b border-[#ECEDEF] px-5 py-4">
							<span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-bold text-[#B30F2A]">{{ previewInitials }}</span>
							<div class="min-w-0">
								<p class="truncate text-sm font-semibold text-[#33353A]">{{ previewName || (isNew ? 'New client' : 'Client') }}</p>
								<p class="mt-0.5 truncate text-xs text-[#858891]">{{ form.scholar_code || 'Code generated on registration' }}</p>
							</div>
						</div>
						<div class="flex flex-wrap gap-2 border-b border-[#ECEDEF] px-5 py-3.5">
							<span class="rounded-full bg-[#FCE8EB] px-2.5 py-1 text-xs font-semibold text-[#A10E24]">{{ form.cohort ? `Cohort ${form.cohort}` : (cohortLoading ? 'Loading cohort…' : 'No cohort') }}</span>
							<span v-if="calculatedAge !== null" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">Age {{ calculatedAge }}</span>
							<span v-if="form.disability_status" class="rounded-full bg-[#E0EAFD] px-2.5 py-1 text-xs font-semibold text-[#1B4DB1]">Disability</span>
							<span v-if="form.refugee_status" class="rounded-full bg-[#FDECC8] px-2.5 py-1 text-xs font-semibold text-[#8A4B00]">Refugee</span>
						</div>

						<div class="px-5 py-4">
							<div class="flex items-baseline justify-between gap-3">
								<span class="text-xs font-semibold text-[#555860]">Required fields</span>
								<span class="text-xs tabular-nums text-[#858891]"><b class="text-sm font-semibold text-[#25272B]">{{ doneCount }}</b> / {{ requiredItems.length }}</span>
							</div>
							<div class="mt-2 h-2 overflow-hidden rounded-full bg-[#F4F5F7]">
								<div class="h-full rounded-full transition-[width] duration-300" :class="progress === 100 ? 'bg-[#146C3A]' : 'bg-[#C8102E]'" :style="{ width: `${progress}%` }"></div>
							</div>
						</div>

						<nav class="hidden border-t border-[#ECEDEF] p-2 lg:block" aria-label="Form sections">
							<button v-for="(s, i) in SECTIONS" :key="s.id" type="button" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition hover:bg-[#F7F7F8]" @click="goTo(s.id)">
								<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold" :class="sectionStats(s.id).complete ? 'bg-[#DCF3E4] text-[#146C3A]' : 'bg-[#F4F5F7] text-[#62656D]'">
									<Check v-if="sectionStats(s.id).complete" :size="14" :stroke-width="2.5" /><template v-else>{{ i + 1 }}</template>
								</span>
								<span class="min-w-0 flex-1">
									<span class="block text-sm font-medium text-[#33353A]">{{ s.title }}</span>
									<span class="block text-xs text-[#858891]">{{ sectionStats(s.id).total ? `${sectionStats(s.id).done} of ${sectionStats(s.id).total} required` : 'Optional' }}</span>
								</span>
							</button>
						</nav>
					</section>
				</aside>

				<!-- ============ Form sections ============ -->
				<div class="min-w-0 space-y-5">
					<!-- Identity -->
					<section id="sec-identity" class="card scroll-mt-24" :class="sectionOpen('identity') ? 'relative z-20' : ''">
						<header class="card-head">
							<span class="card-icon"><UserRound :size="18" /></span>
							<div><h2 class="text-base font-semibold text-[#25272B]">Identity</h2><p class="mt-0.5 text-xs text-[#858891]">Who the client is and how to reach them</p></div>
						</header>
						<div class="grid gap-x-4 gap-y-5 p-5 sm:grid-cols-6 sm:p-6">
							<template v-if="isNew">
								<div class="sm:col-span-3">
									<label class="lbl" for="f-first_name">First name <span class="req" aria-hidden="true">*</span></label>
									<input id="f-first_name" v-model="form.first_name" class="inp" type="text" autocomplete="given-name" />
								</div>
								<div class="sm:col-span-3">
									<label class="lbl" for="f-last_name">Last name <span class="req" aria-hidden="true">*</span></label>
									<input id="f-last_name" v-model="form.last_name" class="inp" type="text" autocomplete="family-name" />
								</div>
							</template>
							<div v-else class="sm:col-span-6">
								<label class="lbl" for="f-full_name">Full name <span class="req" aria-hidden="true">*</span></label>
								<input id="f-full_name" v-model="form.full_name" class="inp" type="text" autocomplete="off" />
							</div>

							<div class="sm:col-span-3">
								<label class="lbl" for="f-cohort">{{ isNew ? 'Active cohort' : 'Cohort' }}</label>
								<div class="relative">
									<input id="f-cohort" v-model="form.cohort" class="inp pr-10" type="text" readonly :placeholder="cohortLoading ? 'Loading active cohort…' : 'Cohort unavailable'" />
									<Lock :size="15" class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-[#A0A2A8]" />
								</div>
								<p v-if="isNew" class="hint">Assigned automatically from Programme Settings. Each cohort supports up to 99 clients.</p>
							</div>
							<div class="sm:col-span-3">
								<label class="lbl" for="f-scholar_code">Scholar / participant code</label>
								<div class="relative">
									<input id="f-scholar_code" v-model="form.scholar_code" class="inp pr-10" type="text" readonly placeholder="Generated on registration" autocomplete="off" />
									<Lock :size="15" class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-[#A0A2A8]" />
								</div>
								<p class="hint">Generated automatically as WoCS_C&lt;cohort&gt;&lt;two-digit number&gt;.</p>
							</div>

							<div class="sm:col-span-3">
								<label class="lbl" for="f-phone_number">Phone number <span class="req" aria-hidden="true">*</span></label>
								<input id="f-phone_number" v-model="form.phone_number" class="inp" type="tel" inputmode="tel" placeholder="0712 345 678" autocomplete="off" />
							</div>
							<div class="sm:col-span-3">
								<label class="lbl" for="f-email">Email address <span class="opt">(optional)</span></label>
								<input id="f-email" v-model="form.email" class="inp" type="email" autocomplete="email" placeholder="name@example.com" />
								<p class="hint">Needed only if you choose to send the baseline form to the client.</p>
							</div>

							<div class="sm:col-span-3">
								<label class="lbl" for="f-date_of_birth">Date of birth <span v-if="isNew" class="req" aria-hidden="true">*</span></label>
								<input id="f-date_of_birth" v-model="form.date_of_birth" class="inp" type="date" :required="isNew" :max="today" />
								<p class="hint">Age is calculated automatically{{ calculatedAge !== null ? ` · current age: ${calculatedAge}` : legacyAge ? ` · recorded age: ${legacyAge}` : '' }}.</p>
								<p v-if="ageError" class="mt-1 text-xs font-medium text-[#A10E24]" role="alert">{{ ageError }}</p>
							</div>

							<div v-for="key in SECTION_SELECTS.identity" :key="key" :class="SELECTS[key].span" class="relative" data-client-dropdown>
								<label :id="`f-${key}-label`" class="lbl">{{ SELECTS[key].label }} <span v-if="SELECTS[key].required" class="req" aria-hidden="true">*</span><span v-else class="opt">(optional)</span></label>
								<button :id="`f-${key}`" type="button" class="select-control" :class="selectedLabel(key) ? '' : 'select-placeholder'" :aria-labelledby="`f-${key}-label f-${key}-value`" :aria-expanded="openDropdown === key" aria-haspopup="listbox" @click="toggleDropdown(key)" @keydown.esc="openDropdown = ''">
									<span :id="`f-${key}-value`" class="truncate">{{ selectedLabel(key) || SELECTS[key].placeholder }}</span>
									<ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="openDropdown === key ? 'rotate-180' : ''" />
								</button>
								<div v-if="openDropdown === key" class="select-menu">
									<input v-if="SELECTS[key].search" v-model="countySearch[key]" class="select-search" type="search" :placeholder="`Search ${SELECTS[key].searchLabel || 'options'}…`" autocomplete="off" @keydown.esc="openDropdown = ''" />
									<div role="listbox" :aria-labelledby="`f-${key}-label`">
										<button v-for="o in filteredOptions(key)" :key="o.value" type="button" role="option" :aria-selected="isSelected(key, o)" class="select-option" :class="isSelected(key, o) ? 'select-option-active' : ''" @click="chooseOption(key, o.value)">{{ o.label }}<Check v-if="isSelected(key, o)" :size="16" /></button>
										<p v-if="!filteredOptions(key).length" class="select-empty">{{ SELECTS[key].empty || 'No options available.' }}</p>
									</div>
								</div>
							</div>
						</div>
					</section>

					<!-- Circumstances -->
					<section id="sec-circumstances" class="card scroll-mt-24" :class="sectionOpen('circumstances') ? 'relative z-20' : ''">
						<header class="card-head">
							<span class="card-icon"><Heart :size="18" /></span>
							<div><h2 class="text-base font-semibold text-[#25272B]">Circumstances</h2><p class="mt-0.5 text-xs text-[#858891]">Helps tailor the support offered</p></div>
						</header>
						<div class="grid gap-4 p-5 sm:grid-cols-2 sm:p-6">
							<label class="choice" :class="form.disability_status ? 'is-on' : ''">
								<input v-model="form.disability_status" type="checkbox" class="choice-input" />
								<span class="check-box"><Check v-if="form.disability_status" :size="14" :stroke-width="3" class="text-white" /></span>
								<span class="min-w-0">
									<span class="block text-sm font-semibold text-[#25272B]">Person with a disability</span>
									<span class="block text-xs text-[#737780]">Tick if the client lives with a disability</span>
								</span>
							</label>
							<label class="choice" :class="form.refugee_status ? 'is-on' : ''">
								<input v-model="form.refugee_status" type="checkbox" class="choice-input" />
								<span class="check-box"><Check v-if="form.refugee_status" :size="14" :stroke-width="3" class="text-white" /></span>
								<span class="min-w-0">
									<span class="block text-sm font-semibold text-[#25272B]">Refugee</span>
									<span class="block text-xs text-[#737780]">Tick if the client has refugee status</span>
								</span>
							</label>

							<div v-for="key in circumstanceSelects" :key="key" class="relative sm:col-span-2" data-client-dropdown>
								<label :id="`f-${key}-label`" class="lbl">{{ SELECTS[key].label }} <span class="req" aria-hidden="true">*</span></label>
								<button :id="`f-${key}`" type="button" class="select-control" :class="selectedLabel(key) ? '' : 'select-placeholder'" :aria-labelledby="`f-${key}-label f-${key}-value`" :aria-expanded="openDropdown === key" aria-haspopup="listbox" @click="toggleDropdown(key)" @keydown.esc="openDropdown = ''">
									<span :id="`f-${key}-value`" class="truncate">{{ selectedLabel(key) || SELECTS[key].placeholder }}</span>
									<ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="openDropdown === key ? 'rotate-180' : ''" />
								</button>
								<div v-if="openDropdown === key" class="select-menu" role="listbox" :aria-labelledby="`f-${key}-label`">
									<button v-for="o in filteredOptions(key)" :key="o.value" type="button" role="option" :aria-selected="isSelected(key, o)" class="select-option" :class="isSelected(key, o) ? 'select-option-active' : ''" @click="chooseOption(key, o.value)">{{ o.label }}<Check v-if="isSelected(key, o)" :size="16" /></button>
								</div>
							</div>
						</div>
					</section>

					<!-- Education -->
					<section id="sec-education" class="card scroll-mt-24" :class="sectionOpen('education') ? 'relative z-20' : ''">
						<header class="card-head">
							<span class="card-icon"><GraduationCap :size="18" /></span>
							<div><h2 class="text-base font-semibold text-[#25272B]">Education</h2><p class="mt-0.5 text-xs text-[#858891]">Institution and studies</p></div>
						</header>
						<div class="grid gap-x-4 gap-y-5 p-5 sm:grid-cols-6 sm:p-6">
							<div v-for="key in SECTION_SELECTS.education" :key="key" :class="SELECTS[key].span" class="relative" data-client-dropdown>
								<label :id="`f-${key}-label`" class="lbl">{{ SELECTS[key].label }} <span v-if="SELECTS[key].required" class="req" aria-hidden="true">*</span><span v-else class="opt">(optional)</span></label>
								<button :id="`f-${key}`" type="button" class="select-control" :class="selectedLabel(key) ? '' : 'select-placeholder'" :aria-labelledby="`f-${key}-label f-${key}-value`" :aria-expanded="openDropdown === key" aria-haspopup="listbox" @click="toggleDropdown(key)" @keydown.esc="openDropdown = ''">
									<span :id="`f-${key}-value`" class="truncate">{{ selectedLabel(key) || SELECTS[key].placeholder }}</span>
									<ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="openDropdown === key ? 'rotate-180' : ''" />
								</button>
								<div v-if="openDropdown === key" class="select-menu">
									<input v-if="SELECTS[key].search" v-model="countySearch[key]" class="select-search" type="search" :placeholder="`Search ${SELECTS[key].searchLabel || 'options'}…`" autocomplete="off" @keydown.esc="openDropdown = ''" />
									<div role="listbox" :aria-labelledby="`f-${key}-label`">
										<button v-for="o in filteredOptions(key)" :key="o.value" type="button" role="option" :aria-selected="isSelected(key, o)" class="select-option" :class="isSelected(key, o) ? 'select-option-active' : ''" @click="chooseOption(key, o.value)">{{ o.label }}<Check v-if="isSelected(key, o)" :size="16" /></button>
										<p v-if="!filteredOptions(key).length" class="select-empty">{{ SELECTS[key].empty || 'No options available.' }}</p>
									</div>
								</div>
							</div>
						</div>
					</section>

					<!-- Programme -->
					<section id="sec-programme" class="card scroll-mt-24" :class="sectionOpen('programme') ? 'relative z-20' : ''">
						<header class="card-head">
							<span class="card-icon"><MapPin :size="18" /></span>
							<div><h2 class="text-base font-semibold text-[#25272B]">Programme</h2><p class="mt-0.5 text-xs text-[#858891]">Location and how they joined</p></div>
						</header>
						<div class="grid gap-x-4 gap-y-5 p-5 sm:grid-cols-6 sm:p-6">
							<div v-for="key in SECTION_SELECTS.programme" :key="key" :class="SELECTS[key].span" class="relative" data-client-dropdown>
								<label :id="`f-${key}-label`" class="lbl">{{ SELECTS[key].label }} <span v-if="SELECTS[key].required" class="req" aria-hidden="true">*</span><span v-else class="opt">(optional)</span></label>
								<button :id="`f-${key}`" type="button" class="select-control" :class="selectedLabel(key) ? '' : 'select-placeholder'" :aria-labelledby="`f-${key}-label f-${key}-value`" :aria-expanded="openDropdown === key" aria-haspopup="listbox" @click="toggleDropdown(key)" @keydown.esc="openDropdown = ''">
									<span :id="`f-${key}-value`" class="truncate">{{ selectedLabel(key) || SELECTS[key].placeholder }}</span>
									<ChevronDown :size="17" class="shrink-0 text-[#737780] transition-transform" :class="openDropdown === key ? 'rotate-180' : ''" />
								</button>
								<div v-if="openDropdown === key" class="select-menu">
									<input v-if="SELECTS[key].search" v-model="countySearch[key]" class="select-search" type="search" :placeholder="`Search ${SELECTS[key].searchLabel || 'options'}…`" autocomplete="off" @keydown.esc="openDropdown = ''" />
									<div role="listbox" :aria-labelledby="`f-${key}-label`">
										<button v-for="o in filteredOptions(key)" :key="o.value" type="button" role="option" :aria-selected="isSelected(key, o)" class="select-option" :class="isSelected(key, o) ? 'select-option-active' : ''" @click="chooseOption(key, o.value)">{{ o.label }}<Check v-if="isSelected(key, o)" :size="16" /></button>
										<p v-if="!filteredOptions(key).length" class="select-empty">{{ SELECTS[key].empty || 'No options available.' }}</p>
									</div>
								</div>
							</div>
							<div v-if="form.referral_source === 'Other'" class="sm:col-span-3">
								<label class="lbl" for="f-referral_source_other">Describe the referral source</label>
								<input id="f-referral_source_other" v-model="form.referral_source_other" class="inp" type="text" autocomplete="off" />
							</div>
						</div>
					</section>

					<div v-if="formError || saver.error" class="flex items-start gap-3 rounded-xl border border-[#F0C8CE] bg-[#FFF6F7] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
						<AlertCircle :size="19" class="mt-px shrink-0" />
						<span v-if="formError">{{ formError }}</span>
						<ErrorMessage v-else :message="saver.error" />
					</div>

					<!-- Action bar -->
					<div class="sticky bottom-3 z-10 flex flex-col-reverse items-stretch justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white/95 p-3 shadow-[0_8px_24px_rgba(31,35,45,0.08)] backdrop-blur sm:flex-row sm:items-center">
						<p class="hidden items-center gap-2 px-2 text-xs text-[#737780] sm:flex">
							<span class="h-2 w-2 rounded-full" :class="progress === 100 ? 'bg-[#146C3A]' : 'bg-[#D99A2B]'"></span>
							{{ progress === 100 ? 'All required fields are complete' : `${requiredItems.length - doneCount} required field${requiredItems.length - doneCount === 1 ? '' : 's'} left` }}
						</p>
						<div class="flex flex-col-reverse gap-2 sm:flex-row">
							<router-link :to="back" class="btn btn-secondary">Cancel</router-link>
							<button type="submit" :disabled="saver.loading" class="btn btn-primary">
								<Loader2 v-if="saver.loading" :size="17" class="animate-spin" />
								<Check v-else :size="17" />
								{{ isNew ? 'Register client' : 'Save changes' }}
							</button>
						</div>
					</div>
				</div>
			</form>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { AlertCircle, ArrowLeft, Check, ChevronDown, GraduationCap, Heart, Loader2, Lock, MapPin, UserRound } from "lucide-vue-next"
import { DISABILITY_TYPES, GENDERS, KENYA_COUNTIES, REFERRALS, STREAMS } from "../data/options"
import { me } from "../data/me"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !clientName.value)
const role = computed(() => me.data?.role)
const isProgrammeManager = computed(() => ["krcti_pm", "woc_pm"].includes(role.value))
const back = computed(() => (isNew.value ? (isProgrammeManager.value ? { name: "ProgrammeClients" } : { name: "Clients" }) : { name: "ClientProfile", params: { name: clientName.value } }))

const TEXT = ["full_name", "phone_number", "email", "gender", "disability_type", "institution", "institution_county",
	"course_programme", "study_program", "study_programme", "county_location", "programme_stream", "referral_source", "referral_source_other"]
const NUMBERS = ["year_of_study"]
const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`
const STUDY_PROGRAMS = ["Teaching", "Engineering"]
const YEAR_OF_STUDY = Array.from({ length: 10 }, (_, index) => ({ label: String(index + 1), value: index + 1 }))
const CHECKS = ["disability_status", "refugee_status"]

const form = reactive({
	...Object.fromEntries([...TEXT, ...NUMBERS].map((k) => [k, ""])),
	date_of_birth: "",
	age: "",
	first_name: "",
	last_name: "",
	cohort: "",
	scholar_code: "",
	disability_status: false,
	refugee_status: false,
})
const loading = ref(false)
const openDropdown = ref("")
const formError = ref("")
const cohortLoading = ref(false)
const countySearch = reactive({ institution_county: "", county_location: "" })
const masterOptions = reactive({ institutions: [], courses: [], programmes: [] })
const calculatedAge = computed(() => {
	if (!form.date_of_birth) return null
	const [year, month, day] = form.date_of_birth.split("-").map(Number)
	const now = new Date()
	return now.getFullYear() - year - ((now.getMonth() + 1 < month || (now.getMonth() + 1 === month && now.getDate() < day)) ? 1 : 0)
})
const legacyAge = computed(() => form.date_of_birth ? null : form.age || null)
const ageError = computed(() => form.date_of_birth && (calculatedAge.value < 10 || calculatedAge.value > 100) ? "The client's age must be between 10 and 100." : "")

// Option lists may be plain strings or { label, value } objects
const opts = (list) => (list || []).map((o) => (o !== null && typeof o === "object" ? { label: o.label ?? o.value, value: o.value ?? o.label } : { label: o, value: o }))
const strings = (list) => (list || []).map((v) => ({ label: v, value: v }))

// ---- Dropdown definitions ----
const SELECTS = {
	gender: { label: "Sex", required: true, placeholder: "Select sex", span: "sm:col-span-3", options: () => opts(GENDERS) },
	disability_type: { label: "Type of disability", required: true, placeholder: "Select type of disability", span: "sm:col-span-2", options: () => opts(DISABILITY_TYPES) },
	institution: { label: "College or learning institution", required: true, placeholder: "Select institution", span: "sm:col-span-6", options: () => strings(masterOptions.institutions), empty: "No active institutions are available." },
	course_programme: { label: "Course or programme", required: true, placeholder: "Select course or programme", span: "sm:col-span-4", options: () => strings(masterOptions.courses), empty: "No active courses are available." },
	year_of_study: { label: "Year of study", required: true, placeholder: "Select year", span: "sm:col-span-2", options: () => YEAR_OF_STUDY },
	study_program: { label: "Study programme", required: true, placeholder: "Select study programme", span: "sm:col-span-3", options: () => strings(STUDY_PROGRAMS) },
	study_programme: { label: "Client programme", required: false, placeholder: "Select client programme", span: "sm:col-span-3", options: () => strings(masterOptions.programmes), empty: "No active programmes are available." },
	institution_county: { label: "County of school", required: true, placeholder: "Select county", span: "sm:col-span-3", options: () => opts(KENYA_COUNTIES), search: true, searchLabel: "counties", empty: "No counties match your search." },
	county_location: { label: "County location", required: true, placeholder: "Select county", span: "sm:col-span-3", options: () => opts(KENYA_COUNTIES), search: true, searchLabel: "counties", empty: "No counties match your search." },
	programme_stream: { label: "WoC programme stream", required: false, placeholder: "Select stream", span: "sm:col-span-3", options: () => opts(STREAMS) },
	referral_source: { label: "Referral source", required: false, placeholder: "Select referral source", span: "sm:col-span-3", options: () => opts(REFERRALS) },
}
const SECTION_SELECTS = {
	identity: ["gender"],
	education: ["institution", "course_programme", "year_of_study", "study_program", "study_programme", "institution_county"],
	programme: ["county_location", "programme_stream", "referral_source"],
}
const circumstanceSelects = computed(() => (form.disability_status ? ["disability_type"] : []))
const sectionKeys = (id) => (id === "circumstances" ? ["disability_type"] : SECTION_SELECTS[id] || [])
const sectionOpen = (id) => sectionKeys(id).includes(openDropdown.value)

const isSelected = (key, o) => form[key] !== "" && form[key] !== null && String(o.value) === String(form[key])
const selectedLabel = (key) => SELECTS[key].options().find((o) => isSelected(key, o))?.label || ""
const filteredOptions = (key) => {
	const list = SELECTS[key].options()
	if (!SELECTS[key].search) return list
	const term = (countySearch[key] || "").trim().toLocaleLowerCase()
	return list.filter((o) => o.value && o.label.toLocaleLowerCase().includes(term))
}
const toggleDropdown = (field) => {
	openDropdown.value = openDropdown.value === field ? "" : field
	if (field in countySearch) countySearch[field] = ""
}
const chooseOption = (field, value) => {
	form[field] = value
	if (field in countySearch) countySearch[field] = ""
	openDropdown.value = ""
}
function closeDropdownOutside(event) {
	if (!event.target.closest("[data-client-dropdown]")) {
		openDropdown.value = ""
		countySearch.institution_county = ""
		countySearch.county_location = ""
	}
}

// ---- Progress ----
const SECTIONS = [
	{ id: "identity", title: "Identity" },
	{ id: "circumstances", title: "Circumstances" },
	{ id: "education", title: "Education" },
	{ id: "programme", title: "Programme" },
]
const requiredItems = computed(() => {
	const items = []
	if (isNew.value) {
		items.push({ section: "identity", done: !!form.first_name.trim() }, { section: "identity", done: !!form.last_name.trim() })
	} else {
		items.push({ section: "identity", done: !!form.full_name.trim() })
	}
	items.push({ section: "identity", done: !!String(form.phone_number).trim() })
	if (isNew.value) items.push({ section: "identity", done: !!form.date_of_birth })
	items.push({ section: "identity", done: !!form.gender })
	if (form.disability_status) items.push({ section: "circumstances", done: !!form.disability_type })
	for (const key of ["institution", "course_programme", "year_of_study", "study_program", "institution_county"]) items.push({ section: "education", done: form[key] !== "" && form[key] !== null })
	items.push({ section: "programme", done: !!form.county_location })
	return items
})
const doneCount = computed(() => requiredItems.value.filter((i) => i.done).length)
const progress = computed(() => (requiredItems.value.length ? Math.round((doneCount.value / requiredItems.value.length) * 100) : 0))
function sectionStats(id) {
	const items = requiredItems.value.filter((i) => i.section === id)
	const done = items.filter((i) => i.done).length
	return { done, total: items.length, complete: items.length > 0 && done === items.length }
}
function goTo(id) {
	document.getElementById(`sec-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" })
}

const previewName = computed(() => (isNew.value ? `${form.first_name} ${form.last_name}`.trim() : form.full_name.trim()))
const previewInitials = computed(() => previewName.value.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase() || "?")

// ---- Data ----
const profile = createResource({
	url: "krcti_mhpss.api.counsellor.client_profile",
	onSuccess(data) {
		const c = data.client
		form.cohort = c.cohort ?? ""
		form.scholar_code = c.scholar_code ?? ""
		for (const k of [...TEXT, ...NUMBERS, "date_of_birth", "age"]) form[k] = c[k] ?? ""
		for (const k of CHECKS) form[k] = !!c[k]
		loading.value = false
	},
})

const registrationSettings = createResource({
	url: "krcti_mhpss.api.records.client_registration_settings",
	onSuccess(data) {
		form.cohort = data.active_cohort || ""
		cohortLoading.value = false
	},
	onError() {
		cohortLoading.value = false
	},
})

const clientMasterOptions = createResource({
	url: "krcti_mhpss.api.records.client_master_options",
	onSuccess(data) {
		masterOptions.institutions = data.institutions || []
		masterOptions.courses = data.courses || []
		masterOptions.programmes = data.programmes || []
	},
})

onMounted(() => {
	clientMasterOptions.submit()
	if (isNew.value) {
		cohortLoading.value = true
		registrationSettings.submit()
	}
	if (!isNew.value) {
		loading.value = true
		profile.submit({ name: clientName.value })
	}
})
onMounted(() => document.addEventListener("click", closeDropdownOutside))
onUnmounted(() => document.removeEventListener("click", closeDropdownOutside))

const saver = createResource({
	url: isProgrammeManager.value ? "krcti_mhpss.api.records.register_programme_client" : "krcti_mhpss.api.records.save_client",
	onSuccess(result) {
		router.replace(isProgrammeManager.value ? { name: "ProgrammeClients" } : { name: "ClientProfile", params: { name: result.name } })
	},
})
const updater = saver // the template may still mention it

function values() {
	const data = {}
	for (const k of TEXT) data[k] = form[k]
	data.date_of_birth = form.date_of_birth
	if (isNew.value) data.full_name = `${form.first_name.trim()} ${form.last_name.trim()}`.trim()
	for (const k of NUMBERS) data[k] = form[k] === "" ? "" : Number(form[k])
	for (const k of CHECKS) data[k] = form[k] ? 1 : 0
	return data
}

function save() {
	formError.value = ""
	if (isNew.value && (!form.first_name.trim() || !form.last_name.trim())) {
		formError.value = "Enter both the client’s first name and last name."
		return
	}
	if (!isNew.value && !form.full_name.trim()) {
		formError.value = "Enter the client’s full name."
		return
	}
	if (isNew.value && !/^[1-9]$/.test(form.cohort)) {
		formError.value = "The active cohort could not be loaded. Refresh the form before registering this client."
		return
	}
	if (isNew.value && !form.date_of_birth) {
		formError.value = "Date of birth is required."
		return
	}
	if (ageError.value) {
		formError.value = ageError.value
		return
	}
	if (!form.gender || !form.institution || !form.course_programme || !form.study_program || !form.year_of_study ||
		Number(form.year_of_study) < 1 || Number(form.year_of_study) > 10 || !form.institution_county || !form.county_location) {
		formError.value = "Complete the required identity, education, and county fields before saving."
		return
	}
	if (form.disability_status && !form.disability_type) {
		formError.value = "Choose the type of disability."
		return
	}
	if (form.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
		formError.value = "Enter a valid email address or leave it blank."
		return
	}
	const data = values()
	if (isProgrammeManager.value) saver.submit({ data })
	else saver.submit({ name: clientName.value || undefined, data })
}
</script>

<style scoped>
/* ---- Cards ---- */
.card { border: 1px solid #e4e6ea; border-radius: 12px; background: #fff; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.03); }
.card-head { display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #ecedef; padding: 16px 20px; }
.card-icon { display: flex; height: 36px; width: 36px; flex-shrink: 0; align-items: center; justify-content: center; border-radius: 999px; background: #fce8eb; color: #a10e24; }

/* ---- Buttons ---- */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid transparent; border-radius: 8px; padding: 10px 16px; font-size: 14px; font-weight: 600; line-height: 20px; white-space: nowrap; transition: background 0.15s, border-color 0.15s, color 0.15s, box-shadow 0.15s; }
.btn:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.2); }
.btn:disabled { cursor: wait; opacity: 0.65; }
.btn-primary { background: #c8102e; color: #fff; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.12); }
.btn-primary:hover:not(:disabled) { background: #a10e24; }
.btn-secondary { border-color: #d9dbe0; background: #fff; color: #33353a; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.04); }
.btn-secondary:hover { border-color: #c8102e; color: #a10e24; }

/* ---- Fields ---- */
.lbl { display: block; margin-bottom: 6px; font-size: 12px; font-weight: 600; line-height: 18px; color: #555860; }
.req { color: #a10e24; }
.opt { font-weight: 400; color: #858891; }
.hint { margin-top: 6px; font-size: 12px; line-height: 17px; color: #858891; }

.inp { display: block; width: 100%; height: 44px; border: 1px solid #d9dbe0; border-radius: 10px; background: #fff; padding: 0 12px; font: inherit; font-size: 14px; line-height: 20px; color: #33353a; transition: border-color 0.15s, box-shadow 0.15s; }
.inp::placeholder { color: #a0a2a8; }
.inp:hover:not(:disabled):not(:read-only) { border-color: #bfc2c8; }
.inp:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }
.inp:disabled, .inp:read-only { cursor: default; background: #f7f7f8; color: #62656d; }
.inp:read-only:focus { border-color: #d9dbe0; box-shadow: none; }

.select-control { display: flex; width: 100%; height: 44px; align-items: center; justify-content: space-between; gap: 10px; border: 1px solid #d9dbe0; border-radius: 10px; background: #fff; padding: 0 12px; font: inherit; font-size: 14px; line-height: 20px; text-align: left; color: #33353a; transition: border-color 0.15s, box-shadow 0.15s; }
.select-control:hover { border-color: #bfc2c8; }
.select-control:focus-visible { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }
.select-placeholder { color: #a0a2a8; }
.select-menu { position: absolute; z-index: 30; top: calc(100% + 8px); left: 0; width: 100%; max-height: 260px; overflow-y: auto; border: 1px solid #e4e6ea; border-radius: 12px; background: #fff; padding: 6px; box-shadow: 0 12px 30px rgba(31, 35, 45, 0.14); }
.select-search { display: block; width: 100%; height: 40px; margin-bottom: 5px; border: 1px solid #e4e6ea; border-radius: 8px; background: #f7f7f8; padding: 0 10px; font: inherit; font-size: 13px; color: #33353a; }
.select-search:focus { outline: none; border-color: #c8102e; background: #fff; box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.12); }
.select-empty { padding: 12px 10px; font-size: 13px; color: #737780; }
.select-option { display: flex; min-height: 40px; width: 100%; align-items: center; justify-content: space-between; gap: 10px; border-radius: 8px; padding: 8px 10px; text-align: left; font-size: 14px; color: #44474e; transition: background 0.15s, color 0.15s; }
.select-option:hover { background: #f7f7f8; }
.select-option-active, .select-option-active:hover { background: #fce8eb; color: #a10e24; font-weight: 600; }

/* ---- Checkbox cards ---- */
.choice { position: relative; display: flex; min-height: 72px; cursor: pointer; align-items: center; gap: 12px; border: 1px solid #e4e6ea; border-radius: 12px; background: #fff; padding: 13px 15px; transition: border-color 0.15s, background 0.15s, box-shadow 0.15s; }
.choice:hover { border-color: #bfc2c8; background: #fcfcfd; }
.choice.is-on { border-color: #c8102e; background: #fff8f9; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.08); }
.choice:focus-within { box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.15); }
.choice-input { position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); clip-path: inset(50%); white-space: nowrap; opacity: 0; }
.check-box { display: grid; height: 22px; width: 22px; flex-shrink: 0; place-items: center; border: 1.5px solid #c5c8cf; border-radius: 7px; background: #fff; transition: background 0.15s, border-color 0.15s; }
.choice.is-on .check-box { border-color: #c8102e; background: #c8102e; }
</style>
