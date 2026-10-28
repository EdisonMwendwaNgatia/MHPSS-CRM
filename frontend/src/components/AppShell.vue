<template>
  <div class="min-h-screen bg-[#F4F5F7]">
    <header class="sticky top-0 z-30 flex h-[68px] items-center justify-between border-b border-[#E4E6EA] bg-white px-4 md:hidden">
      <div class="flex items-center gap-3">
        <button type="button" class="rounded-lg p-2 text-[#555860] hover:bg-[#F4F5F7]" aria-label="Open menu" @click="open = true"><Menu :size="21" /></button>
        <span class="text-sm font-semibold text-[#25272B]">{{ pageTitle }}</span>
      </div>
      <span class="flex h-8 w-8 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
    </header>
    <div v-if="open" class="fixed inset-0 z-40 bg-black/40 md:hidden" @click="open = false"></div>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-[248px] flex-col border-r border-[#E4E6EA] bg-white transition-transform duration-200 md:translate-x-0"
      :class="open ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex items-center justify-between border-b border-[#ECEDEF] px-5 py-5">
        <div class="flex items-center gap-3">
          <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#C8102E] text-sm font-bold tracking-wide text-white">KR</span>
          <span>
            <span class="block text-sm font-semibold text-[#25272B]">KRCTI MHPSS</span>
            <span class="mt-0.5 block text-xs text-[#858891]">Case management</span>
          </span>
        </div>
        <button type="button" class="rounded-md p-1.5 text-[#737780] hover:bg-[#F4F5F7] md:hidden" aria-label="Close menu" @click="open = false">
          <X :size="20" />
        </button>
      </div>

      <div class="px-5 pb-2 pt-6 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#A0A2A8]">Workspace</div>
      <nav class="flex-1 space-y-1 px-3">
        <router-link
          v-for="item in items"
          :key="item.name"
          :to="{ name: item.name }"
          :class="linkClass(isActive(item))"
          @click="open = false"
        >
          <component :is="item.icon" :size="18" />
          {{ item.label }}
        </router-link>
        <a v-if="role === 'admin'" href="/desk" :class="linkClass(false)">
          <Settings :size="18" />
          Users and settings
        </a>
      </nav>

      <div class="border-t border-[#E4E6EA] p-4">
        <div class="flex items-center gap-3">
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
          <span class="min-w-0"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span><span class="mt-0.5 block truncate text-xs text-[#858891]">{{ roleLabel }}</span></span>
        </div>
        <button
          type="button"
          class="mt-3 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-[#62656D] hover:bg-[#F4F5F7]"
          @click="session.logout.submit()"
        >
          <LogOut :size="18" />
          Log out
        </button>
      </div>
    </aside>

    <div class="md:pl-[248px]">
      <header v-if="me.data" class="sticky top-0 z-30 hidden h-[72px] items-center border-b border-[#E4E6EA] bg-white px-7 lg:flex">
        <div class="flex w-[220px] shrink-0 items-center gap-2 text-sm"><span class="text-[#9A9CA2]">Workspace</span><ChevronRight :size="15" class="text-[#B9BBC1]" /><span class="font-medium text-[#33353A]">{{ pageTitle }}</span></div>
        <div v-if="canSearchClients" class="flex min-w-0 flex-1 justify-center px-8">
          <div class="relative w-full max-w-[460px]" data-client-search>
            <label for="topbar-client-search" class="sr-only">Search clients</label>
            <div class="flex h-10 items-center gap-2.5 rounded-xl border border-[#E4E6EA] bg-[#FAFAFB] px-3.5 transition focus-within:border-[#C8102E] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#C8102E]/10">
              <Search :size="17" class="shrink-0 text-[#858891]" />
              <input id="topbar-client-search" v-model="searchTerm" type="search" autocomplete="off" placeholder="Search by code, name or phone" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#92949A] focus:ring-0" @keydown.esc="searchOpen = false" @focus="searchOpen = true" />
              <LoaderCircle v-if="clientSearch.loading" :size="16" class="animate-spin text-[#858891]" />
              <kbd v-else class="rounded-md border border-[#E4E6EA] bg-white px-1.5 py-0.5 text-[10px] font-medium text-[#92949A]">⌕</kbd>
            </div>
            <div v-if="searchOpen && searchTerm.trim().length >= 2" class="absolute left-0 right-0 top-full z-40 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]">
              <div v-if="clientSearch.loading && !clientSearch.data?.length" class="px-4 py-3 text-sm text-[#737780]">Searching clients…</div>
              <div v-else-if="clientSearch.data?.length" class="max-h-[360px] overflow-y-auto py-1.5">
                <router-link v-for="row in clientSearch.data" :key="row.name" :to="{ name: 'ClientProfile', params: { name: row.name } }" class="flex items-center gap-3 px-3.5 py-2.5 transition hover:bg-[#F7F7F8]" @click="clearSearch">
                  <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ clientInitials(row.full_name) }}</span>
                  <span class="min-w-0 flex-1"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ row.full_name }}</span><span class="mt-0.5 block truncate text-xs text-[#858891]">{{ [row.scholar_code, row.phone_number, row.institution].filter(Boolean).join(' · ') }}</span></span>
                  <ChevronRight :size="16" class="shrink-0 text-[#B9BBC1]" />
                </router-link>
              </div>
              <p v-else class="px-4 py-4 text-sm text-[#737780]">No clients found for “{{ searchTerm.trim() }}”.</p>
            </div>
          </div>
        </div>
        <div v-else class="flex-1"></div>
        <div class="flex shrink-0 items-center gap-4">
          <div v-if="role === 'counsellor'" class="relative" data-notification-menu>
            <button type="button" class="relative flex h-10 w-10 items-center justify-center rounded-xl text-[#62656D] transition hover:bg-[#F4F5F7]" aria-label="Notifications" :aria-expanded="notificationsOpen" @click="toggleNotifications">
              <Bell :size="19" />
              <span v-if="notificationCount" class="absolute right-1 top-1 flex h-[17px] min-w-[17px] items-center justify-center rounded-full border-2 border-white bg-[#C8102E] px-1 text-[9px] font-bold leading-none text-white">{{ notificationCount > 9 ? '9+' : notificationCount }}</span>
            </button>
            <div v-if="notificationsOpen" class="absolute right-0 top-full z-40 mt-3 w-[min(360px,calc(100vw-2rem))] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]">
              <div class="flex items-center justify-between border-b border-[#ECEDEF] px-4 py-3.5"><div><h2 class="text-sm font-semibold text-[#25272B]">Notifications</h2><p class="mt-0.5 text-xs text-[#858891]">Follow-ups that need attention</p></div><span v-if="notificationCount" class="rounded-full bg-[#FCE8EB] px-2 py-1 text-[11px] font-semibold text-[#A10E24]">{{ notificationCount }} new</span></div>
              <div v-if="notificationData.loading && !notificationData.data" class="flex items-center gap-2.5 px-4 py-5 text-sm text-[#737780]"><LoaderCircle :size="16" class="animate-spin" /> Checking follow-ups…</div>
              <div v-else-if="notificationData.error" class="px-4 py-5 text-sm text-[#737780]">Couldn’t load follow-ups. Close and reopen notifications to try again.</div>
              <div v-else-if="overdueFollowups.length" class="max-h-[320px] overflow-y-auto divide-y divide-[#F0F1F3]">
                <router-link v-for="row in overdueFollowups" :key="row.name" :to="{ name: 'AppointmentEdit', params: { name: row.name } }" class="flex items-start gap-3 px-4 py-3.5 transition hover:bg-[#FCFCFD]" @click="notificationsOpen = false">
                  <span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#FDEBEC] text-[#B42332]"><BellRing :size="15" /></span>
                  <span class="min-w-0 flex-1"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ row.client_name || row.client_id }}</span><span class="mt-0.5 block text-xs text-[#737780]">Overdue follow-up · {{ row.date_time ? new Date(String(row.date_time).replace(' ', 'T')).toLocaleDateString() : '' }}</span></span>
                  <ChevronRight :size="15" class="mt-1 shrink-0 text-[#B9BBC1]" />
                </router-link>
                <p v-if="notificationCount > overdueFollowups.length" class="px-4 py-3 text-xs text-[#737780]">{{ notificationCount - overdueFollowups.length }} more overdue follow-up{{ notificationCount - overdueFollowups.length === 1 ? '' : 's' }}. <router-link :to="{ name: 'Appointments' }" class="font-semibold text-[#A10E24]" @click="notificationsOpen = false">View appointments</router-link></p>
              </div>
              <div v-else class="px-5 py-8 text-center"><span class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF5EE] text-[#26834B]"><Check :size="19" /></span><p class="mt-3 text-sm font-semibold text-[#33353A]">You’re all caught up</p><p class="mt-1 text-xs text-[#858891]">No overdue follow-ups to review.</p></div>
            </div>
          </div>
          <span class="h-7 w-px bg-[#E4E6EA]"></span>
          <div class="flex items-center gap-2.5">
            <span class="flex h-9 w-9 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
            <span><span class="block max-w-[190px] truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span><span class="mt-0.5 block text-xs text-[#858891]">{{ roleLabel }}</span></span>
          </div>
        </div>
      </header>
      <PageLoader v-if="!me.data" />
      <div v-else-if="!allowed" class="m-4 rounded-lg border border-gp-line bg-white p-5 md:m-8">
        <h1 class="font-semibold text-gp-ink">You do not have access to this page</h1>
        <router-link :to="{ name: 'Home' }" class="mt-3 inline-block font-medium text-gp">Go to my home page</router-link>
      </div>
      <slot v-else />
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { Bell, BellRing, CalendarDays, Check, ChevronRight, ClipboardList, LayoutDashboard, LoaderCircle, LogOut, Menu, Search, Settings, Users, X } from "lucide-vue-next"
import { me } from "../data/me"
import { session } from "../data/session"

const NAV = [
	{ label: "Dashboard", name: "Home", icon: LayoutDashboard, match: ["Home"], roles: ["counsellor"] },
	{ label: "Clients", name: "Clients", icon: Users, match: ["Clients", "ClientNew", "ClientProfile", "ClientEdit", "Baseline"], roles: ["counsellor", "admin"] },
	{ label: "Appointments", name: "Appointments", icon: CalendarDays, match: ["Appointments", "AppointmentNew", "AppointmentEdit"], roles: ["counsellor", "admin"] },
	{ label: "Programme", name: "Programme", icon: ClipboardList, match: ["Programme"], roles: ["krcti_pm", "woc_pm", "admin"] },
]
const LABELS = {
	admin: "System Administrator", counsellor: "Counsellor", krcti_pm: "KRCTI Programme Manager",
	woc_pm: "WoC Programme Manager", client: "Client",
}

const route = useRoute()
const open = ref(false)
onMounted(() => me.reload())
watch(() => route.fullPath, () => (open.value = false))

const searchTerm = ref("")
const searchOpen = ref(false)
const notificationsOpen = ref(false)
const clientSearch = createResource({ url: "krcti_mhpss.api.counsellor.search_clients" })
const notificationData = createResource({ url: "krcti_mhpss.api.counsellor.home" })
const overdueFollowups = computed(() => (notificationData.data?.followups || []).filter((row) => row.overdue))
const notificationCount = computed(() => notificationData.data?.overdue_followups || 0)
let searchTimer = null
watch(searchTerm, (value) => {
	clearTimeout(searchTimer)
	if (value.trim().length < 2) {
		clientSearch.data = []
		return
	}
	searchOpen.value = true
	searchTimer = setTimeout(() => clientSearch.submit({ term: value.trim(), limit: 8 }), 250)
})
watch(() => me.data?.role, (value) => {
	if (value === "counsellor") notificationData.submit()
}, { immediate: true })
function clientInitials(name) {
	return (name || "Client").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase()
}
function clearSearch() {
	searchTerm.value = ""
	searchOpen.value = false
}
function toggleNotifications() {
	notificationsOpen.value = !notificationsOpen.value
	if (notificationsOpen.value) notificationData.submit()
}
function closeHeaderMenus(event) {
	if (!event.target.closest("[data-client-search]")) searchOpen.value = false
	if (!event.target.closest("[data-notification-menu]")) notificationsOpen.value = false
}
onMounted(() => document.addEventListener("click", closeHeaderMenus))
onUnmounted(() => {
	clearTimeout(searchTimer)
	document.removeEventListener("click", closeHeaderMenus)
})

const role = computed(() => me.data?.role)
const canSearchClients = computed(() => ["counsellor", "admin"].includes(role.value))
const roleLabel = computed(() => LABELS[role.value] || "")
const pageTitle = computed(() => NAV.find((item) => item.match.includes(route.name))?.label || "Dashboard")
const initials = computed(() => (me.data?.full_name || "KR").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase())
const items = computed(() => NAV.filter((item) => item.roles.includes(role.value)))
const allowed = computed(() => !route.meta.roles || route.meta.roles.includes(role.value))
const isActive = (item) => item.match.includes(route.name)
const linkClass = (active) => [
	"flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
	active ? "bg-[#FCE8EB] text-[#B30F2A]" : "text-[#62656D] hover:bg-[#F7F7F8] hover:text-[#33353A]",
]
</script>
