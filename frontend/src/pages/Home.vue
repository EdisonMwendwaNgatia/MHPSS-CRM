<template>
  <main class="min-h-[calc(100vh-72px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <PageLoader v-if="home.loading && !home.data" />
      <ErrorMessage class="mb-5" :message="home.error" />

      <template v-if="home.data">
        <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p class="text-sm font-medium text-[#737780]">{{ todayLabel }}</p>
            <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Counsellor Dashboard</h1>
            <p class="mt-1 text-sm text-[#737780]">A clear view of your caseload and the work ahead.</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <router-link :to="{ name: 'AppointmentNew' }" class="inline-flex items-center gap-2 rounded-lg border border-[#D9DBE0] bg-white px-4 py-2.5 text-sm font-semibold text-[#34363B] shadow-sm transition hover:border-[#BFC2C8] hover:bg-[#FAFAFB]">
              <CalendarPlus :size="17" /> Schedule appointment
            </router-link>
            <router-link :to="{ name: 'ClientNew' }" class="inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#A10E24]">
              <UserRoundPlus :size="17" /> Register client
            </router-link>
          </div>
        </div>

        <div v-if="home.data.overdue_followups" class="mt-6 flex items-start gap-3 rounded-xl border border-[#F2D59B] bg-[#FFF8E9] px-4 py-3.5 text-[#765310]">
          <TriangleAlert class="mt-0.5 shrink-0" :size="19" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold">{{ home.data.overdue_followups }} follow-up{{ home.data.overdue_followups === 1 ? '' : 's' }} need attention</p>
            <p class="mt-0.5 text-sm text-[#876B31]">Review overdue follow-up appointments and update their status.</p>
          </div>
          <router-link :to="{ name: 'Appointments' }" class="shrink-0 text-sm font-semibold text-[#765310] underline underline-offset-2">Review</router-link>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <router-link v-for="stat in stats" :key="stat.label" :to="{ name: stat.route }" class="group rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(20,25,35,0.03)] transition hover:-translate-y-0.5 hover:border-[#D7A0AA] hover:shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <span class="text-sm font-medium text-[#737780]">{{ stat.label }}</span>
              <span class="flex h-9 w-9 items-center justify-center rounded-lg" :class="stat.iconBg"><component :is="stat.icon" :size="18" :class="stat.iconColor" /></span>
            </div>
            <p class="mt-4 text-[30px] font-semibold leading-none tracking-tight text-[#25272B]">{{ stat.value }}</p>
            <p class="mt-2 text-xs text-[#858891]">{{ stat.note }}</p>
          </router-link>
        </div>

        <div v-if="home.data.baselines_outstanding" class="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white px-4 py-3">
          <div class="flex items-center gap-2.5">
            <ClipboardList :size="18" class="text-[#C8102E]" />
            <p class="text-sm text-[#555860]"><span class="font-semibold text-[#25272B]">{{ home.data.baselines_outstanding }} baseline survey{{ home.data.baselines_outstanding === 1 ? '' : 's' }}</span> still to complete</p>
          </div>
          <router-link :to="{ name: 'Clients' }" class="text-sm font-semibold text-[#B30F2A] hover:underline">View clients <ArrowRight :size="14" class="ml-1 inline" /></router-link>
        </div>

        <div class="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.9fr)]">
          <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
            <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-4">
              <div>
                <h2 class="text-base font-semibold text-[#25272B]">Upcoming appointments</h2>
                <p class="mt-0.5 text-xs text-[#858891]">Your next scheduled client sessions</p>
              </div>
              <router-link :to="{ name: 'Appointments' }" class="text-sm font-semibold text-[#B30F2A] hover:underline">View all</router-link>
            </div>
            <div v-if="home.data.upcoming.length" class="overflow-x-auto">
              <table class="w-full min-w-[600px] text-left">
                <thead><tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><th class="px-5 py-3">Client</th><th class="px-4 py-3">Date &amp; time</th><th class="px-4 py-3">Session</th><th class="px-5 py-3 text-right">Status</th></tr></thead>
                <tbody class="divide-y divide-[#F0F1F3]">
                  <tr v-for="row in home.data.upcoming" :key="row.name" class="transition hover:bg-[#FCFCFD]">
                    <td class="px-5 py-3.5"><router-link :to="{ name: 'AppointmentEdit', params: { name: row.name } }" class="font-medium text-[#33353A] hover:text-[#B30F2A]">{{ row.client_name || row.client_id }}</router-link><p class="mt-0.5 text-xs text-[#858891]">{{ row.client_id }}</p></td>
                    <td class="px-4 py-3.5 text-sm text-[#555860]">{{ fmtDate(row.date_time) }}<p class="mt-0.5 text-xs text-[#858891]">{{ fmtTime(row.date_time) }}</p></td>
                    <td class="px-4 py-3.5"><span class="text-sm text-[#555860]">{{ row.session_type }}</span><p class="mt-0.5 text-xs text-[#858891]">{{ row.mode_of_contact }}</p></td>
                    <td class="px-5 py-3.5 text-right"><Badge :label="apptLabel(row)" :theme="apptTheme(row)" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="px-5 py-12 text-center"><CalendarDays class="mx-auto text-[#B9BBC1]" :size="25" /><p class="mt-3 text-sm font-medium text-[#555860]">No upcoming appointments</p><p class="mt-1 text-xs text-[#858891]">New sessions you schedule will appear here.</p></div>
          </section>

          <section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
            <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-4">
              <div><h2 class="text-base font-semibold text-[#25272B]">Follow-up actions</h2><p class="mt-0.5 text-xs text-[#858891]">Scheduled follow-up sessions</p></div>
              <router-link :to="{ name: 'FollowUps' }" class="text-sm font-semibold text-[#B30F2A] hover:underline">View all</router-link>
            </div>
            <div v-if="home.data.followups.length" class="divide-y divide-[#F0F1F3]">
              <router-link v-for="row in home.data.followups" :key="row.name" :to="{ name: 'SessionRecord', params: { name: row.name } }" class="flex items-center gap-3 px-5 py-4 transition hover:bg-[#FCFCFD]">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-[#B30F2A]"><UserRound :size="17" /></span>
                <span class="min-w-0 flex-1"><span class="block truncate text-sm font-medium text-[#33353A]">{{ row.client_name || row.client_id }}</span><span class="mt-1 block text-xs text-[#858891]">{{ fmtDate(row.date_time) }} · {{ fmtTime(row.date_time) }}</span></span>
                <span class="shrink-0 rounded-full px-2.5 py-1 text-[11px] font-semibold" :class="row.overdue ? 'bg-[#FDEBEC] text-[#B42332]' : 'bg-[#FFF4D9] text-[#8A6416]'">{{ row.overdue ? 'Overdue' : 'Upcoming' }}</span>
              </router-link>
            </div>
            <div v-else class="px-5 py-12 text-center"><HeartHandshake class="mx-auto text-[#B9BBC1]" :size="25" /><p class="mt-3 text-sm font-medium text-[#555860]">No follow-ups scheduled</p><p class="mt-1 text-xs text-[#858891]">Follow-up appointments will appear here.</p></div>
          </section>
        </div>

        <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
          <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-4"><div><h2 class="text-base font-semibold text-[#25272B]">Recent session records</h2><p class="mt-0.5 text-xs text-[#858891]">Recently completed appointments</p></div><router-link :to="{ name: 'SessionRecords' }" class="text-sm font-semibold text-[#B30F2A] hover:underline">View all records</router-link></div>
          <div v-if="home.data.recent_sessions.length" class="grid divide-y divide-[#F0F1F3] md:grid-cols-2 md:divide-x md:divide-y-0 xl:grid-cols-3">
            <router-link v-for="row in home.data.recent_sessions" :key="row.name" :to="{ name: 'SessionRecord', params: { name: row.name } }" class="flex items-center gap-3 px-5 py-4 transition hover:bg-[#FCFCFD]">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#EAF5EE] text-[#26834B]"><ClipboardCheck :size="17" /></span>
              <span class="min-w-0 flex-1"><span class="block truncate text-sm font-medium text-[#33353A]">{{ row.client_name || row.client_id }}</span><span class="mt-1 block truncate text-xs text-[#858891]">{{ row.session_type }} · {{ fmtDate(row.date_time) }}</span></span>
              <Badge label="Completed" theme="green" />
            </router-link>
          </div>
          <div v-else class="px-5 py-10 text-center"><p class="text-sm font-medium text-[#555860]">No completed sessions yet</p><p class="mt-1 text-xs text-[#858891]">Completed appointment records will appear here.</p></div>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, watch } from "vue"
import { useRouter } from "vue-router"
import { ArrowRight, CalendarDays, CalendarPlus, ClipboardCheck, ClipboardList, HeartHandshake, UsersRound, TriangleAlert, UserRound, UserRoundPlus } from "lucide-vue-next"
import { me } from "../data/me"
import { apptLabel, apptTheme, fmtDate, fmtTime } from "../data/format"

const router = useRouter()
const role = computed(() => me.data?.role)
const home = createResource({ url: "krcti_mhpss.api.counsellor.home" })
const todayLabel = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" })
const stats = computed(() => [
	{ label: "Active caseload", value: home.data?.active_clients ?? 0, note: "Clients assigned to you", route: "Clients", icon: UsersRound, iconBg: "bg-[#FCE8EB]", iconColor: "text-[#B30F2A]" },
	{ label: "Upcoming appointments", value: home.data?.upcoming_count ?? 0, note: "Scheduled sessions ahead", route: "Appointments", icon: CalendarDays, iconBg: "bg-[#EAF1FC]", iconColor: "text-[#3B69A8]" },
	{ label: "Sessions conducted", value: home.data?.sessions_conducted ?? 0, note: "Completed appointment records", route: "Appointments", icon: ClipboardCheck, iconBg: "bg-[#EAF5EE]", iconColor: "text-[#26834B]" },
	{ label: "Follow-ups pending", value: home.data?.followups_pending ?? 0, note: "Scheduled follow-up sessions", route: "Appointments", icon: HeartHandshake, iconBg: "bg-[#FFF4D9]", iconColor: "text-[#A87814]" },
])

onMounted(() => me.reload())
watch(
	role,
	(value) => {
		if (value === "counsellor") home.submit()
		else if (["krcti_pm", "woc_pm", "admin"].includes(value)) router.replace({ name: "Programme" })
	},
	{ immediate: true },
)
</script>
