<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 font-[Inter,system-ui,sans-serif] text-[#2B2F36] sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1100px]">
      <div class="flex flex-wrap items-end justify-between gap-4"><div><h1 class="text-2xl font-semibold">Session records</h1><p class="mt-1 text-sm text-[#5B616B]">Chronological records of completed counselling sessions.</p></div><router-link :to="{ name: 'Appointments' }" class="inline-flex h-10 items-center gap-2 rounded-[10px] border border-[#D5D8DE] bg-white px-4 text-sm font-semibold hover:bg-[#F4F5F7]"><CalendarDays :size="17" /> Appointments</router-link></div>
      <ErrorMessage class="mt-4" :message="records.error" />
      <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
        <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-4"><div><h2 class="font-semibold">Completed sessions</h2><p class="mt-1 text-xs text-[#737780]">{{ data?.length || 0 }} records</p></div><LoaderCircle v-if="records.loading" :size="18" class="animate-spin text-[#737780]" /></div>
        <ul v-if="data?.length" class="divide-y divide-[#ECEDEF]">
          <li v-for="row in data" :key="row.name" class="grid gap-3 px-5 py-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
            <div class="min-w-0"><router-link :to="{ name: 'ClientProfile', params: { name: row.client_id } }" class="font-semibold hover:text-[#A10E24]">{{ row.client_name || row.client_id }}</router-link><p class="mt-1 text-xs text-[#737780]">{{ row.scholar_code }} · {{ fmtDateTime(row.date_time) }} · {{ row.session_type }} · {{ row.mode_of_contact }}</p><p class="mt-2 truncate text-sm text-[#5B616B]">{{ row.presenting_issues || row.session_details || 'Session summary recorded' }}</p></div>
            <div class="flex items-center gap-2 sm:justify-end"><Badge label="Recorded" theme="green" /><router-link :to="{ name: 'SessionRecord', params: { name: row.name } }" class="inline-flex h-10 items-center gap-2 rounded-lg border border-[#D5D8DE] px-3.5 text-sm font-semibold hover:bg-[#F4F5F7]"><Eye :size="16" /> View record</router-link></div>
          </li>
        </ul>
        <div v-else-if="!records.loading" class="px-5 py-14 text-center"><BookOpen :size="28" class="mx-auto text-[#B9BBC1]" /><h3 class="mt-3 font-semibold">No session records yet</h3><p class="mt-1 text-sm text-[#737780]">Completed session summaries will appear here.</p></div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted } from "vue"
import { BookOpen, CalendarDays, Eye, LoaderCircle } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"

const records = createResource({ url: "krcti_mhpss.api.counsellor.my_session_records" })
const data = computed(() => records.data)
onMounted(() => records.submit())
</script>
