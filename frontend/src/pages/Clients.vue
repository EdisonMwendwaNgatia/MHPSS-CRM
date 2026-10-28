<template>
  <main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
    <div class="mx-auto max-w-[1440px]">
      <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p class="text-sm font-medium text-[#737780]">Client records</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Clients</h1>
          <p class="mt-1 text-sm text-[#737780]">Find and manage the people in your caseload.</p>
        </div>
        <router-link :to="{ name: 'ClientNew' }" class="inline-flex items-center justify-center gap-2 self-start rounded-lg bg-[#C8102E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#A10E24] sm:self-auto">
          <UserRoundPlus :size="17" /> Register client
        </router-link>
      </div>

      <section class="mt-6 rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
        <div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_230px] md:items-end">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-[#555860]">Search clients</span>
            <span class="flex h-11 items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10">
              <Search :size="17" class="shrink-0 text-[#858891]" />
              <input v-model="term" type="search" placeholder="Code, name, phone or institution" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
              <button v-if="term" type="button" class="shrink-0 text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="term = ''">Clear</button>
            </span>
          </label>
          <div class="block">
            <span class="mb-1.5 block text-xs font-semibold text-[#555860]">Case status</span>
            <div class="relative">
              <button type="button" :disabled="searching" class="flex h-11 w-full items-center justify-between rounded-lg border border-[#D9DBE0] bg-white px-3.5 text-left text-sm font-medium text-[#33353A] shadow-[0_1px_2px_rgba(20,25,35,0.03)] outline-none transition hover:border-[#BFC2C8] focus:border-[#C8102E] focus:ring-2 focus:ring-[#C8102E]/10 disabled:cursor-not-allowed disabled:border-[#E4E6EA] disabled:bg-[#F7F7F8] disabled:text-[#A0A2A8]" :aria-expanded="statusMenuOpen" aria-haspopup="listbox" @click="statusMenuOpen = !statusMenuOpen" @keydown.esc="statusMenuOpen = false">
                <span>{{ selectedStatus.label }}</span>
                <ChevronDown :size="16" class="shrink-0 text-[#737780] transition-transform" :class="statusMenuOpen ? 'rotate-180' : ''" />
              </button>
              <div v-if="statusMenuOpen && !searching" class="absolute left-0 right-0 z-20 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-label="Filter clients by case status">
                <button v-for="option in statusOptions" :key="option.value" type="button" role="option" :aria-selected="status === option.value" class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition" :class="status === option.value ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click="chooseStatus(option.value)">
                  {{ option.label }}
                  <Check v-if="status === option.value" :size="16" class="text-[#C8102E]" />
                </button>
              </div>
            </div>
          </div>
        </div>
        <p v-if="searching" class="mt-3 text-xs text-[#858891]">Search by participant code, name, phone number or institution.</p>
      </section>

      <ErrorMessage class="mt-4" :message="list.error || search.error" />

      <section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#ECEDEF] px-5 py-4">
          <div>
            <h2 class="text-base font-semibold text-[#25272B]">{{ searching ? 'Search results' : status || 'All clients' }}</h2>
            <p class="mt-0.5 text-xs text-[#858891]">{{ resultDescription }}</p>
          </div>
          <span v-if="searching && rows.length" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ rows.length }} found</span>
          <span v-else-if="!searching" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ total }} total</span>
        </div>

        <div v-if="(list.loading || search.loading) && !rows.length" class="px-5 py-10"><PageLoader /></div>
        <div v-else-if="!rows.length" class="px-5 py-14 text-center">
          <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><UsersRound :size="22" /></span>
          <p class="mt-3 text-sm font-semibold text-[#33353A]">{{ searching ? 'No matching clients' : 'No clients in this list yet' }}</p>
          <p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ searching ? 'Try another name, participant code, phone number or institution.' : 'Register a client to start building your caseload.' }}</p>
          <router-link v-if="!searching" :to="{ name: 'ClientNew' }" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2 text-sm font-semibold text-white hover:bg-[#A10E24]"><UserRoundPlus :size="16" /> Register client</router-link>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[680px] text-left">
            <thead><tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><th class="px-5 py-3">Client</th><th class="px-4 py-3">Participant code</th><th class="px-4 py-3">Institution</th><th class="px-4 py-3">Phone</th><th class="px-5 py-3 text-right">Case status</th></tr></thead>
            <tbody class="divide-y divide-[#F0F1F3]">
              <tr v-for="row in rows" :key="row.name" class="transition hover:bg-[#FCFCFD]">
                <td class="px-5 py-3.5">
                  <router-link :to="{ name: 'ClientProfile', params: { name: row.name } }" class="group flex items-center gap-3">
                    <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials(row.full_name) }}</span>
                    <span class="min-w-0"><span class="block truncate text-sm font-semibold text-[#33353A] group-hover:text-[#B30F2A]">{{ row.full_name }}</span><span class="mt-0.5 block truncate text-xs text-[#858891]">{{ row.name }}</span></span>
                  </router-link>
                </td>
                <td class="px-4 py-3.5 text-sm font-medium text-[#555860]">{{ row.scholar_code || '—' }}</td>
                <td class="max-w-[240px] px-4 py-3.5 text-sm text-[#555860]"><span class="block truncate">{{ row.institution || '—' }}</span></td>
                <td class="px-4 py-3.5 text-sm text-[#555860]">{{ row.phone_number || '—' }}</td>
                <td class="px-5 py-3.5 text-right"><Badge :label="row.case_status" :theme="caseTheme(row.case_status)" /></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!searching && total > rows.length" class="flex flex-wrap items-center justify-between gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
          <p class="text-xs text-[#737780]">Showing {{ rows.length }} of {{ total }} clients</p>
          <p class="text-xs text-[#858891]">Use search to find a specific client.</p>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, onUnmounted, ref, watch } from "vue"
