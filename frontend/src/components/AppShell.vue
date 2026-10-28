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
      <header v-if="me.data" class="sticky top-0 z-20 hidden h-[68px] items-center justify-between border-b border-[#E4E6EA] bg-white px-7 lg:flex">
        <div class="flex items-center gap-2 text-sm"><span class="text-[#9A9CA2]">Workspace</span><ChevronRight :size="15" class="text-[#B9BBC1]" /><span class="font-medium text-[#33353A]">{{ pageTitle }}</span></div>
        <div class="flex items-center gap-5">
          <router-link :to="{ name: 'Clients' }" class="flex w-[290px] items-center gap-2.5 rounded-lg border border-[#E4E6EA] bg-[#FAFAFB] px-3.5 py-2 text-sm text-[#858891] transition hover:border-[#D0D2D7]">
            <Search :size="16" /><span>Search clients</span><span class="ml-auto rounded border border-[#E4E6EA] bg-white px-1.5 py-0.5 text-[10px] text-[#A0A2A8]">⌕</span>
          </router-link>
          <span class="h-6 w-px bg-[#E4E6EA]"></span>
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
import { CalendarDays, ChevronRight, ClipboardList, LayoutDashboard, LogOut, Menu, Search, Settings, Users, X } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
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

const role = computed(() => me.data?.role)
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
