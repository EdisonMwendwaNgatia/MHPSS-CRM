<template>
  <main class="mx-auto max-w-6xl px-4 py-6 md:px-7 md:py-8">
    <nav class="mb-6 flex flex-wrap gap-2 border-b border-[#E4E6EA] pb-3 text-sm" aria-label="Programme operations">
      <router-link v-for="tab in tabs" :key="tab.name" :to="{ name: tab.name }" class="rounded-lg px-3 py-2" :class="tab.name === route.name ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#4A505A] hover:bg-white'">{{ tab.label }}</router-link>
    </nav>

    <template v-if="kind === 'clients'">
      <div class="flex flex-wrap items-end justify-between gap-3"><div><h1 class="title">Programme clients</h1><p class="sub">Client records and case history within your programme.</p></div><router-link :to="{ name: 'ProgrammeClientNew' }" class="primary">Register client</router-link></div>
      <input v-model="search" class="field mt-5 max-w-md" type="search" placeholder="Search code, name or phone" />
      <ErrorMessage class="mt-3" :message="clients.error" />
      <div class="mt-4 overflow-x-auto rounded-xl border border-[#E4E6EA] bg-white"><table class="w-full text-left text-sm"><thead><tr class="bg-[#F4F5F7] text-[#5B616B]"><th class="p-3">Participant code</th><th class="p-3">Client</th><th class="p-3">Counsellor</th><th class="p-3">Case status</th><th class="p-3"></th></tr></thead><tbody><tr v-for="row in clients.data?.clients || []" :key="row.name" class="border-t border-[#E4E6EA]"><td class="p-3 font-medium">{{ row.scholar_code }}</td><td class="p-3">{{ row.full_name }}</td><td class="p-3">{{ row.counsellor_name }}</td><td class="p-3">{{ row.case_status }}</td><td class="p-3"><router-link :to="{ name: 'ProgrammeClientDetail', params: { name: row.name } }" class="link">View record</router-link></td></tr></tbody></table><p v-if="!clients.loading && !clients.data?.clients?.length" class="p-6 text-sm text-[#5B616B]">No clients found.</p></div>
    </template>

    <template v-else-if="kind === 'client'">
      <PageLoader v-if="client.loading && !client.data" />
      <template v-else-if="client.data">
        <router-link :to="{ name: 'ProgrammeClients' }" class="link text-sm">← Programme clients</router-link>
        <h1 class="title mt-3">{{ client.data.full_name }}</h1><p class="sub">{{ client.data.scholar_code }} · {{ client.data.case_status }} · {{ client.data.programme_stream }}</p>
        <section class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-5"><h2 class="font-semibold">Client information</h2><div class="mt-3 grid gap-3 text-sm sm:grid-cols-2"><p><b>Phone:</b> {{ client.data.phone_number }}</p><p><b>Age:</b> {{ client.data.age }}</p><p><b>Sex:</b> {{ client.data.gender }}</p><p><b>Institution:</b> {{ client.data.institution }}</p><p><b>Counsellor:</b> {{ client.data.assigned_counsellor }}</p><p><b>Referral source:</b> {{ [client.data.referral_source, client.data.referral_source_other].filter(Boolean).join(' — ') }}</p></div></section>
        <section class="mt-5 rounded-xl border border-[#E4E6EA] bg-white p-5"><h2 class="font-semibold">Case history</h2><ol class="mt-3 divide-y divide-[#E4E6EA]"><li v-for="entry in client.data.case_history || []" :key="entry.name" class="py-4"><div class="flex flex-wrap items-center justify-between gap-2"><div class="font-medium">{{ dateTime(entry.date_time) }} · {{ entry.session_type }} · {{ entry.status }}</div><span class="text-xs text-[#5B616B]">{{ entry.counsellor_name }}</span></div><div v-if="entry.status === 'Completed'" class="mt-3 grid gap-3 text-sm sm:grid-cols-2"><p><b>Mode:</b> {{ entry.mode_of_contact }}</p><p><b>Presenting issues:</b> {{ issueText(entry.presenting_issues) }}</p><p><b>Session details:</b> {{ entry.session_details }}</p><p><b>Interventions:</b> {{ entry.interventions_applied }}</p><p><b>Risk:</b> {{ entry.urgency_level }} · {{ entry.risk_assessment }}</p><p><b>Follow-up:</b> {{ entry.needs_follow_up }} · {{ entry.follow_up_plan }}</p><template v-if="entry.session_type === 'Follow-Up'"><p><b>Wellbeing:</b> {{ entry.followup_wellbeing_rating }}</p><p><b>Stress frequency:</b> {{ entry.followup_stress_frequency }}</p><p><b>Progress:</b> {{ entry.progress_previous_goals }}</p><p><b>Current concerns:</b> {{ entry.followup_new_issues }}</p><p><b>Coping and support:</b> {{ entry.followup_coping_support }}</p><p><b>Next steps:</b> {{ entry.followup_recommendations }} {{ entry.followup_takeaways }} {{ entry.next_session_focus }}</p></template><audio v-if="entry.audio_recording" controls preload="none" class="mt-2 max-w-md"> <source :src="entry.audio_recording" /></audio></div><div v-for="referral in entry.referral_history || []" :key="`ref-${referral.referred_on}`" class="mt-2 text-xs text-[#3767A6]">Referred {{ referral.from_name }} → {{ referral.to_name }} on {{ dateTime(referral.referred_on) }}. {{ referral.reason }}</div><div v-for="action in entry.management_history || []" :key="`manage-${action.event_time}`" class="mt-2 text-xs text-[#5B616B]">{{ action.event_type }} by {{ action.manager_name }} on {{ dateTime(action.event_time) }}: {{ action.reason }}<span v-if="action.to_name"> · {{ action.from_name }} → {{ action.to_name }}</span></div></li></ol><p v-if="!client.data.case_history?.length" class="mt-3 text-sm text-[#5B616B]">No session history yet.</p></section>
      </template><ErrorMessage v-else :message="client.error" />
    </template>

    <template v-else-if="kind === 'counsellors'">
      <div class="flex flex-wrap items-end justify-between gap-3"><div><h1 class="title">Counsellor management</h1><p class="sub">Create and manage counsellor accounts for your programme.</p></div><button class="primary" @click="showCreate = !showCreate">{{ showCreate ? 'Close' : 'Create counsellor' }}</button></div>
      <form v-if="showCreate" class="mt-4 grid gap-3 rounded-xl border border-[#E4E6EA] bg-white p-4 sm:grid-cols-2" @submit.prevent="createCounsellor"><input v-model="newUser.first_name" class="field" required placeholder="First name" /><input v-model="newUser.last_name" class="field" placeholder="Last name" /><input v-model="newUser.email" class="field" required type="email" placeholder="Email" /><input v-model="newUser.password" class="field" required type="password" minlength="8" placeholder="Password: uppercase, number and symbol" /><ErrorMessage class="sm:col-span-2" :message="saveUser.error" /><button class="primary w-fit" :disabled="saveUser.loading">Create account</button></form>
      <ErrorMessage class="mt-3" :message="counsellors.error || saveUser.error" />
      <div class="mt-4 overflow-x-auto rounded-xl border border-[#E4E6EA] bg-white"><table class="w-full text-left text-sm"><thead><tr class="bg-[#F4F5F7] text-[#5B616B]"><th class="p-3">Counsellor</th><th class="p-3">Email</th><th class="p-3">Status</th><th class="p-3">Last login</th><th class="p-3">Account</th></tr></thead><tbody><tr v-for="row in counsellors.data || []" :key="row.name" class="border-t border-[#E4E6EA]"><td class="p-3">{{ row.full_name }}</td><td class="p-3">{{ row.name }}</td><td class="p-3">{{ row.enabled ? 'Active' : 'Inactive' }}</td><td class="p-3">{{ dateTime(row.last_login) }}</td><td class="p-3"><button v-if="row.enabled" class="link" :disabled="saveUser.loading" @click="retireCounsellor(row, 'deactivate')">Deactivate</button><button v-else class="link" :disabled="saveUser.loading" @click="retireCounsellor(row, 'remove')">Remove</button></td></tr></tbody></table><p v-if="!counsellors.loading && !counsellors.data?.length" class="p-6 text-sm text-[#5B616B]">No counsellor accounts in this programme.</p></div>
      <p class="mt-2 text-xs text-[#5B616B]">Removing a counsellor disables their account and preserves their historical records.</p>
    </template>

    <template v-else-if="kind === 'sessions'">
      <h1 class="title">Session management</h1><p class="sub">View all scheduled appointments, including overdue ones. Reassign or cancel and record the reason.</p>
      <ErrorMessage class="mt-3" :message="sessions.error || manageSession.error" />
      <div class="mt-4 overflow-x-auto rounded-xl border border-[#E4E6EA] bg-white"><table class="w-full text-left text-sm"><thead><tr class="bg-[#F4F5F7] text-[#5B616B]"><th class="p-3">Date</th><th class="p-3">Participant</th><th class="p-3">Counsellor</th><th class="p-3">Session</th><th class="p-3">Status</th><th class="p-3">Case history</th><th class="p-3"></th></tr></thead><tbody><tr v-for="row in sessions.data || []" :key="row.name" class="border-t border-[#E4E6EA]"><td class="p-3">{{ dateTime(row.date_time) }}</td><td class="p-3">{{ row.scholar_code }}</td><td class="p-3">{{ row.counsellor_name }}</td><td class="p-3">{{ row.session_type }} · {{ row.mode_of_contact }}</td><td class="p-3"><span :class="row.overdue ? 'font-semibold text-[#A10E24]' : 'text-[#1B4DB1]'">{{ row.overdue ? 'Overdue' : 'Scheduled' }}</span></td><td class="p-3"><router-link :to="{ name: 'ProgrammeClientDetail', params: { name: row.client_id } }" class="link">View record</router-link></td><td class="p-3"><button class="link" @click="openSession(row)">Manage</button></td></tr></tbody></table><p v-if="!sessions.loading && !sessions.data?.length" class="p-6 text-sm text-[#5B616B]">No scheduled sessions.</p></div>
      <div v-if="selectedSession" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" @click.self="selectedSession = null"><form class="w-full max-w-lg space-y-3 rounded-xl bg-white p-5" @submit.prevent="submitSessionAction"><h2 class="text-lg font-semibold">Manage {{ selectedSession.scholar_code }}</h2><p class="text-sm">{{ dateTime(selectedSession.date_time) }} · {{ selectedSession.counsellor_name }}</p><select v-model="sessionAction" class="field"><option value="reassign">Reassign session</option><option value="cancel">Cancel session</option></select><select v-if="sessionAction === 'reassign'" v-model="targetCounsellor" class="field" required><option value="">Choose counsellor</option><option v-for="person in counsellors.data || []" :key="person.name" :value="person.name" :disabled="!person.enabled || person.name === selectedSession.counsellor_id">{{ person.full_name }}{{ person.enabled ? '' : ' (inactive)' }}</option></select><textarea v-model="actionReason" class="field" rows="3" required minlength="3" maxlength="2000" placeholder="Reason for this change" /><ErrorMessage :message="manageSession.error" /><div class="flex justify-end gap-2"><button type="button" class="secondary" @click="selectedSession = null">Close</button><button class="primary" :disabled="manageSession.loading">Save</button></div></form></div>
    </template>

    <template v-else>
      <h1 class="title">Counsellor activity</h1><p class="sub">Operational activity and account access events for counsellors in your programme.</p>
      <label class="mt-4 block max-w-md text-sm font-medium">Counsellor<select v-model="selectedUser" class="field mt-1.5"><option value="">Choose counsellor</option><option v-for="person in counsellors.data || []" :key="person.name" :value="person.name">{{ person.full_name }}</option></select></label>
      <ErrorMessage class="mt-3" :message="activity.error" /><section class="mt-4 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white"><ActivityTable :rows="activity.data?.logs || []" :loading="activity.loading" /><p v-if="selectedUser && !activity.loading && !activity.data?.logs?.length" class="p-5 text-sm text-[#5B616B]">No activity recorded.</p></section>
    </template>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"