import { Check, ChevronDown, Search, UserRoundPlus, UsersRound } from "lucide-vue-next"
import { caseTheme } from "../data/format"

const term = ref("")
const status = ref("")
const statusMenuOpen = ref(false)
const statusOptions = [
	{ label: "All case statuses", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Follow-Up Pending", value: "Follow-Up Pending" },
	{ label: "Closed", value: "Closed" },
]

const list = createResource({ url: "krcti_mhpss.api.counsellor.list_clients" })
const search = createResource({ url: "krcti_mhpss.api.counsellor.search_clients" })

const searching = computed(() => term.value.trim().length >= 2)
const rows = computed(() => (searching.value ? search.data || [] : list.data?.data || []))
const total = computed(() => list.data?.total || 0)
const selectedStatus = computed(() => statusOptions.find((option) => option.value === status.value) || statusOptions[0])
const resultDescription = computed(() => searching.value ? `Matching “${term.value.trim()}”` : `Showing clients${status.value ? ` with ${status.value.toLowerCase()} cases` : " across all case statuses"}`)

const initials = (fullName) => (fullName || "Client").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase()
const chooseStatus = (value) => {
	status.value = value
	statusMenuOpen.value = false
}

function onOutsideClick(event) {
	if (!event.target.closest('[aria-haspopup="listbox"]') && !event.target.closest('[role="listbox"]')) statusMenuOpen.value = false
}

let timer = null
watch([term, status], () => {
	clearTimeout(timer)
	timer = setTimeout(() => {
		if (searching.value) search.submit({ term: term.value.trim() })
		else list.submit({ status: status.value || undefined, page_length: 50 })
	}, 300)
})
onBeforeUnmount(() => clearTimeout(timer))
onMounted(() => list.submit({ page_length: 50 }))
onMounted(() => document.addEventListener("click", onOutsideClick))
onUnmounted(() => document.removeEventListener("click", onOutsideClick))
</script>
