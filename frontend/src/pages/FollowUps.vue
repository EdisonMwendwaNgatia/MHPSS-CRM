<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1100px]">
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div><h1 class="text-2xl font-semibold">Follow-ups</h1><p class="mt-1 text-sm text-[#5B616B]">Scheduled follow-up sessions linked to each client’s case history.</p></div>
        <router-link :to="{ name: 'AppointmentNew', query: { type: 'Follow-Up' } }" class="inline-flex h-11 items-center gap-2 rounded-[10px] bg-[#C8102E] px-4 text-sm font-semibold text-white hover:bg-[#A10E24]"><CalendarPlus :size="17" /> Book follow-up</router-link>
      </div>

      <div v-if="data?.overdue_total" class="mt-5 flex items-start gap-3 rounded-xl border border-[#F0C8CE] bg-[#FFF6F7] px-4 py-3.5 text-sm text-[#A10E24]" role="alert">
        <AlertTriangle :size="19" class="mt-0.5 shrink-0" /><p><strong>{{ data.overdue_total }} overdue follow-up{{ data.overdue_total === 1 ? '' : 's' }}.</strong> These are past the appointment date set by the counsellor.</p>
      </div>
      <ErrorMessage class="mt-4" :message="followups.error" />
      <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
        <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-4"><div><h2 class="font-semibold">Scheduled follow-up sessions</h2><p class="mt-1 text-xs text-[#737780]">{{ data?.followups?.length || 0 }} sessions</p></div><LoaderCircle v-if="followups.loading" :size="18" class="animate-spin text-[#737780]" /></div>
        <ul v-if="data?.followups?.length" class="divide-y divide-[#ECEDEF]">
          <li v-for="row in data.followups" :key="row.name" class="grid gap-3 px-5 py-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
            <div class="min-w-0">
              <router-link :to="{ name: 'ClientProfile', params: { name: row.client_id } }" class="font-semibold hover:text-[#A10E24]">{{ row.client_name || row.client_id }}</router-link>
              <p class="mt-1 text-xs text-[#737780]">{{ row.scholar_code }} · {{ fmtDateTime(row.date_time) }} · {{ row.mode_of_contact }}</p>
              <p v-if="row.overdue" class="mt-1 text-xs font-semibold text-[#A10E24]">Overdue against the scheduled date</p>
            </div>
            <div class="flex items-center gap-2 sm:justify-end"><Badge :label="row.overdue ? 'Overdue' : 'Scheduled'" :theme="row.overdue ? 'red' : 'blue'" /><router-link :to="{ name: 'SessionRecord', params: { name: row.name } }" class="inline-flex h-10 items-center gap-2 rounded-lg bg-[#C8102E] px-3.5 text-sm font-semibold text-white hover:bg-[#A10E24]"><ClipboardList :size="16" /> In-session</router-link></div>
          </li>
        </ul>
        <div v-else-if="!followups.loading" class="px-5 py-14 text-center"><HeartHandshake :size="28" class="mx-auto text-[#B9BBC1]" /><h3 class="mt-3 font-semibold">No scheduled follow-ups</h3><p class="mt-1 text-sm text-[#737780]">Schedule a Follow-Up appointment to add it here.</p></div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted } from "vue"
import { AlertTriangle, CalendarPlus, ClipboardList, HeartHandshake, LoaderCircle } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"

const followups = createResource({ url: "krcti_mhpss.api.counsellor.my_followups" })
const data = computed(() => followups.data)
onMounted(() => followups.submit())
</script>
