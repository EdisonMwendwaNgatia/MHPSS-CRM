<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[960px]">
      <router-link
        :to="back"
        class="inline-flex h-11 items-center gap-2 rounded-[10px] pr-3 text-sm font-medium text-[#5B616B] transition hover:text-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
      >
        <ArrowLeft :size="18" /> {{ isNew ? "Back to clients" : "Back to client" }}
      </router-link>

      <div class="mt-1">
        <h1 class="text-2xl font-semibold leading-8">{{ isNew ? "Register a client" : "Edit client details" }}</h1>
        <p class="mt-0.5 text-[13px] text-[#5B616B]">
          {{ isNew ? "Add a participant to your caseload. You can record their baseline survey afterwards." : `Update the record for ${form.full_name || "this client"}.` }}
        </p>
      </div>

      <PageLoader v-if="loading" />

      <form v-else class="mt-6 space-y-5" novalidate @submit.prevent="save">
        <!-- Identity -->
        <section class="overflow-visible rounded-xl border border-[#E4E6EA] bg-white">
          <div class="grid gap-x-8 gap-y-5 px-5 py-6 sm:px-6 lg:grid-cols-[210px_minmax(0,1fr)]">
            <div class="flex items-center gap-3 lg:items-start">
              <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><UserRound :size="19" /></span>
              <div>
                <h2 class="text-lg font-semibold leading-6">Identity</h2>
                <p class="text-[13px] leading-[18px] text-[#5B616B]">Who the client is and how to reach them</p>
              </div>
            </div>

            <div class="grid gap-x-4 gap-y-5 sm:grid-cols-6">
              <div class="sm:col-span-6">
                <label class="lbl" for="f-full_name">Full name <span class="req" aria-hidden="true">*</span></label>
                <input id="f-full_name" v-model="form.full_name" class="inp" type="text" autocomplete="off" />
              </div>

              <div class="sm:col-span-3">
                <label class="lbl" for="f-scholar_code">Scholar / participant code</label>
                <div class="relative">
                  <input
                    id="f-scholar_code"
                    v-model="form.scholar_code"
                    class="inp pr-11"
                    type="text"
                    readonly
                    :placeholder="isNew ? 'Generated automatically on registration' : ''"
                    autocomplete="off"
                  />
                  <Lock :size="16" class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-[#5B616B]" />
                </div>
                <p class="hint">Generated automatically when the client is registered.</p>
              </div>

              <div class="sm:col-span-3">
                <label class="lbl" for="f-phone_number">Phone number <span class="req" aria-hidden="true">*</span></label>
                <input id="f-phone_number" v-model="form.phone_number" class="inp" type="tel" inputmode="tel" placeholder="0712 345 678" autocomplete="off" />
              </div>

              <div class="sm:col-span-2">
                <label class="lbl" for="f-age">Age</label>
                <input id="f-age" v-model="form.age" class="inp" type="number" inputmode="numeric" min="0" />
              </div>

              <div class="sm:col-span-2">
                <label id="f-gender-label" class="lbl">Gender</label>
                <div class="relative" data-client-dropdown>
                  <button id="f-gender" type="button" class="select-control" :class="form.gender ? '' : 'select-placeholder'" :aria-labelledby="'f-gender-label f-gender-value'" :aria-expanded="openDropdown === 'gender'" aria-haspopup="listbox" @click="toggleDropdown('gender')" @keydown.esc="openDropdown = ''">
                    <span id="f-gender-value">{{ optionLabel(GENDERS, form.gender) }}</span><ChevronDown :size="17" class="text-[#737780] transition-transform" :class="openDropdown === 'gender' ? 'rotate-180' : ''" />
                  </button>
                  <div v-if="openDropdown === 'gender'" class="select-menu" role="listbox" aria-labelledby="f-gender-label">
                    <button v-for="o in opts(GENDERS)" :key="o.value" type="button" role="option" :aria-selected="form.gender === o.value" class="select-option" :class="form.gender === o.value ? 'select-option-active' : ''" @click="chooseOption('gender', o.value)">{{ o.label }}<Check v-if="form.gender === o.value" :size="16" /></button>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>

        <!-- Circumstances -->
        <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
          <div class="grid gap-x-8 gap-y-5 px-5 py-6 sm:px-6 lg:grid-cols-[210px_minmax(0,1fr)]">
            <div class="flex items-center gap-3 lg:items-start">
              <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><Heart :size="19" /></span>
              <div>
                <h2 class="text-lg font-semibold leading-6">Circumstances</h2>
                <p class="text-[13px] leading-[18px] text-[#5B616B]">Helps tailor the support offered</p>
              </div>
            </div>

            <div class="grid gap-x-4 gap-y-4 sm:grid-cols-2">
              <label class="choice" :class="form.disability_status ? 'is-on' : ''">
                <input v-model="form.disability_status" type="checkbox" class="choice-input" />
                <span class="check-box"><Check v-if="form.disability_status" :size="14" :stroke-width="3" class="text-white" /></span>
                <span class="min-w-0">
                  <span class="block text-sm font-semibold">Person with a disability</span>
                  <span class="block text-[13px] text-[#5B616B]">Tick if the client lives with a disability</span>
                </span>
              </label>

              <label class="choice" :class="form.refugee_status ? 'is-on' : ''">
                <input v-model="form.refugee_status" type="checkbox" class="choice-input" />
                <span class="check-box"><Check v-if="form.refugee_status" :size="14" :stroke-width="3" class="text-white" /></span>
                <span class="min-w-0">
                  <span class="block text-sm font-semibold">Refugee</span>
                  <span class="block text-[13px] text-[#5B616B]">Tick if the client has refugee status</span>
                </span>
              </label>

              <div v-if="form.disability_status" class="sm:col-span-2">
                <label class="lbl" for="f-disability_type">Type of disability</label>
                <input id="f-disability_type" v-model="form.disability_type" class="inp" type="text" autocomplete="off" />
              </div>
            </div>
          </div>
        </section>

        <!-- Education -->
        <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
          <div class="grid gap-x-8 gap-y-5 px-5 py-6 sm:px-6 lg:grid-cols-[210px_minmax(0,1fr)]">
            <div class="flex items-center gap-3 lg:items-start">
              <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><GraduationCap :size="19" /></span>
              <div>
                <h2 class="text-lg font-semibold leading-6">Education</h2>
                <p class="text-[13px] leading-[18px] text-[#5B616B]">Institution and studies</p>
              </div>
            </div>

            <div class="grid gap-x-4 gap-y-5 sm:grid-cols-6">
              <div class="sm:col-span-6">
                <label class="lbl" for="f-institution">College or learning institution</label>
                <input id="f-institution" v-model="form.institution" class="inp" type="text" autocomplete="off" />
              </div>
              <div class="sm:col-span-4">
                <label class="lbl" for="f-course_programme">Course or programme</label>
                <input id="f-course_programme" v-model="form.course_programme" class="inp" type="text" autocomplete="off" />
              </div>
              <div class="sm:col-span-2">
                <label class="lbl" for="f-year_of_study">Year of study</label>
                <input id="f-year_of_study" v-model="form.year_of_study" class="inp" type="number" inputmode="numeric" min="0" />
              </div>
            </div>
          </div>
        </section>

        <!-- Programme -->
        <section class="overflow-visible rounded-xl border border-[#E4E6EA] bg-white">
          <div class="grid gap-x-8 gap-y-5 px-5 py-6 sm:px-6 lg:grid-cols-[210px_minmax(0,1fr)]">
            <div class="flex items-center gap-3 lg:items-start">
              <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#FCE8EB] text-[#A10E24]"><MapPin :size="19" /></span>
              <div>
                <h2 class="text-lg font-semibold leading-6">Programme</h2>
                <p class="text-[13px] leading-[18px] text-[#5B616B]">Location and how they joined</p>
              </div>
            </div>

            <div class="grid gap-x-4 gap-y-5 sm:grid-cols-2">
              <div>
                <label class="lbl" for="f-county_location">County location</label>
                <input id="f-county_location" v-model="form.county_location" class="inp" type="text" autocomplete="off" />
              </div>
              <div>
                <label id="f-programme_stream-label" class="lbl">WoC programme stream</label>
                <div class="relative" data-client-dropdown>
                  <button id="f-programme_stream" type="button" class="select-control" :class="form.programme_stream ? '' : 'select-placeholder'" :aria-labelledby="'f-programme_stream-label f-programme_stream-value'" :aria-expanded="openDropdown === 'programme_stream'" aria-haspopup="listbox" @click="toggleDropdown('programme_stream')" @keydown.esc="openDropdown = ''">
                    <span id="f-programme_stream-value">{{ optionLabel(STREAMS, form.programme_stream) }}</span><ChevronDown :size="17" class="text-[#737780] transition-transform" :class="openDropdown === 'programme_stream' ? 'rotate-180' : ''" />
                  </button>
                  <div v-if="openDropdown === 'programme_stream'" class="select-menu" role="listbox" aria-labelledby="f-programme_stream-label">
                    <button v-for="o in opts(STREAMS)" :key="o.value" type="button" role="option" :aria-selected="form.programme_stream === o.value" class="select-option" :class="form.programme_stream === o.value ? 'select-option-active' : ''" @click="chooseOption('programme_stream', o.value)">{{ o.label }}<Check v-if="form.programme_stream === o.value" :size="16" /></button>
                  </div>
                </div>
              </div>
              <div>
                <label id="f-referral_source-label" class="lbl">Referral source</label>
                <div class="relative" data-client-dropdown>
                  <button id="f-referral_source" type="button" class="select-control" :class="form.referral_source ? '' : 'select-placeholder'" :aria-labelledby="'f-referral_source-label f-referral_source-value'" :aria-expanded="openDropdown === 'referral_source'" aria-haspopup="listbox" @click="toggleDropdown('referral_source')" @keydown.esc="openDropdown = ''">
                    <span id="f-referral_source-value">{{ optionLabel(REFERRALS, form.referral_source) }}</span><ChevronDown :size="17" class="text-[#737780] transition-transform" :class="openDropdown === 'referral_source' ? 'rotate-180' : ''" />
                  </button>
                  <div v-if="openDropdown === 'referral_source'" class="select-menu" role="listbox" aria-labelledby="f-referral_source-label">
                    <button v-for="o in opts(REFERRALS)" :key="o.value" type="button" role="option" :aria-selected="form.referral_source === o.value" class="select-option" :class="form.referral_source === o.value ? 'select-option-active' : ''" @click="chooseOption('referral_source', o.value)">{{ o.label }}<Check v-if="form.referral_source === o.value" :size="16" /></button>
                  </div>
                </div>
              </div>
              <div v-if="form.referral_source === 'Other'">
                <label class="lbl" for="f-referral_source_other">Describe the referral source</label>
                <input id="f-referral_source_other" v-model="form.referral_source_other" class="inp" type="text" autocomplete="off" />
              </div>
            </div>
          </div>
        </section>

        <div v-if="saver.error" class="flex items-start gap-3 rounded-xl bg-[#FBE0E4] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
          <AlertCircle :size="20" class="mt-px shrink-0" />
          <ErrorMessage :message="saver.error" />
        </div>

        <!-- Action bar -->
        <div class="sticky bottom-3 z-10 flex flex-col-reverse items-stretch justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white/95 p-3 backdrop-blur sm:flex-row sm:items-center">
          <p class="hidden px-2 text-[13px] text-[#5B616B] sm:block"><span class="text-[#A10E24]">*</span> Required to identify the client</p>
          <div class="flex flex-col-reverse gap-2 sm:flex-row">
            <router-link
              :to="back"
              class="inline-flex h-11 items-center justify-center rounded-[10px] border border-[#D5D8DE] bg-white px-[18px] text-sm font-semibold transition hover:bg-[#F4F5F7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
            >Cancel</router-link>
            <button
              type="submit"
              :disabled="saver.loading"
              class="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] border border-[#C8102E] bg-[#C8102E] px-[22px] text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40 focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-70"
            >
              <Loader2 v-if="saver.loading" :size="18" class="animate-spin" />
              <Check v-else :size="18" />
              {{ isNew ? "Register client" : "Save changes" }}
            </button>
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
import { GENDERS, REFERRALS, STREAMS } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !clientName.value)
const back = computed(() => (isNew.value ? { name: "Clients" } : { name: "ClientProfile", params: { name: clientName.value } }))

