<template>
  <div class="min-h-screen bg-gp-bg">
    <header class="sticky top-0 z-30 flex items-center gap-3 border-b border-gp-line bg-white px-4 py-2.5 md:hidden">
      <button type="button" class="rounded-md p-1.5 hover:bg-gp-bg" aria-label="Open menu" @click="open = true">
        <Menu :size="22" />
      </button>
      <span class="font-semibold text-gp">KRCTI MHPSS</span>
    </header>
    <div v-if="open" class="fixed inset-0 z-40 bg-black/40 md:hidden" @click="open = false"></div>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-gp-line bg-white md:translate-x-0"
      :class="open ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex items-center justify-between px-5 py-5">
        <div>
          <p class="text-lg font-semibold text-gp">KRCTI MHPSS</p>
          <p class="text-xs text-gp-muted">Case management</p>
        </div>
        <button type="button" class="rounded-md p-1.5 hover:bg-gp-bg md:hidden" aria-label="Close menu" @click="open = false">
          <X :size="20" />
        </button>
      </div>

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

      <div class="border-t border-gp-line p-4">
        <p class="truncate text-sm font-medium text-gp-ink">{{ me.data?.full_name }}</p>
        <p class="text-xs text-gp-muted">{{ roleLabel }}</p>
        <button
          type="button"
          class="mt-3 flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-gp-ink hover:bg-gp-bg"
          @click="session.logout.submit()"
        >
          <LogOut :size="18" />
          Log out
        </button>
      </div>
    </aside>

    <div class="md:pl-64">
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
import { CalendarDays, LayoutDashboard, LogOut, Menu, Settings, Users, X } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { me } from "../data/me"
import { session } from "../data/session"

const NAV = [
	{ label: "My day", name: "Home", icon: LayoutDashboard, match: ["Home"], roles: ["counsellor"] },
	{ label: "Clients", name: "Clients", icon: Users, match: ["Clients", "ClientNew", "ClientProfile", "ClientEdit", "Baseline"], roles: ["counsellor", "admin"] },
	{ label: "Appointments", name: "Appointments", icon: CalendarDays, match: ["Appointments", "AppointmentNew", "AppointmentEdit"], roles: ["counsellor", "admin"] },
	{ label: "Programme overview", name: "Programme", icon: LayoutDashboard, match: ["Programme"], roles: ["krcti_pm", "woc_pm", "admin"] },
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
const items = computed(() => NAV.filter((item) => item.roles.includes(role.value)))
const allowed = computed(() => !route.meta.roles || route.meta.roles.includes(role.value))
const isActive = (item) => item.match.includes(route.name)
const linkClass = (active) => [
	"flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium",
	active ? "bg-gp-bg text-gp" : "text-gp-ink hover:bg-gp-bg",
]
</script>