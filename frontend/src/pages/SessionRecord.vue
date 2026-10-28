<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1040px]">
      <router-link :to="backTo" class="inline-flex h-10 items-center gap-2 text-sm font-medium text-[#5B616B] hover:text-[#A10E24]"><ArrowLeft :size="17" /> Back</router-link>
      <PageLoader v-if="resource.loading && !resource.data" />
      <template v-else-if="record">
        <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-[#A10E24]">{{ record.session_type }} · {{ record.name }}</p>
            <h1 class="mt-1 text-2xl font-semibold">{{ isReadOnly ? 'Session record' : 'In-session record' }}</h1>
            <p class="mt-1 text-sm text-[#5B616B]">{{ record.client_name }} · {{ record.scholar_code }} · {{ fmtDateTime(record.date_time) }}</p>
          </div>
          <Badge :label="record.status === 'Scheduled' ? (record.overdue ? 'Overdue' : 'Scheduled') : record.status" :theme="record.status === 'Completed' ? 'green' : record.overdue ? 'red' : 'blue'" />
        </div>

        <section class="mt-6 rounded-xl border border-[#E4E6EA] bg-white">
          <div class="border-b border-[#ECEDEF] px-5 py-4 sm:px-6">
            <h2 class="text-base font-semibold">Case history</h2>
            <p class="mt-1 text-sm text-[#5B616B]">Chronological history for {{ record.client_name }}. Review earlier sessions before recording this one.</p>
          </div>
          <ol v-if="history.length" class="divide-y divide-[#ECEDEF]">
            <li v-for="item in history" :key="item.name" class="px-5 py-4 sm:px-6">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div><span class="font-semibold">{{ fmtDateTime(item.date_time) }}</span><span class="ml-2 text-sm text-[#5B616B]">{{ item.session_type }} · {{ item.mode_of_contact }}</span></div>
                <Badge :label="item.status === 'Scheduled' && item.overdue ? 'Overdue' : item.status" :theme="item.status === 'Completed' ? 'green' : item.overdue ? 'red' : item.status === 'Cancelled' ? 'gray' : 'blue'" />
              </div>
              <div v-if="item.status === 'Completed'" class="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                <p><span class="font-medium">Presenting issues:</span> {{ item.presenting_issues || '—' }}</p>
                <p><span class="font-medium">Issue subclassifications:</span> {{ item.issue_subclassifications || '—' }}</p>
                <p><span class="font-medium">Interventions:</span> {{ item.interventions_applied || '—' }}</p>
                <p><span class="font-medium">Referrals:</span> {{ item.referrals_made || '—' }}</p>
                <p><span class="font-medium">Urgency:</span> {{ item.urgency_level || '—' }}</p>
                <p><span class="font-medium">Risk assessment:</span> {{ item.risk_assessment || '—' }}</p>
                <p class="sm:col-span-2"><span class="font-medium">Session details:</span> {{ item.session_details || '—' }}</p>
                <p class="sm:col-span-2"><span class="font-medium">Follow-up plan:</span> {{ item.follow_up_plan || '—' }}</p>
                <template v-if="item.session_type === 'Follow-Up'">
                  <p><span class="font-medium">Progress on previous goals:</span> {{ item.progress_previous_goals || '—' }}</p>
                  <p><span class="font-medium">Counsellor observations:</span> {{ item.counsellor_observations || '—' }}</p>
                  <p class="sm:col-span-2"><span class="font-medium">Next session focus:</span> {{ item.next_session_focus || '—' }}</p>
                </template>
                <div v-if="item.audio_recording" class="sm:col-span-2">
                  <p class="mb-2 font-medium">Session audio</p>
                  <audio controls preload="none" class="w-full max-w-xl" :src="item.audio_recording">Your browser does not support audio playback.</audio>
                </div>
              </div>
              <p v-else class="mt-2 text-sm text-[#5B616B]">{{ item.status === 'Scheduled' ? 'Session is scheduled.' : 'Session was cancelled.' }}</p>
              <div v-if="item.referral_history?.length" class="mt-3 space-y-2 rounded-lg bg-[#F1F5FB] px-3.5 py-3">
                <p v-for="referral in item.referral_history" :key="referral.name || referral.referred_on" class="text-xs leading-5 text-[#315A91]">
                  <span class="font-semibold">Referral:</span> {{ referral.from_name || referral.from_counsellor }} → {{ referral.to_name || referral.to_counsellor }} · {{ fmtDateTime(referral.referred_on) }}. {{ referral.reason }}
                </p>
              </div>
            </li>
          </ol>
          <p v-else class="px-5 py-8 text-sm text-[#737780]">No earlier sessions are recorded for this client.</p>
        </section>

        <section v-if="record.status === 'Completed' || (!caseClosed && record.status === 'Scheduled' && canManage)" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white">
          <div class="border-b border-[#ECEDEF] px-5 py-4 sm:px-6">
            <h2 class="text-base font-semibold">{{ isReadOnly ? 'Recorded summary' : 'Session summary' }}</h2>
            <p class="mt-1 text-sm text-[#5B616B]">Capture the session details, issues, interventions, referrals, urgency, risk, and follow-up plan.</p>
          </div>
          <form class="space-y-5 p-5 sm:p-6" @submit.prevent="save">
            <fieldset :disabled="isReadOnly" class="space-y-5">
              <div class="grid gap-4 sm:grid-cols-2">
                <Field label="Session details" required><textarea v-model="form.session_details" class="field" rows="3" required /></Field>
                <Field label="Presenting issues" required><textarea v-model="form.presenting_issues" class="field" rows="3" required /></Field>
                <Field label="Issue subclassifications"><textarea v-model="form.issue_subclassifications" class="field" rows="3" placeholder="Add relevant categories or descriptors" /></Field>
                <Field label="Interventions applied" required><textarea v-model="form.interventions_applied" class="field" rows="3" required /></Field>
                <Field label="Referrals made"><textarea v-model="form.referrals_made" class="field" rows="3" placeholder="Enter referral or write None" /></Field>
                <Field label="Urgency level" required>
                  <select v-model="form.urgency_level" class="field" required><option value="" disabled>Select urgency</option><option v-for="level in urgencyLevels" :key="level">{{ level }}</option></select>
                </Field>
                <Field label="Risk assessment" required><textarea v-model="form.risk_assessment" class="field" rows="3" required /></Field>
                <Field label="Follow-up plan" required><textarea v-model="form.follow_up_plan" class="field" rows="3" required /></Field>
              </div>

              <div v-if="record.session_type === 'Follow-Up'" class="rounded-xl border border-[#F0D6DA] bg-[#FFFAFB] p-4 sm:p-5">
                <h3 class="font-semibold">Follow-up review</h3>
                <p class="mt-1 text-sm text-[#5B616B]">Link this entry to the client’s existing case history.</p>
                <div class="mt-4 grid gap-4 sm:grid-cols-2">
                  <Field label="Progress on previous goals" required><textarea v-model="form.progress_previous_goals" class="field" rows="3" required /></Field>
                  <Field label="Counsellor observations" required><textarea v-model="form.counsellor_observations" class="field" rows="3" required /></Field>
                  <Field label="Next session focus" required><textarea v-model="form.next_session_focus" class="field" rows="3" required /></Field>
                </div>
              </div>
            </fieldset>

            <ErrorMessage v-if="saver.error" :message="saver.error" />
            <div v-if="caseClosed" class="rounded-lg bg-[#F4F5F7] px-4 py-3 text-sm text-[#5B616B]">This case is closed. Its session records are available in read-only mode.</div>
            <div v-else-if="!isReadOnly" class="flex flex-wrap justify-end gap-3 border-t border-[#ECEDEF] pt-5">
              <router-link :to="backTo" class="inline-flex h-11 items-center rounded-[10px] border border-[#D5D8DE] px-4 text-sm font-semibold hover:bg-[#F4F5F7]">Cancel</router-link>
              <button type="submit" :disabled="saver.loading" class="inline-flex h-11 items-center gap-2 rounded-[10px] bg-[#C8102E] px-5 text-sm font-semibold text-white hover:bg-[#A10E24] disabled:opacity-60"><Loader2 v-if="saver.loading" :size="17" class="animate-spin" /><Check v-else :size="17" /> Save session record</button>
            </div>
          </form>
        </section>
        <div v-else class="mt-5 rounded-xl border border-[#E4E6EA] bg-white px-5 py-6 text-sm text-[#5B616B]">{{ caseClosed ? 'This case is closed. Its records are available in read-only mode.' : record.status === 'Scheduled' && !canManage ? `This appointment was referred to ${record.counsellor_name || record.counsellor_id} and is now on their schedule.` : 'This appointment was cancelled, so it cannot be recorded.' }}</div>
        <section v-if="record.status === 'Completed' || (!caseClosed && record.status === 'Scheduled' && canManage)" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-5 sm:p-6">
          <h2 class="text-base font-semibold">Session audio <span class="font-normal text-[#737780]">(optional)</span></h2>
          <p class="mt-1 text-sm text-[#5B616B]">Upload an audio recording if one is available. The file is stored privately with this session.</p>
          <div v-if="audioUrl" class="mt-4 rounded-lg border border-[#E4E6EA] bg-[#F8F9FA] p-4">
            <audio controls preload="none" class="w-full" :src="audioUrl">Your browser does not support audio playback.</audio>
          </div>
          <FileUploader v-if="!isReadOnly" class="mt-4" :fileTypes="['audio/*']" :validateFile="validateAudio" :uploadArgs="audioUploadArgs" @success="onAudioUploaded">
            <template #default="{ uploading, progress, openFileSelector, error }">
              <button type="button" :disabled="uploading" class="inline-flex h-10 items-center gap-2 rounded-[10px] border border-[#D5D8DE] px-4 text-sm font-semibold hover:bg-[#F4F5F7] disabled:opacity-60" @click="openFileSelector">
                <Loader2 v-if="uploading" :size="16" class="animate-spin" />
                <Upload v-else :size="16" />
                {{ uploading ? `Uploading ${progress}%` : audioUrl ? 'Replace audio file' : 'Upload audio file' }}
              </button>
              <p v-if="error" class="mt-2 text-sm text-[#A10E24]">{{ error }}</p>
            </template>
          </FileUploader>
        </section>
      </template>
      <ErrorMessage v-else :message="resource.error" />
    </div>
  </main>
</template>

<script setup>
import { createResource, FileUploader } from "frappe-ui"
import { computed, h, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, Check, Loader2, Upload } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const name = computed(() => props.name || route.params.name || "")
const urgencyLevels = ["Low", "Moderate", "High", "Immediate"]
const recordFields = [
	"session_details", "presenting_issues", "issue_subclassifications", "interventions_applied", "referrals_made",
	"urgency_level", "risk_assessment", "follow_up_plan", "progress_previous_goals", "counsellor_observations", "next_session_focus",
]
const form = reactive({
	session_details: "", presenting_issues: "", issue_subclassifications: "", interventions_applied: "",
	referrals_made: "", urgency_level: "", risk_assessment: "", follow_up_plan: "",
	progress_previous_goals: "", counsellor_observations: "", next_session_focus: "",
})
const uploadedAudio = ref("")
const audioUrl = computed(() => uploadedAudio.value || record.value?.audio_recording || "")
const audioUploadArgs = computed(() => ({
	doctype: "Appointment",
	docname: name.value,
	fieldname: "audio_recording",
	private: true,
}))
const resource = createResource({
	url: "krcti_mhpss.api.records.session_record_detail",
	onSuccess(data) {
		for (const field of recordFields) form[field] = data.appointment[field] ?? ""
	},
})
const record = computed(() => resource.data?.appointment)
const history = computed(() => resource.data?.history || [])
const caseClosed = computed(() => resource.data?.case_status === "Closed")
const canManage = computed(() => resource.data?.can_manage === true)
const isReadOnly = computed(() => record.value?.status === "Completed" || record.value?.status === "Cancelled" || caseClosed.value || !canManage.value)
const backTo = computed(() => !canManage.value
	? { name: "ClientProfile", params: { name: record.value?.client_id } }
	: record.value?.status === "Completed"
		? { name: "SessionRecords" }
	: record.value?.status === "Scheduled" && record.value?.session_type === "Follow-Up"
		? { name: "FollowUps" }
		: { name: "Appointments" })
onMounted(() => resource.submit({ name: name.value }))

const saver = createResource({
	url: "krcti_mhpss.api.records.record_session",
	onSuccess() { router.replace({ name: "SessionRecords" }) },
})
function save() {
	saver.submit({ name: name.value, data: Object.fromEntries(recordFields.map((field) => [field, form[field]])) })
}
function onAudioUploaded(file) {
	uploadedAudio.value = file?.file_url || ""
}
function validateAudio(file) {
	return file.type?.startsWith("audio/") ? "" : "Choose an audio file."
}

const Field = (props, { slots }) => h("label", { class: "block text-sm font-medium text-[#33353A]" }, [
	h("span", { class: "mb-1.5 block" }, `${props.label}${props.required ? " *" : ""}`),
	slots.default?.(),
])
</script>

<style scoped>
.field { display:block; width:100%; min-height:44px; border:1px solid #d5d8de; border-radius:10px; background:#fff; padding:10px 12px; font:14px/20px Inter,system-ui,sans-serif; color:#2b2f36; }
.field:focus { outline:none; border-color:#c8102e; box-shadow:0 0 0 3px rgba(200,16,46,.12); }
fieldset:disabled .field { background:#f4f5f7; color:#5b616b; }
</style>