import { useRoute } from "vue-router"
import ActivityTable from "../components/ActivityTable.vue"
import { fmtDateTime } from "../data/format"

const props = defineProps({ kind: { type: String, required: true } })
const route = useRoute()
const kind = computed(() => props.kind)
const tabs = [{ name: "ProgrammeClients", label: "Clients" }, { name: "ProgrammeCounsellors", label: "Counsellors" }, { name: "ProgrammeSessions", label: "Sessions" }, { name: "ProgrammeActivity", label: "Activity" }]
const clients = createResource({ url: "krcti_mhpss.api.oversight.programme_clients" })
const client = createResource({ url: "krcti_mhpss.api.oversight.programme_client_detail" })
const counsellors = createResource({ url: "krcti_mhpss.api.oversight.programme_counsellors" })
const sessions = createResource({ url: "krcti_mhpss.api.oversight.programme_sessions" })
const activity = createResource({ url: "krcti_mhpss.api.oversight.programme_counsellor_activity" })
const saveUser = createResource({ url: "krcti_mhpss.api.oversight.programme_save_counsellor", onSuccess: () => { showCreate.value = false; newUser.first_name = newUser.last_name = newUser.email = newUser.password = ""; counsellors.submit() } })
const manageSession = createResource({ url: "krcti_mhpss.api.oversight.programme_manage_session", onSuccess: () => { selectedSession.value = null; sessions.submit() } })
const search = ref("")
const showCreate = ref(false)
const newUser = reactive({ first_name: "", last_name: "", email: "", password: "" })
const selectedSession = ref(null)
const sessionAction = ref("reassign")
const targetCounsellor = ref("")
const actionReason = ref("")
const selectedUser = ref("")
let timer
const dateTime = (value) => value ? fmtDateTime(value) : "—"
const issueText = (value) => { try { const parsed = JSON.parse(value); return Array.isArray(parsed) ? parsed.join(", ") : value } catch { return value || "—" } }
function load() {
  if (kind.value === "clients") clients.submit({ search: search.value })
  if (kind.value === "client") client.submit({ name: route.params.name })
  if (["counsellors", "sessions", "activity"].includes(kind.value)) counsellors.submit()
  if (kind.value === "sessions") sessions.submit()
}
watch(search, () => { clearTimeout(timer); timer = setTimeout(() => clients.submit({ search: search.value }), 250) })
watch(selectedUser, (user) => { if (user) activity.submit({ user }) })
watch([kind, () => route.params.name], load, { immediate: true })
function createCounsellor() { saveUser.submit({ ...newUser, action: "create" }) }
function retireCounsellor(row, action) { if (window.confirm(`${action === 'deactivate' ? 'Deactivate' : 'Remove'} ${row.full_name}? Their history will remain available.`)) saveUser.submit({ user: row.name, action }) }
function openSession(row) { selectedSession.value = row; targetCounsellor.value = ""; actionReason.value = ""; sessionAction.value = "reassign" }
function submitSessionAction() { manageSession.submit({ name: selectedSession.value.name, action: sessionAction.value, counsellor: targetCounsellor.value, reason: actionReason.value }) }
</script>

<style scoped>
.title{font-size:24px;font-weight:650;color:#2b2f36}.sub{margin-top:4px;font-size:14px;color:#5b616b}.field{display:block;min-height:42px;width:100%;border:1px solid #d5d8de;border-radius:8px;background:#fff;padding:9px 11px;font-size:14px;color:#2b2f36}.field:focus{outline:none;border-color:#c8102e;box-shadow:0 0 0 2px #c8102e22}.primary,.secondary{display:inline-flex;min-height:40px;align-items:center;justify-content:center;border-radius:8px;padding:0 14px;font-size:13px;font-weight:600}.primary{background:#c8102e;color:#fff}.primary:disabled{opacity:.55}.secondary{border:1px solid #d5d8de;background:white;color:#2b2f36}.link{color:#a10e24;font-weight:600}.link:hover{text-decoration:underline}
</style>
