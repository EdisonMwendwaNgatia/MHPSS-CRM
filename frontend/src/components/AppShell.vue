<template>
  <div class="min-h-screen bg-[#F4F5F7]">
    <header class="sticky top-0 z-30 flex h-[68px] items-center justify-between border-b border-[#E4E6EA] bg-white px-4 md:hidden">
      <div class="flex items-center gap-3">
        <button type="button" class="rounded-lg p-2 text-[#555860] hover:bg-[#F4F5F7]" aria-label="Open menu" @click="open = true"><Menu :size="21" /></button>
        <span class="text-sm font-semibold text-[#25272B]">{{ pageTitle }}</span>
      </div>
      <div v-if="isProgrammeManager" class="relative" data-programme-notification-menu>
        <button type="button" class="relative flex h-10 w-10 items-center justify-center rounded-xl text-[#62656D] hover:bg-[#F4F5F7]" aria-label="Programme notifications" :aria-expanded="programmeNotificationsOpen" @click="toggleProgrammeNotifications">
          <Bell :size="19" />
          <span v-if="programmeNotificationCount" class="absolute right-1 top-1 flex h-[17px] min-w-[17px] items-center justify-center rounded-full border-2 border-white bg-[#C8102E] px-1 text-[9px] font-bold leading-none text-white">{{ programmeNotificationCount > 9 ? '9+' : programmeNotificationCount }}</span>
        </button>
        <div v-if="programmeNotificationsOpen" class="absolute right-0 top-full z-50 mt-2 w-[min(360px,calc(100vw-2rem))] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white text-left shadow-[0_14px_36px_rgba(31,35,45,0.16)]">
          <div class="flex items-center justify-between border-b border-[#ECEDEF] px-4 py-3.5"><div><h2 class="text-sm font-semibold text-[#25272B]">Programme notifications</h2><p class="mt-0.5 text-xs text-[#858891]">Appointments and completed sessions</p></div><button v-if="programmeNotificationCount" type="button" class="text-[11px] font-semibold text-[#A10E24] hover:underline" @click="markAllProgrammeNotificationsRead">Mark all read</button></div>
          <div v-if="programmeNotificationData.loading && !programmeNotificationData.data" class="px-4 py-5 text-sm text-[#737780]">Checking programme activity…</div>
          <div v-else-if="programmeNotificationData.error" class="px-4 py-5 text-sm text-[#737780]">Couldn’t load programme notifications.</div>
          <div v-else-if="programmeNotifications.length" class="max-h-[360px] divide-y divide-[#F0F1F3] overflow-y-auto">
            <div v-for="item in programmeNotifications" :key="item.name" class="flex items-start gap-3 px-4 py-3.5"><span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#E0EAFD] text-[#1B4DB1]"><BellRing :size="15" /></span><div class="min-w-0 flex-1"><p class="text-sm font-semibold text-[#33353A]">{{ item.title }}</p><p class="mt-0.5 text-xs text-[#737780]">{{ item.description }}</p><p class="mt-1 text-[11px] text-[#858891]">{{ formatNotificationDate(item.creation) }}</p><button type="button" class="mt-1 text-xs font-semibold text-[#A10E24] hover:underline" @click="markProgrammeNotificationRead(item.name)">Mark as read</button></div></div>
          </div>
          <div v-else class="px-5 py-8 text-center"><span class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF5EE] text-[#26834B]"><Check :size="19" /></span><p class="mt-3 text-sm font-semibold text-[#33353A]">You’re all caught up</p></div>
        </div>
      </div>
      <div class="relative" data-account-menu>
        <button type="button" class="rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30" aria-label="Account options" :aria-expanded="accountOpen" aria-haspopup="menu" @click="accountOpen = !accountOpen">
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
        </button>
        <div v-if="accountOpen" class="absolute right-0 top-full z-50 mt-2 w-[260px] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white text-left shadow-[0_14px_36px_rgba(31,35,45,0.16)]" role="menu" aria-label="Account options">
          <div class="flex items-center gap-3 border-b border-[#ECEDEF] px-4 py-4">
            <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
            <span class="min-w-0"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span><span class="mt-0.5 block truncate text-xs text-[#858891]">{{ roleLabel }}</span></span>
          </div>
          <div class="p-1.5"><button type="button" role="menuitem" class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-[#A10E24] hover:bg-[#FCE8EB]" @click="logout"><LogOut :size="17" /> Log out</button></div>
        </div>
      </div>
    </header>
    <div v-if="open" class="fixed inset-0 z-40 bg-black/40 md:hidden" @click="open = false"></div>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-[#E4E6EA] bg-white transition-[width,transform] duration-200 md:translate-x-0"
      :class="[open ? 'translate-x-0' : '-translate-x-full', collapsed ? 'w-[248px] md:w-[84px]' : 'w-[248px]']"
      @click="handleSidebarBackgroundClick"
    >
      <!-- Brand: height matches the top bar so the two border lines meet -->
      <div class="flex h-[68px] shrink-0 items-center justify-between border-b border-[#E4E6EA] px-4 md:h-[72px]" :class="collapsed ? 'md:justify-center md:px-2' : ''">
        <div class="flex min-w-0 items-center gap-3" :class="collapsed ? 'md:gap-1' : ''">
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-[#C8102E] text-sm font-semibold tracking-wide text-white" :class="collapsed ? 'md:h-8 md:w-8 md:rounded-lg md:text-xs' : ''">KR</span>
          <span v-if="!collapsed || open" class="min-w-0 leading-[18px]">
            <span class="block truncate text-[15px] font-semibold text-[#2B2F36]">KRCTI MHPSS</span>
            <span class="block truncate text-[13px] text-[#5B616B]">Case management</span>
          </span>
        </div>
        <button type="button" class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px] text-[#5B616B] hover:bg-[#F4F5F7] md:hidden" aria-label="Close menu" @click="open = false">
          <X :size="20" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 space-y-1 overflow-y-auto px-3 pt-4" aria-label="Main navigation">
        <p v-if="!collapsed || open" class="px-3 pb-1.5 text-xs font-medium text-[#5B616B]">Workspace</p>
        <div v-else class="mx-3 mb-3 hidden h-px bg-[#E4E6EA] md:block" aria-hidden="true"></div>
        <router-link
          v-for="item in items"
          :key="item.name"
          :to="{ name: item.name }"
          :title="collapsed ? navLabel(item) : undefined"
          :aria-label="collapsed ? navLabel(item) : undefined"
          :aria-current="isActive(item) ? 'page' : undefined"
          :class="linkClass(isActive(item))"
          @click="open = false"
        >
          <component :is="item.icon" :size="20" class="shrink-0" />
          <span v-if="!collapsed || open" class="truncate">{{ navLabel(item) }}</span>
        </router-link>
      </nav>

      <div class="hidden shrink-0 border-t border-[#E4E6EA] p-3 md:block">
        <button type="button" class="flex h-11 w-full items-center gap-3 rounded-[10px] px-3 text-sm font-medium text-[#4A505A] transition-colors hover:bg-[#F4F5F7] hover:text-[#2B2F36] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40" :class="collapsed ? 'md:justify-center md:px-0' : ''" :title="collapsed ? 'Expand sidebar' : undefined" :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'" :aria-expanded="!collapsed" @click="toggleSidebar">
          <PanelLeftOpen v-if="collapsed" :size="20" class="shrink-0" />
          <PanelLeftClose v-else :size="20" class="shrink-0" />
          <span v-if="!collapsed">Collapse sidebar</span>
        </button>
      </div>

    </aside>

    <div class="transition-[padding] duration-200" :class="collapsed ? 'md:pl-[84px]' : 'md:pl-[248px]'">
      <header v-if="me.data" class="sticky top-0 z-30 hidden h-[72px] items-center border-b border-[#E4E6EA] bg-white px-5 lg:px-7 md:flex">
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
              <div class="flex items-center justify-between border-b border-[#ECEDEF] px-4 py-3.5"><div><h2 class="text-sm font-semibold text-[#25272B]">Notifications</h2><p class="mt-0.5 text-xs text-[#858891]">Follow-ups and referral updates</p></div><div class="flex items-center gap-2"><span v-if="notificationCount" class="rounded-full bg-[#FCE8EB] px-2 py-1 text-[11px] font-semibold text-[#A10E24]">{{ notificationCount }} new</span><button v-if="notificationCount" type="button" class="text-[11px] font-semibold text-[#A10E24] hover:underline" @click="markAllNotificationsRead">Mark all read</button></div></div>
              <div v-if="notificationData.loading && !notificationData.data" class="flex items-center gap-2.5 px-4 py-5 text-sm text-[#737780]"><LoaderCircle :size="16" class="animate-spin" /> Checking follow-ups…</div>
              <div v-else-if="notificationData.error" class="px-4 py-5 text-sm text-[#737780]">Couldn’t load follow-ups. Close and reopen notifications to try again.</div>
              <div v-else-if="overdueFollowups.length || referralEvents.length" class="max-h-[360px] overflow-y-auto divide-y divide-[#F0F1F3]">
                <router-link v-for="row in overdueFollowups" :key="`overdue-${row.name}`" :to="{ name: 'SessionRecord', params: { name: row.name } }" class="flex items-start gap-3 px-4 py-3.5 transition hover:bg-[#FCFCFD]" @click="markOverdueNotificationsRead.submit({ name: row.name }); notificationsOpen = false">
                  <span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#FDEBEC] text-[#B42332]"><BellRing :size="15" /></span>
                  <span class="min-w-0 flex-1"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ row.client_name || row.client_id }}</span><span class="mt-0.5 block text-xs text-[#737780]">Overdue follow-up · {{ row.date_time ? new Date(String(row.date_time).replace(' ', 'T')).toLocaleDateString() : '' }}</span></span>
                  <ChevronRight :size="15" class="mt-1 shrink-0 text-[#B9BBC1]" />
                </router-link>
                <router-link v-for="row in referralEvents" :key="row.id" :to="{ name: 'SessionRecord', params: { name: row.appointment } }" class="flex items-start gap-3 px-4 py-3.5 transition hover:bg-[#FCFCFD]" @click="markReferralNotificationsRead.submit({ name: row.id }); notificationsOpen = false">
                  <span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full" :class="row.direction === 'received' ? 'bg-[#EAF1FC] text-[#3767A6]' : 'bg-[#EAF5EE] text-[#26834B]'"><Users :size="15" /></span>
                  <span class="min-w-0 flex-1"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ row.client_name || row.client_id }}</span><span class="mt-0.5 block text-xs text-[#737780]">{{ row.direction === 'received' ? `Referred to you by ${row.from_name}` : `You referred this appointment to ${row.to_name}` }}</span><span class="mt-1 block truncate text-xs text-[#858891]">{{ row.reason }}</span></span>
                  <ChevronRight :size="15" class="mt-1 shrink-0 text-[#B9BBC1]" />
                </router-link>
              </div>
              <div v-else class="px-5 py-8 text-center"><span class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF5EE] text-[#26834B]"><Check :size="19" /></span><p class="mt-3 text-sm font-semibold text-[#33353A]">You’re all caught up</p><p class="mt-1 text-xs text-[#858891]">No overdue follow-ups or referral updates.</p></div>
            </div>
          </div>
          <div v-if="isProgrammeManager" class="relative" data-programme-notification-menu>
            <button type="button" class="relative flex h-10 w-10 items-center justify-center rounded-xl text-[#62656D] transition hover:bg-[#F4F5F7]" aria-label="Programme notifications" :aria-expanded="programmeNotificationsOpen" @click="toggleProgrammeNotifications">
              <Bell :size="19" />
              <span v-if="programmeNotificationCount" class="absolute right-1 top-1 flex h-[17px] min-w-[17px] items-center justify-center rounded-full border-2 border-white bg-[#C8102E] px-1 text-[9px] font-bold leading-none text-white">{{ programmeNotificationCount > 9 ? '9+' : programmeNotificationCount }}</span>
            </button>
            <div v-if="programmeNotificationsOpen" class="absolute right-0 top-full z-40 mt-3 w-[min(380px,calc(100vw-2rem))] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]">
              <div class="flex items-center justify-between border-b border-[#ECEDEF] px-4 py-3.5"><div><h2 class="text-sm font-semibold text-[#25272B]">Programme notifications</h2><p class="mt-0.5 text-xs text-[#858891]">Appointments and completed sessions</p></div><button v-if="programmeNotificationCount" type="button" class="text-[11px] font-semibold text-[#A10E24] hover:underline" @click="markAllProgrammeNotificationsRead">Mark all read</button></div>
              <div v-if="programmeNotificationData.loading && !programmeNotificationData.data" class="px-4 py-5 text-sm text-[#737780]">Checking programme activity…</div>
              <div v-else-if="programmeNotificationData.error" class="px-4 py-5 text-sm text-[#737780]">Couldn’t load programme notifications.</div>
              <div v-else-if="programmeNotifications.length" class="max-h-[360px] divide-y divide-[#F0F1F3] overflow-y-auto">
                <div v-for="item in programmeNotifications" :key="item.name" class="flex items-start gap-3 px-4 py-3.5"><span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#E0EAFD] text-[#1B4DB1]"><BellRing :size="15" /></span><div class="min-w-0 flex-1"><p class="text-sm font-semibold text-[#33353A]">{{ item.title }}</p><p class="mt-0.5 text-xs text-[#737780]">{{ item.description }}</p><p class="mt-1 text-[11px] text-[#858891]">{{ formatNotificationDate(item.creation) }}</p><button type="button" class="mt-1 text-xs font-semibold text-[#A10E24] hover:underline" @click="markProgrammeNotificationRead(item.name)">Mark as read</button></div></div>
              </div>
              <div v-else class="px-5 py-8 text-center"><span class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF5EE] text-[#26834B]"><Check :size="19" /></span><p class="mt-3 text-sm font-semibold text-[#33353A]">You’re all caught up</p></div>
            </div>
          </div>
          <span class="h-7 w-px bg-[#E4E6EA]"></span>
          <div class="relative" data-account-menu>
            <button type="button" class="flex items-center gap-2.5 rounded-xl px-2 py-1.5 text-left transition hover:bg-[#F7F7F8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30" :aria-expanded="accountOpen" aria-haspopup="menu" @click="accountOpen = !accountOpen">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
              <span class="hidden xl:block"><span class="block max-w-[170px] truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span><span class="mt-0.5 block text-xs text-[#858891]">{{ roleLabel }}</span></span>
              <ChevronDown :size="16" class="text-[#737780] transition-transform" :class="accountOpen ? 'rotate-180' : ''" />
            </button>
            <div v-if="accountOpen" class="absolute right-0 top-full z-40 mt-2 w-[260px] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]" role="menu" aria-label="Account options">
              <div class="flex items-center gap-3 border-b border-[#ECEDEF] px-4 py-4">
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
                <span class="min-w-0"><span class="block truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span><span class="mt-0.5 block truncate text-xs text-[#858891]">{{ roleLabel }}</span></span>
              </div>
              <div class="p-1.5">
                <button type="button" role="menuitem" class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-[#A10E24] transition hover:bg-[#FCE8EB] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30" @click="logout">
                  <LogOut :size="17" /> Log out
                </button>
              </div>
            </div>
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
import { Bell, BellRing, BookOpen, CalendarDays, Check, ChevronDown, ChevronRight, ClipboardCheck, ClipboardList, HeartHandshake, LayoutDashboard, LoaderCircle, LogOut, Menu, PanelLeftClose, PanelLeftOpen, Search, UserRoundPlus, Users, UsersRound, X } from "lucide-vue-next"
import { me } from "../data/me"
import { session } from "../data/session"

const NAV = [
	{ label: "Dashboard", name: "Home", icon: LayoutDashboard, match: ["Home"], roles: ["counsellor"] },
	{ label: "Clients", name: "Clients", icon: UsersRound, match: ["Clients", "ClientNew", "ClientProfile", "ClientEdit", "Baseline"], roles: ["counsellor"] },
	{ label: "Appointments", name: "Appointments", icon: CalendarDays, match: ["Appointments", "AppointmentNew", "AppointmentEdit"], roles: ["counsellor"] },
	{ label: "Follow-ups", name: "FollowUps", icon: HeartHandshake, match: ["FollowUps"], roles: ["counsellor"] },
	{ label: "Session records", name: "SessionRecords", icon: BookOpen, match: ["SessionRecords", "SessionRecord"], roles: ["counsellor"] },
	{ label: "Programme", name: "Programme", icon: ClipboardList, match: ["Programme"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Register client", name: "ProgrammeClientNew", icon: UserRoundPlus, match: ["ProgrammeClientNew"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Programme clients", name: "ProgrammeClients", icon: UsersRound, match: ["ProgrammeClients", "ProgrammeClientDetail"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Counsellors", name: "ProgrammeCounsellors", icon: Users, match: ["ProgrammeCounsellors"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Session management", name: "ProgrammeSessions", icon: CalendarDays, match: ["ProgrammeSessions"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Counsellor activity", name: "ProgrammeActivity", icon: ClipboardCheck, match: ["ProgrammeActivity"], roles: ["krcti_pm", "woc_pm"] },
	{ label: "Audit logs", name: "AuditLogs", icon: ClipboardCheck, match: ["AuditLogs"], roles: ["dpo"] },
]
const LABELS = {
	admin: "System Administrator", counsellor: "Counsellor", krcti_pm: "KRCTI Programme Manager",
	woc_pm: "WoC Programme Manager", client: "Client", dpo: "KRCS Data Protection Officer",
}

const route = useRoute()
const open = ref(false)
const collapsed = ref(typeof localStorage !== "undefined" && localStorage.getItem("krcti-sidebar-collapsed") === "true")
function toggleSidebar() {
	collapsed.value = !collapsed.value
	if (typeof localStorage !== "undefined") localStorage.setItem("krcti-sidebar-collapsed", String(collapsed.value))
}
function handleSidebarBackgroundClick(event) {
	if (window.innerWidth < 768 || event.target.closest("a, button, input, p, span, svg")) return
	toggleSidebar()
}
onMounted(() => me.reload())
watch(() => route.fullPath, () => (open.value = false))

const searchTerm = ref("")
const searchOpen = ref(false)
const notificationsOpen = ref(false)
const programmeNotificationsOpen = ref(false)
const accountOpen = ref(false)
const clientSearch = createResource({ url: "krcti_mhpss.api.counsellor.search_clients" })
const notificationData = createResource({ url: "krcti_mhpss.api.counsellor.home" })
const referralNotificationData = createResource({ url: "krcti_mhpss.api.records.referral_notifications" })
const programmeNotificationData = createResource({ url: "krcti_mhpss.api.oversight.programme_notifications" })
const markProgrammeNotificationsRead = createResource({
	url: "krcti_mhpss.api.oversight.mark_programme_notifications_read",
	onSuccess() { programmeNotificationData.submit() },
})
const markReferralNotificationsRead = createResource({
	url: "krcti_mhpss.api.records.mark_referral_notifications_read",
	onSuccess() { referralNotificationData.submit() },
})
const markOverdueNotificationsRead = createResource({
	url: "krcti_mhpss.api.counsellor.mark_overdue_followup_notifications_read",
	onSuccess() { notificationData.submit() },
})
const overdueFollowups = computed(() => notificationData.data?.overdue_notifications || [])
const referralEvents = computed(() => referralNotificationData.data?.notifications || [])
const programmeNotifications = computed(() => programmeNotificationData.data?.notifications || [])
const programmeNotificationCount = computed(() => programmeNotificationData.data?.unread_count || 0)
const notificationCount = computed(() => (notificationData.data?.overdue_followups || 0) + (referralNotificationData.data?.unread_count || 0))
let searchTimer = null
let notificationTimer = null
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
	if (value === "counsellor") {
		notificationData.submit()
		referralNotificationData.submit()
	} else if (["krcti_pm", "woc_pm"].includes(value)) {
		programmeNotificationData.submit()
	}
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
	if (notificationsOpen.value) {
		notificationData.submit()
		referralNotificationData.submit()
	}
}
function toggleProgrammeNotifications() {
	programmeNotificationsOpen.value = !programmeNotificationsOpen.value
	if (programmeNotificationsOpen.value) programmeNotificationData.submit()
}
function markProgrammeNotificationRead(name) {
	markProgrammeNotificationsRead.submit({ name })
}
function markAllProgrammeNotificationsRead() {
	markProgrammeNotificationsRead.submit()
}
function formatNotificationDate(value) {
	return value ? new Date(String(value).replace(" ", "T")).toLocaleString() : ""
}
function markAllNotificationsRead() {
	markReferralNotificationsRead.submit()
	markOverdueNotificationsRead.submit()
}
function logout() {
	accountOpen.value = false
	session.logout.submit()
}
function closeHeaderMenus(event) {
	if (!event.target.closest("[data-client-search]")) searchOpen.value = false
	if (!event.target.closest("[data-notification-menu]")) notificationsOpen.value = false
	if (!event.target.closest("[data-programme-notification-menu]")) programmeNotificationsOpen.value = false
	if (!event.target.closest("[data-account-menu]")) accountOpen.value = false
}
onMounted(() => document.addEventListener("click", closeHeaderMenus))
notificationTimer = setInterval(() => {
	if (role.value === "counsellor" && !notificationsOpen.value) {
		notificationData.submit()
		referralNotificationData.submit()
	} else if (isProgrammeManager.value && !programmeNotificationsOpen.value) {
		programmeNotificationData.submit()
	}
}, 60000)
onUnmounted(() => {
	clearTimeout(searchTimer)
	clearInterval(notificationTimer)
	document.removeEventListener("click", closeHeaderMenus)
})

const role = computed(() => me.data?.role)
const isProgrammeManager = computed(() => ["krcti_pm", "woc_pm"].includes(role.value))
const canSearchClients = computed(() => role.value === "counsellor")
const roleLabel = computed(() => LABELS[role.value] || "")
const pageTitle = computed(() => {
	const item = NAV.find((entry) => entry.match.includes(route.name))
	return item ? navLabel(item) : "Dashboard"
})
const initials = computed(() => (me.data?.full_name || "KR").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase())
function navLabel(item) {
	if (item.name !== "Programme") return item.label
	if (role.value === "krcti_pm") return "KRCTI PM Dashboard"
	if (role.value === "woc_pm") return "WoC PM Dashboard"
	return "Programme Dashboard"
}
const items = computed(() => NAV.filter((item) => item.roles.includes(role.value)))
const allowed = computed(() => !route.meta.roles || route.meta.roles.includes(role.value))
const isActive = (item) => item.match.includes(route.name)
const linkClass = (active) => [
	"flex h-11 items-center gap-3 rounded-[10px] px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40",
	collapsed.value ? "md:justify-center md:px-0" : "",
	active ? "bg-[#FCE8EB] font-semibold text-[#A10E24]" : "text-[#4A505A] hover:bg-[#F4F5F7] hover:text-[#2B2F36]",
]
</script>
