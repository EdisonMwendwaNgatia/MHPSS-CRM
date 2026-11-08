<template>
	<div class="min-h-screen bg-[#F4F5F7]">
		<!-- Mobile overlay -->
		<Transition name="shell-fade">
			<div v-if="open" class="fixed inset-0 z-40 bg-[#1F232D]/45 backdrop-blur-[2px] md:hidden" @click="open = false"></div>
		</Transition>

		<!-- ============ Sidebar ============ -->
		<aside
			class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-[#E4E6EA] bg-white transition-[width,transform] duration-200 md:translate-x-0"
			:class="[open ? 'translate-x-0 shadow-[0_24px_60px_rgba(31,35,45,0.25)] md:shadow-none' : '-translate-x-full', collapsed ? 'w-[248px] md:w-[84px]' : 'w-[248px]']"
			@click="handleSidebarBackgroundClick"
		>
			<!-- Brand -->
			<div class="flex h-[68px] shrink-0 items-center justify-between border-b border-[#E4E6EA] px-4 md:h-[72px]" :class="collapsed ? 'md:justify-center md:px-2' : ''">
				<div class="flex min-w-0 items-center gap-3">
					<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-[#C8102E] text-sm font-bold tracking-wide text-white shadow-[0_4px_12px_rgba(200,16,46,0.3)]" :class="collapsed ? 'md:h-9 md:w-9 md:rounded-lg md:text-xs' : ''">KR</span>
					<span v-if="!collapsed || open" class="min-w-0 leading-[18px]">
						<span class="block truncate text-[15px] font-semibold text-[#25272B]">KRCTI MHPSS</span>
						<span class="block truncate text-xs text-[#858891]">Case management</span>
					</span>
				</div>
				<button type="button" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-[#737780] transition hover:bg-[#F4F5F7] md:hidden" aria-label="Close menu" @click="open = false">
					<X :size="20" />
				</button>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
				<div v-for="(group, gi) in groups" :key="group.title" :class="gi ? 'mt-5' : ''">
					<p v-if="!collapsed || open" class="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-[#92949A]">{{ group.title }}</p>
					<div v-else-if="gi" class="mx-3 mb-3 hidden h-px bg-[#E4E6EA] md:block" aria-hidden="true"></div>
					<div class="space-y-1">
						<router-link
							v-for="item in group.items"
							:key="item.name"
							:to="{ name: item.name }"
							:title="collapsed ? navLabel(item) : undefined"
							:aria-label="collapsed ? navLabel(item) : undefined"
							:aria-current="isActive(item) ? 'page' : undefined"
							:class="linkClass(isActive(item))"
							@click="open = false"
						>
							<span v-if="isActive(item)" class="absolute -left-3 bottom-2 top-2 w-[3px] rounded-r-full bg-[#C8102E]" aria-hidden="true"></span>
							<component :is="item.icon" :size="19" class="shrink-0" />
							<span v-if="!collapsed || open" class="truncate">{{ navLabel(item) }}</span>
						</router-link>
					</div>
				</div>
			</nav>

			<!-- Collapse -->
			<div class="hidden shrink-0 border-t border-[#E4E6EA] p-3 md:block">
				<button
					type="button"
					class="flex h-11 w-full items-center gap-3 rounded-[10px] px-3 text-sm font-medium text-[#62656D] transition-colors hover:bg-[#F4F5F7] hover:text-[#25272B] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
					:class="collapsed ? 'md:justify-center md:px-0' : ''"
					:title="collapsed ? 'Expand sidebar' : undefined"
					:aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
					:aria-expanded="!collapsed"
					@click="toggleSidebar"
				>
					<PanelLeftOpen v-if="collapsed" :size="19" class="shrink-0" />
					<PanelLeftClose v-else :size="19" class="shrink-0" />
					<span v-if="!collapsed">Collapse sidebar</span>
				</button>
			</div>
		</aside>

		<!-- ============ Main ============ -->
		<div class="transition-[padding] duration-200" :class="collapsed ? 'md:pl-[84px]' : 'md:pl-[248px]'">
			<!-- Top bar -->
			<header class="sticky top-0 z-30 flex h-[68px] items-center gap-3 border-b border-[#E4E6EA] bg-white/95 px-4 backdrop-blur md:h-[72px] md:px-5 lg:px-7">
				<button type="button" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-[#555860] transition hover:bg-[#F4F5F7] md:hidden" aria-label="Open menu" @click="open = true">
					<Menu :size="21" />
				</button>

				<!-- Breadcrumb -->
				<div class="flex min-w-0 shrink-0 items-center gap-2 text-sm md:w-[220px]">
					<span class="hidden text-[#92949A] md:inline">Workspace</span>
					<ChevronRight :size="15" class="hidden text-[#B9BBC1] md:block" />
					<span class="truncate font-semibold text-[#25272B] md:font-medium md:text-[#33353A]">{{ pageTitle }}</span>
				</div>

				<!-- Client search -->
				<div v-if="me.data && canSearchClients" class="hidden min-w-0 flex-1 justify-center px-4 md:flex lg:px-8">
					<div class="relative w-full max-w-[460px]" data-client-search>
						<label for="topbar-client-search" class="sr-only">Search clients</label>
						<div class="flex h-10 items-center gap-2.5 rounded-xl border border-[#E4E6EA] bg-[#F7F7F8] px-3.5 transition focus-within:border-[#C8102E] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#C8102E]/10">
							<Search :size="17" class="shrink-0 text-[#858891]" />
							<input
								id="topbar-client-search"
								ref="searchInput"
								v-model="searchTerm"
								type="search"
								autocomplete="off"
								placeholder="Search by code, name or phone"
								class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#92949A] focus:ring-0"
								@keydown.esc="searchOpen = false"
								@focus="searchOpen = true"
							/>
							<LoaderCircle v-if="clientSearch.loading" :size="16" class="shrink-0 animate-spin text-[#858891]" />
							<kbd v-else-if="!searchTerm" class="shrink-0 rounded-md border border-[#E4E6EA] bg-white px-1.5 py-0.5 text-[10px] font-semibold text-[#92949A]">/</kbd>
							<button v-else type="button" class="shrink-0 text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="clearSearch">Clear</button>
						</div>

						<div v-if="searchOpen && searchTerm.trim().length >= 2" class="absolute left-0 right-0 top-full z-40 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]">
							<div v-if="clientSearch.loading && !clientSearch.data?.length" class="flex items-center gap-2.5 px-4 py-3.5 text-sm text-[#737780]">
								<LoaderCircle :size="15" class="animate-spin" /> Searching clients…
							</div>
							<div v-else-if="clientSearch.data?.length" class="max-h-[360px] overflow-y-auto p-1.5">
								<router-link v-for="row in clientSearch.data" :key="row.name" :to="{ name: 'ClientProfile', params: { name: row.name } }" class="group flex items-center gap-3 rounded-lg px-2.5 py-2.5 transition hover:bg-[#F7F7F8]" @click="clearSearch">
									<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initialsOf(row.full_name) }}</span>
									<span class="min-w-0 flex-1">
										<span class="block truncate text-sm font-semibold text-[#33353A] group-hover:text-[#B30F2A]">{{ row.full_name }}</span>
										<span class="mt-0.5 block truncate text-xs text-[#858891]">{{ [row.scholar_code, row.phone_number, row.institution].filter(Boolean).join(' · ') }}</span>
									</span>
									<ChevronRight :size="16" class="shrink-0 text-[#B9BBC1] transition group-hover:translate-x-0.5" />
								</router-link>
							</div>
							<div v-else class="px-5 py-8 text-center">
								<span class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><Search :size="18" /></span>
								<p class="mt-3 text-sm font-semibold text-[#33353A]">No clients found</p>
								<p class="mt-1 text-xs text-[#858891]">Nothing matches “{{ searchTerm.trim() }}”.</p>
							</div>
							<router-link v-if="clientSearch.data?.length" :to="{ name: 'Clients' }" class="flex items-center justify-between border-t border-[#ECEDEF] bg-[#FCFCFD] px-4 py-2.5 text-xs font-semibold text-[#A10E24] hover:bg-[#FCE8EB]" @click="clearSearch">
								Open full client list <ArrowRight :size="13" />
							</router-link>
						</div>
					</div>
				</div>
				<div v-else class="flex-1"></div>

				<!-- Right cluster -->
				<div v-if="me.data" class="flex shrink-0 items-center gap-2 sm:gap-3">
					<!-- ===== Notifications (counsellor + programme managers) ===== -->
					<div v-if="hasNotifications" class="relative" data-notification-menu>
						<button
							type="button"
							class="relative flex h-10 w-10 items-center justify-center rounded-xl border border-[#E4E6EA] bg-white text-[#555860] shadow-[0_1px_2px_rgba(20,25,35,0.04)] transition hover:border-[#D5D8DE] hover:bg-[#F7F7F8]"
							:class="notificationsOpen ? 'border-[#C8102E] ring-2 ring-[#C8102E]/10' : ''"
							:aria-label="isProgrammeManager ? 'Programme notifications' : 'Notifications'"
							:aria-expanded="notificationsOpen"
							@click="toggleNotifications"
						>
							<Bell :size="19" />
							<span v-if="bellCount" class="absolute -right-1 -top-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full border-2 border-white bg-[#C8102E] px-1 text-[9px] font-bold leading-none text-white">{{ bellCount > 9 ? '9+' : bellCount }}</span>
						</button>

						<Transition name="shell-pop">
							<div
								v-if="notificationsOpen"
								class="fixed inset-x-3 top-[76px] z-40 flex max-h-[calc(100vh-92px)] flex-col overflow-hidden rounded-2xl border border-[#E4E6EA] bg-white shadow-[0_24px_60px_rgba(31,35,45,0.22)] sm:absolute sm:inset-x-auto sm:right-0 sm:top-full sm:mt-3 sm:w-[420px] sm:max-h-[min(640px,calc(100vh-110px))]"
								role="dialog"
								:aria-label="isProgrammeManager ? 'Programme notifications' : 'Notifications'"
							>
								<!-- Header -->
								<div class="flex items-start justify-between gap-3 px-5 pb-4 pt-5">
									<div>
										<div class="flex items-center gap-2.5">
											<h2 class="text-lg font-semibold tracking-tight text-[#25272B]">{{ isProgrammeManager ? 'Programme notifications' : 'Notifications' }}</h2>
											<span v-if="bellCount" class="flex h-[22px] min-w-[22px] items-center justify-center rounded-full bg-[#C8102E] px-1.5 text-xs font-bold text-white">{{ bellCount }}</span>
										</div>
										<p class="mt-0.5 text-[13px] text-[#858891]">{{ isProgrammeManager ? 'Appointments and completed sessions' : 'Follow-ups and referral updates' }}</p>
									</div>
									<button type="button" class="-mr-1.5 -mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-[#737780] transition hover:bg-[#F4F5F7] hover:text-[#25272B]" aria-label="Close notifications" @click="notificationsOpen = false">
										<X :size="19" />
									</button>
								</div>

								<!-- Toolbar -->
								<div class="flex items-center justify-between gap-2 border-y border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
									<div v-if="hasFilter" class="relative">
										<button type="button" class="inline-flex h-9 items-center gap-2 rounded-lg border bg-white px-3 text-[13px] font-semibold shadow-[0_1px_2px_rgba(20,25,35,0.04)] transition" :class="notificationFilter !== 'all' ? 'border-[#C8102E] text-[#A10E24]' : 'border-[#D9DBE0] text-[#44474E] hover:bg-[#F7F7F8]'" :aria-expanded="filterOpen" aria-haspopup="listbox" @click.stop="filterOpen = !filterOpen">
											<ListFilter :size="15" />
											{{ notificationFilter === 'all' ? 'Filter' : activeFilterLabel }}
										</button>
										<div v-if="filterOpen" class="absolute left-0 top-full z-10 mt-2 w-52 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-label="Filter notifications">
											<button v-for="option in filterOptions" :key="option.value" type="button" role="option" :aria-selected="notificationFilter === option.value" class="flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition" :class="notificationFilter === option.value ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click.stop="chooseFilter(option.value)">
												<span>{{ option.label }}</span>
												<span class="rounded-full px-1.5 py-0.5 text-[11px] font-semibold" :class="notificationFilter === option.value ? 'bg-white text-[#A10E24]' : 'bg-[#F4F5F7] text-[#62656D]'">{{ option.count }}</span>
											</button>
										</div>
									</div>
									<span v-else class="text-xs font-medium text-[#858891]">{{ feed.length }} {{ feed.length === 1 ? 'notification' : 'notifications' }}</span>

									<button type="button" class="inline-flex h-9 items-center gap-2 rounded-lg border border-[#D9DBE0] bg-white px-3 text-[13px] font-semibold text-[#33353A] shadow-[0_1px_2px_rgba(20,25,35,0.04)] transition hover:bg-[#F7F7F8] disabled:cursor-not-allowed disabled:opacity-50" :disabled="!bellCount" @click="markAllRead">
										<CheckCheck :size="16" class="text-[#146C3A]" /> Mark all as read
									</button>
								</div>

								<!-- Body -->
								<div class="min-h-[160px] flex-1 overflow-y-auto" @click="filterOpen = false">
									<div v-if="feedLoading && !feed.length" class="flex items-center justify-center gap-2.5 px-5 py-12 text-sm text-[#737780]">
										<LoaderCircle :size="16" class="animate-spin" /> Checking for updates…
									</div>
									<div v-else-if="feedError" class="px-5 py-12 text-center">
										<span class="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-[#FBE0E4] text-[#A10E24]"><AlertTriangle :size="20" /></span>
										<p class="mt-3 text-sm font-semibold text-[#33353A]">Couldn’t load notifications</p>
										<p class="mt-1 text-xs text-[#858891]">Close and reopen this panel to try again.</p>
									</div>
									<template v-else-if="groupedFeed.length">
										<section v-for="group in groupedFeed" :key="group.label">
											<!-- Date divider -->
											<div class="flex items-center gap-3 px-5 pb-1 pt-4" role="separator">
												<span class="h-px flex-1 bg-[#ECEDEF]"></span>
												<span class="text-xs font-semibold text-[#858891]">{{ group.label }}</span>
												<span class="h-px flex-1 bg-[#ECEDEF]"></span>
											</div>

											<ul class="divide-y divide-[#F0F1F3]">
												<li v-for="item in group.items" :key="item.key">
													<component
														:is="item.to ? 'router-link' : 'div'"
														v-bind="item.to ? { to: item.to } : {}"
														class="group relative flex items-start gap-3 px-5 py-4 transition hover:bg-[#FCFCFD]"
														@click="item.to && openItem(item)"
													>
														<!-- Avatar -->
														<span class="relative mt-0.5 shrink-0">
															<span class="flex h-10 w-10 items-center justify-center rounded-full text-xs font-bold" :class="item.avatarTone">
																<template v-if="item.initials">{{ item.initials }}</template>
																<BellRing v-else :size="17" />
															</span>
															<span class="absolute -bottom-1 -right-1 flex h-[18px] w-[18px] items-center justify-center rounded-full border-2 border-white" :class="item.badgeTone">
																<component :is="item.icon" :size="9" :stroke-width="3" />
															</span>
														</span>

														<!-- Content -->
														<div class="min-w-0 flex-1">
															<p class="text-sm leading-5 text-[#555860]">
																<span class="font-semibold text-[#25272B]">{{ item.actor }}</span>
																<span v-if="item.action"> {{ item.action }}</span>
															</p>
															<p v-if="item.preview" class="mt-1 line-clamp-2 text-[13px] leading-5 text-[#737780]">{{ item.preview }}</p>
															<div class="mt-1.5 flex items-center justify-between gap-3">
																<p class="text-xs text-[#92949A]">{{ item.date ? stamp(item.date) : 'Recently' }}</p>
																<button v-if="!item.to" type="button" class="text-xs font-semibold text-[#A10E24] hover:underline" @click.stop.prevent="item.markRead()">Mark as read</button>
															</div>
															<span v-if="item.chip" class="mt-2.5 inline-flex max-w-full items-center gap-2 rounded-lg border border-[#E4E6EA] bg-white px-3 py-2 text-xs font-medium text-[#44474E]">
																<component :is="item.chip.icon" :size="14" class="shrink-0 text-[#858891]" />
																<span class="truncate">{{ item.chip.label }}</span>
															</span>
														</div>

														<!-- Unread dot -->
														<span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#C8102E]" title="Unread" aria-label="Unread"></span>
													</component>
												</li>
											</ul>
										</section>
									</template>
									<div v-else class="px-5 py-14 text-center">
										<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#DCF3E4] text-[#146C3A]"><Check :size="22" /></span>
										<p class="mt-3 text-sm font-semibold text-[#33353A]">{{ notificationFilter !== 'all' ? 'Nothing in this filter' : 'You’re all caught up' }}</p>
										<p class="mx-auto mt-1 max-w-[260px] text-xs text-[#858891]">{{ notificationFilter !== 'all' ? 'Try another filter to see more updates.' : isProgrammeManager ? 'No new programme activity.' : 'No overdue follow-ups or referral updates.' }}</p>
										<button v-if="notificationFilter !== 'all'" type="button" class="mt-4 text-xs font-semibold text-[#A10E24] hover:underline" @click="chooseFilter('all')">Show all notifications</button>
									</div>
								</div>

								<!-- Footer -->
								<router-link v-if="!isProgrammeManager" :to="{ name: 'FollowUps' }" class="flex shrink-0 items-center justify-between border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3 text-[13px] font-semibold text-[#A10E24] transition hover:bg-[#FCE8EB]" @click="notificationsOpen = false">
									View all follow-ups <ArrowRight :size="14" />
								</router-link>
							</div>
						</Transition>
					</div>

					<span class="hidden h-7 w-px bg-[#E4E6EA] sm:block"></span>

					<!-- Account -->
					<div class="relative" data-account-menu>
						<button type="button" class="flex items-center gap-2.5 rounded-xl p-1 text-left transition hover:bg-[#F7F7F8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30 sm:px-2 sm:py-1.5" :aria-expanded="accountOpen" aria-haspopup="menu" aria-label="Account options" @click="accountOpen = !accountOpen">
							<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
							<span class="hidden xl:block">
								<span class="block max-w-[170px] truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span>
								<span class="mt-0.5 block text-xs text-[#858891]">{{ roleLabel }}</span>
							</span>
							<ChevronDown :size="16" class="hidden text-[#737780] transition-transform sm:block" :class="accountOpen ? 'rotate-180' : ''" />
						</button>
						<div v-if="accountOpen" class="absolute right-0 top-full z-40 mt-2 w-[270px] overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_14px_36px_rgba(31,35,45,0.16)]" role="menu" aria-label="Account options">
							<div class="flex items-center gap-3 border-b border-[#ECEDEF] bg-[#FCFCFD] px-4 py-4">
								<span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-sm font-bold text-[#B30F2A]">{{ initials }}</span>
								<span class="min-w-0">
									<span class="block truncate text-sm font-semibold text-[#33353A]">{{ me.data?.full_name }}</span>
									<span class="mt-1 inline-block max-w-full truncate rounded-full bg-[#F4F5F7] px-2 py-0.5 text-[11px] font-semibold text-[#62656D]">{{ roleLabel }}</span>
								</span>
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

			<!-- Content -->
			<PageLoader v-if="!me.data" />
			<div v-else-if="!allowed" class="mx-auto max-w-lg px-4 py-16 md:py-24">
				<div class="rounded-xl border border-[#E4E6EA] bg-white p-8 text-center shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#FCE8EB] text-[#A10E24]"><ShieldAlert :size="22" /></span>
					<h1 class="mt-4 text-base font-semibold text-[#25272B]">You do not have access to this page</h1>
					<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">Your role doesn’t include permission to view this section.</p>
					<router-link :to="{ name: 'Home' }" class="mt-5 inline-flex items-center justify-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#A10E24]">
						<ArrowLeft :size="16" /> Go to my home page
					</router-link>
				</div>
			</div>
			<slot v-else />
		</div>
	</div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { AlertTriangle, ArrowLeft, ArrowRight, Bell, BellRing, BookOpen, CalendarDays, Check, CheckCheck, ChevronDown, ChevronRight, ClipboardCheck, ClipboardList, HeartHandshake, LayoutDashboard, ListFilter, LoaderCircle, LogOut, Menu, PanelLeftClose, PanelLeftOpen, Search, ShieldAlert, Users, UsersRound, X } from "lucide-vue-next"
import { me } from "../data/me"
import { session } from "../data/session"

const NAV = [
	{ label: "Dashboard", name: "Home", icon: LayoutDashboard, match: ["Home"], roles: ["counsellor"], group: "Workspace" },
	{ label: "Clients", name: "Clients", icon: UsersRound, match: ["Clients", "ClientNew", "ClientProfile", "ClientEdit", "Baseline"], roles: ["counsellor"], group: "Workspace" },
	{ label: "Appointments", name: "Appointments", icon: CalendarDays, match: ["Appointments", "AppointmentNew", "AppointmentEdit"], roles: ["counsellor"], group: "Workspace" },
	{ label: "Follow-ups", name: "FollowUps", icon: HeartHandshake, match: ["FollowUps"], roles: ["counsellor"], group: "Workspace" },
	{ label: "Session records", name: "SessionRecords", icon: BookOpen, match: ["SessionRecords", "SessionRecord"], roles: ["counsellor"], group: "Workspace" },
	{ label: "Programme", name: "Programme", icon: ClipboardList, match: ["Programme"], roles: ["krcti_pm", "woc_pm"], group: "Programme" },
	{ label: "Programme clients", name: "ProgrammeClients", icon: UsersRound, match: ["ProgrammeClients", "ProgrammeClientDetail", "ProgrammeClientNew"], roles: ["krcti_pm", "woc_pm"], group: "Programme" },
	{ label: "Counsellors", name: "ProgrammeCounsellors", icon: Users, match: ["ProgrammeCounsellors"], roles: ["krcti_pm", "woc_pm"], group: "Programme" },
	{ label: "Session management", name: "ProgrammeSessions", icon: CalendarDays, match: ["ProgrammeSessions"], roles: ["krcti_pm", "woc_pm"], group: "Programme" },
	{ label: "Audit logs", name: "AuditLogs", icon: ClipboardCheck, match: ["AuditLogs"], roles: ["dpo"], group: "Compliance" },
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

// ---- Resources ----
const searchTerm = ref("")
const searchInput = ref(null)
const searchOpen = ref(false)
const notificationsOpen = ref(false)
const filterOpen = ref(false)
const notificationFilter = ref("all")
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

// ---- Roles ----
const role = computed(() => me.data?.role)
const isProgrammeManager = computed(() => ["krcti_pm", "woc_pm"].includes(role.value))
const isCounsellor = computed(() => role.value === "counsellor")
const hasNotifications = computed(() => isCounsellor.value || isProgrammeManager.value)
const canSearchClients = computed(() => isCounsellor.value)

// ---- Date helpers ----
const toDate = (value) => {
	if (!value) return null
	const date = new Date(String(value).replace(" ", "T"))
	return Number.isNaN(date.getTime()) ? null : date
}
const dayKey = (date) => `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
function dayLabel(date) {
	const today = new Date()
	const yesterday = new Date(Date.now() - 86400000)
	if (dayKey(date) === dayKey(today)) return "Today"
	if (dayKey(date) === dayKey(yesterday)) return "Yesterday"
	return date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })
}
function stamp(value) {
	const date = toDate(value)
	if (!date) return ""
	return `${date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })}, ${date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}`
}
const initialsOf = (name) => (name || "").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase()

// ---- Notification feed ----
const TONES = {
	red: { avatar: "bg-[#FBE0E4] text-[#A10E24]", badge: "bg-[#C8102E] text-white" },
	blue: { avatar: "bg-[#E0EAFD] text-[#1B4DB1]", badge: "bg-[#1B4DB1] text-white" },
	green: { avatar: "bg-[#DCF3E4] text-[#146C3A]", badge: "bg-[#146C3A] text-white" },
}
const overdueFollowups = computed(() => notificationData.data?.overdue_notifications || [])
const referralEvents = computed(() => referralNotificationData.data?.notifications || [])
const programmeNotifications = computed(() => programmeNotificationData.data?.notifications || [])

const counsellorFeed = computed(() => [
	...overdueFollowups.value.map((row) => {
		const client = row.client_name || row.client_id
		return {
			key: `overdue-${row.name}`,
			type: "followup",
			actor: client,
			action: "has an overdue follow-up",
			preview: row.date_time ? `Scheduled for ${stamp(row.date_time)}` : "",
			date: row.date_time,
			initials: initialsOf(client),
			avatarTone: TONES.red.avatar,
			badgeTone: TONES.red.badge,
			icon: BellRing,
			to: { name: "SessionRecord", params: { name: row.name } },
			markRead: () => markOverdueNotificationsRead.submit({ name: row.name }),
		}
	}),
	...referralEvents.value.map((row) => {
		const client = row.client_name || row.client_id
		const received = row.direction === "received"
		const tone = received ? TONES.blue : TONES.green
		return {
			key: `referral-${row.id}`,
			type: "referral",
			actor: received ? row.from_name : "You",
			action: received ? `referred ${client} to you` : `referred ${client} to ${row.to_name}`,
			preview: row.reason,
			date: row.referred_on || row.creation || row.modified,
			initials: initialsOf(received ? row.from_name : client),
			avatarTone: tone.avatar,
			badgeTone: tone.badge,
			icon: Users,
			to: { name: "SessionRecord", params: { name: row.appointment } },
			markRead: () => markReferralNotificationsRead.submit({ name: row.id }),
		}
	}),
])
const programmeFeed = computed(() => programmeNotifications.value.map((item) => ({
	key: `programme-${item.name}`,
	type: "programme",
	actor: item.title,
	action: "",
	preview: item.description,
	date: item.creation,
	initials: "",
	avatarTone: TONES.blue.avatar,
	badgeTone: TONES.blue.badge,
	icon: Check,
	to: null,
	markRead: () => markProgrammeNotificationsRead.submit({ name: item.name }),
})))

const feed = computed(() => isProgrammeManager.value ? programmeFeed.value : counsellorFeed.value)
const feedLoading = computed(() => isProgrammeManager.value
	? programmeNotificationData.loading && !programmeNotificationData.data
	: (notificationData.loading && !notificationData.data) || (referralNotificationData.loading && !referralNotificationData.data))
const feedError = computed(() => isProgrammeManager.value
	? !!programmeNotificationData.error
	: !!notificationData.error && !overdueFollowups.value.length && !referralEvents.value.length)
const bellCount = computed(() => isProgrammeManager.value
	? (programmeNotificationData.data?.unread_count || 0)
	: (notificationData.data?.overdue_followups || 0) + (referralNotificationData.data?.unread_count || 0))

// Filter (counsellors have two kinds of updates)
const hasFilter = computed(() => isCounsellor.value)
const filterOptions = computed(() => [
	{ value: "all", label: "All notifications", count: feed.value.length },
	{ value: "followup", label: "Follow-ups", count: feed.value.filter((item) => item.type === "followup").length },
	{ value: "referral", label: "Referrals", count: feed.value.filter((item) => item.type === "referral").length },
])
const activeFilterLabel = computed(() => filterOptions.value.find((option) => option.value === notificationFilter.value)?.label || "Filter")
const filteredFeed = computed(() => notificationFilter.value === "all" ? feed.value : feed.value.filter((item) => item.type === notificationFilter.value))
function chooseFilter(value) {
	notificationFilter.value = value
	filterOpen.value = false
}

// Newest first, grouped under date dividers
const groupedFeed = computed(() => {
	const sorted = [...filteredFeed.value].sort((a, b) => (toDate(b.date)?.getTime() ?? -Infinity) - (toDate(a.date)?.getTime() ?? -Infinity))
	const groups = []
	for (const item of sorted) {
		const date = toDate(item.date)
		const label = date ? dayLabel(date) : "Recent"
		const last = groups[groups.length - 1]
		if (last && last.label === label) last.items.push(item)
		else groups.push({ label, items: [item] })
	}
	return groups
})

function toggleNotifications() {
	notificationsOpen.value = !notificationsOpen.value
	filterOpen.value = false
	if (!notificationsOpen.value) return
	if (isProgrammeManager.value) {
		programmeNotificationData.submit()
	} else {
		notificationData.submit()
		referralNotificationData.submit()
	}
}
function openItem(item) {
	item.markRead()
	notificationsOpen.value = false
}
function markAllRead() {
	if (isProgrammeManager.value) {
		markProgrammeNotificationsRead.submit()
	} else {
		markReferralNotificationsRead.submit()
		markOverdueNotificationsRead.submit()
	}
}

// ---- Client search ----
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
function clearSearch() {
	searchTerm.value = ""
	searchOpen.value = false
}
function logout() {
	accountOpen.value = false
	session.logout.submit()
}

// ---- Global listeners ----
function closeHeaderMenus(event) {
	if (!event.target.closest("[data-client-search]")) searchOpen.value = false
	if (!event.target.closest("[data-notification-menu]")) {
		notificationsOpen.value = false
		filterOpen.value = false
	}
	if (!event.target.closest("[data-account-menu]")) accountOpen.value = false
}
function onKeydown(event) {
	if (event.key === "Escape") {
		if (filterOpen.value) {
			filterOpen.value = false
			return
		}
		searchOpen.value = false
		notificationsOpen.value = false
		accountOpen.value = false
		return
	}
	// "/" focuses the client search, unless the person is already typing somewhere
	const target = event.target
	const typing = target instanceof HTMLElement && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
	if (event.key === "/" && !typing && canSearchClients.value && searchInput.value) {
		event.preventDefault()
		searchInput.value.focus()
	}
}
onMounted(() => {
	document.addEventListener("click", closeHeaderMenus)
	document.addEventListener("keydown", onKeydown)
	notificationTimer = setInterval(() => {
		if (notificationsOpen.value) return
		if (isCounsellor.value) {
			notificationData.submit()
			referralNotificationData.submit()
		} else if (isProgrammeManager.value) {
			programmeNotificationData.submit()
		}
	}, 60000)
})
onUnmounted(() => {
	clearTimeout(searchTimer)
	clearInterval(notificationTimer)
	document.removeEventListener("click", closeHeaderMenus)
	document.removeEventListener("keydown", onKeydown)
})

// ---- Navigation ----
const roleLabel = computed(() => LABELS[role.value] || "")
const pageTitle = computed(() => {
	const item = NAV.find((entry) => entry.match.includes(route.name))
	return item ? navLabel(item) : "Dashboard"
})
const initials = computed(() => initialsOf(me.data?.full_name || "KR") || "KR")
function navLabel(item) {
	if (item.name !== "Programme") return item.label
	if (role.value === "krcti_pm") return "KRCTI PM Dashboard"
	if (role.value === "woc_pm") return "WoC PM Dashboard"
	return "Programme Dashboard"
}
const items = computed(() => NAV.filter((item) => item.roles.includes(role.value)))
const groups = computed(() => {
	const map = new Map()
	for (const item of items.value) {
		if (!map.has(item.group)) map.set(item.group, { title: item.group, items: [] })
		map.get(item.group).items.push(item)
	}
	return [...map.values()]
})
const allowed = computed(() => !route.meta.roles || route.meta.roles.includes(role.value))
const isActive = (item) => item.match.includes(route.name)
const linkClass = (active) => [
	"relative flex h-11 items-center gap-3 rounded-[10px] px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40",
	collapsed.value ? "md:justify-center md:px-0" : "",
	active ? "bg-[#FCE8EB] font-semibold text-[#A10E24]" : "text-[#555860] hover:bg-[#F4F5F7] hover:text-[#25272B]",
]
</script>

<style scoped>
.shell-fade-enter-active, .shell-fade-leave-active { transition: opacity 0.2s ease; }
.shell-fade-enter-from, .shell-fade-leave-to { opacity: 0; }

.shell-pop-enter-active, .shell-pop-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; transform-origin: top right; }
.shell-pop-enter-from, .shell-pop-leave-to { opacity: 0; transform: translateY(-6px) scale(0.98); }

@media (prefers-reduced-motion: reduce) {
	.shell-pop-enter-active, .shell-pop-leave-active { transition: opacity 0.15s ease; }
	.shell-pop-enter-from, .shell-pop-leave-to { transform: none; }
}
</style>