const TEXT = ["full_name", "phone_number", "gender", "disability_type", "institution",
	"course_programme", "county_location", "programme_stream", "referral_source", "referral_source_other"]
const NUMBERS = ["age", "year_of_study"]
const CHECKS = ["disability_status", "refugee_status"]

const form = reactive({
	...Object.fromEntries([...TEXT, ...NUMBERS].map((k) => [k, ""])),
	scholar_code: "",
	disability_status: false,
	refugee_status: false,
})
const loading = ref(false)
const openDropdown = ref("")

// Option lists may be plain strings or { label, value } objects
const opts = (list) => (list || []).map((o) => (o !== null && typeof o === "object" ? { label: o.label ?? o.value, value: o.value ?? o.label } : { label: o, value: o }))
const optionLabel = (list, value) => opts(list).find((option) => option.value === value)?.label || "Select"
const toggleDropdown = (field) => { openDropdown.value = openDropdown.value === field ? "" : field }
const chooseOption = (field, value) => {
	form[field] = value
	openDropdown.value = ""
}
function closeDropdownOutside(event) {
	if (!event.target.closest("[data-client-dropdown]")) openDropdown.value = ""
}

const profile = createResource({
	url: "krcti_mhpss.api.counsellor.client_profile",
	onSuccess(data) {
		const c = data.client
		form.scholar_code = c.scholar_code ?? ""
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
onMounted(() => document.addEventListener("click", closeDropdownOutside))
onUnmounted(() => document.removeEventListener("click", closeDropdownOutside))

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
	saver.submit({ name: clientName.value || undefined, data })
}
</script>

<style scoped>
.lbl {
	display: block;
	margin-bottom: 6px;
	font-size: 14px;
	font-weight: 500;
	line-height: 20px;
	color: #2b2f36;
}
.req { color: #a10e24; }
.hint {
	margin-top: 6px;
	font-size: 13px;
	line-height: 18px;
	color: #5b616b;
}

.inp {
	display: block;
	width: 100%;
	height: 44px;
	border: 1px solid #d5d8de;
	border-radius: 10px;
	background: #fff;
	padding: 0 12px;
	font: 400 14px/20px Inter, system-ui, sans-serif;
	color: #2b2f36;
	transition: border-color 0.15s, box-shadow 0.15s;
}
.inp::placeholder { color: #6b717b; }
.inp:hover:not(:disabled) { border-color: #b5bac3; }
.inp:focus {
	outline: none;
	border-color: #c8102e;
	box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.15);
}
.inp:disabled {
	cursor: not-allowed;
	background: #f4f5f7;
	color: #5b616b;
}
.inp:read-only {
	cursor: default;
	background: #f4f5f7;
	color: #5b616b;
}

.select-control {
	display: flex;
	width: 100%;
	height: 44px;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	border: 1px solid #d5d8de;
	border-radius: 10px;
	background: #fff;
	padding: 0 12px;
	font: 400 14px/20px Inter, system-ui, sans-serif;
	text-align: left;
	color: #2b2f36;
	transition: border-color .15s, box-shadow .15s;
}
.select-control:hover { border-color: #b5bac3; }
.select-control:focus-visible { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, .15); }
.select-placeholder { color: #6b717b; }
.select-menu {
	position: absolute;
	z-index: 30;
	top: calc(100% + 8px);
	left: 0;
	width: 100%;
	max-height: 240px;
	overflow-y: auto;
	border: 1px solid #e4e6ea;
	border-radius: 12px;
	background: #fff;
	padding: 6px;
	box-shadow: 0 12px 30px rgba(31, 35, 45, .14);
}
.select-option {
	display: flex;
	min-height: 40px;
	width: 100%;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	border-radius: 8px;
	padding: 8px 10px;
	text-align: left;
	font-size: 14px;
	color: #44474e;
	transition: background .15s, color .15s;
}
.select-option:hover { background: #f7f7f8; }
.select-option-active, .select-option-active:hover { background: #fce8eb; color: #a10e24; font-weight: 600; }

.choice {
	position: relative;
	display: flex;
	min-height: 72px;
	cursor: pointer;
	align-items: center;
	gap: 12px;
	border: 1px solid #e1e3e7;
	border-radius: 14px;
	background: #fff;
	padding: 13px 15px;
	transition: border-color .16s, background .16s, box-shadow .16s, transform .16s;
}
.choice:hover { border-color: #c9cbd1; background: #fcfcfd; }
.choice.is-on {
	border-color: #e6a5af;
	background: linear-gradient(135deg, #fff8f9 0%, #fdf1f3 100%);
	box-shadow: 0 2px 8px rgba(169, 20, 43, .07);
}
.choice:focus-within { box-shadow: 0 0 0 3px rgba(200, 16, 46, .13); }

.choice-input {
	position: absolute;
	height: 1px;
	width: 1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
	clip-path: inset(50%);
	opacity: 0;
}
.check-box {
	display: grid;
	height: 22px;
	width: 22px;
	flex-shrink: 0;
	place-items: center;
	border: 1.5px solid #c5c8cf;
	border-radius: 7px;
	background: #fff;
	color: transparent;
	transition: background .16s, border-color .16s, color .16s, box-shadow .16s, transform .16s;
}
.choice.is-on .check-box { transform: scale(1.03); border-color: #b30f2a; background: #b30f2a; color: #fff; box-shadow: 0 2px 5px rgba(179, 15, 42, .22); }
.choice.is-on .check-box svg { color: #fff; stroke: #fff; }
.choice-input:focus-visible + .check-box { outline: none; box-shadow: 0 0 0 3px rgba(200, 16, 46, .18); }
</style>
