<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- ============ Client detail ============ -->
			<template v-if="kind === 'client'">
				<PageLoader v-if="client.loading && !client.data" />
				<template v-else-if="client.data">
					<!-- Breadcrumb -->
					<div class="mb-5 text-sm text-[#737780]">
						<router-link :to="{ name: 'ProgrammeClients' }" class="hover:text-[#A10E24]">Programme clients</router-link>
						<span class="px-2">/</span><span class="font-semibold text-[#25272B]">{{ client.data.scholar_code || client.data.full_name }}</span>
					</div>

					<!-- Profile header -->
					<section class="rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-6">
						<div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
							<div class="flex min-w-0 items-center gap-4">
								<span class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-lg font-bold text-[#B30F2A] sm:h-16 sm:w-16 sm:text-xl">{{ initials(client.data.full_name) }}</span>
								<div class="min-w-0">
									<p class="text-xs font-semibold uppercase tracking-wide text-[#A10E24]">Programme client</p>
									<h1 class="mt-0.5 truncate text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">{{ client.data.full_name }}</h1>
									<div class="mt-2 flex flex-wrap items-center gap-2">
										<span v-if="client.data.scholar_code" class="rounded-full bg-[#FCE8EB] px-2.5 py-1 text-xs font-semibold text-[#A10E24]">{{ client.data.scholar_code }}</span>
										<span v-if="client.data.programme_case_status" class="rounded-full bg-[#E0EAFD] px-2.5 py-1 text-xs font-semibold text-[#1B4DB1]">{{ client.data.programme_case_status }}</span>
										<span v-if="client.data.programme_stream" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ client.data.programme_stream }}</span>
									</div>
								</div>
							</div>
							<router-link :to="{ name: 'ProgrammeClients' }" class="inline-flex shrink-0 items-center justify-center gap-2 self-start rounded-lg border border-[#D9DBE0] bg-white px-4 py-2.5 text-sm font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8] sm:self-auto">
								<ArrowLeft :size="16" /> Programme clients
							</router-link>
						</div>
					</section>

					<!-- Summary cards -->
					<section class="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Session summary">
						<div v-for="card in summaryCards" :key="card.label" class="rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
							<div class="flex items-center justify-between gap-2">
								<span class="text-xs font-semibold text-[#555860]">{{ card.label }}</span>
								<span class="flex h-8 w-8 items-center justify-center rounded-full" :class="card.tone"><component :is="card.icon" :size="16" /></span>
							</div>
							<span class="mt-3 block text-[28px] font-semibold leading-none tabular-nums text-[#25272B]">{{ card.value }}</span>
						</div>
					</section>

					<div class="mt-5 flex items-start gap-5 max-[900px]:flex-col">
						<!-- Client information -->
						<aside class="w-[340px] shrink-0 max-[900px]:w-full min-[901px]:sticky min-[901px]:top-6" aria-label="Client information">
							<section class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
								<div class="border-b border-[#ECEDEF] px-5 py-4">
									<h2 class="text-base font-semibold text-[#25272B]">Client information</h2>
									<p class="mt-0.5 text-xs text-[#858891]">Registration and referral details.</p>
								</div>
								<dl class="divide-y divide-[#F0F1F3] text-sm">
									<div v-for="item in clientInfo" :key="item.label" class="flex items-start justify-between gap-4 px-5 py-3">
										<dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-[#858891]">{{ item.label }}</dt>
										<dd class="min-w-0 break-words text-right font-medium text-[#33353A]">{{ item.value || '—' }}</dd>
									</div>
								</dl>
							</section>
						</aside>

						<!-- Main card: tabs -->
						<section class="min-w-0 flex-1 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
							<div class="flex gap-1 overflow-x-auto border-b border-[#ECEDEF] px-3 pt-2" role="tablist" aria-label="Client record">
								<button v-for="tab in mainTabs" :key="tab.key" type="button" role="tab" :aria-selected="activeTab === tab.key" class="relative inline-flex shrink-0 items-center gap-2 px-3 py-3 text-sm font-semibold transition" :class="activeTab === tab.key ? 'text-[#A10E24]' : 'text-[#737780] hover:text-[#33353A]'" @click="activeTab = tab.key">
									<component :is="tab.icon" :size="16" />
									{{ tab.label }}
									<span class="rounded-full px-2 py-0.5 text-[11px]" :class="activeTab === tab.key ? 'bg-[#FCE8EB] text-[#A10E24]' : 'bg-[#F4F5F7] text-[#62656D]'">{{ tab.badge }}</span>
									<span v-if="activeTab === tab.key" class="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-[#C8102E]"></span>
								</button>
							</div>

							<!-- ===== Case history tab ===== -->
							<div v-if="activeTab === 'history'">
								<div class="flex flex-wrap items-center justify-between gap-3 px-5 pb-1 pt-4">
									<div>
										<h2 class="text-base font-semibold text-[#25272B]">Case history</h2>
										<p class="mt-0.5 text-xs text-[#858891]">Newest sessions first. Select a session to see its details.</p>
									</div>
									<button v-if="expandableIds.length" type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-[#D9DBE0] bg-white px-3 py-1.5 text-xs font-semibold text-[#44474E] transition hover:bg-[#F7F7F8]" @click="toggleAll">
										<ChevronsUpDown :size="14" /> {{ allOpen ? 'Collapse all' : 'Expand all' }}
									</button>
								</div>

								<div v-if="history.length" class="flex flex-wrap gap-2 px-5 pb-4 pt-3" role="tablist" aria-label="Filter by status">
									<button v-for="tab in historyTabs" :key="tab.key" type="button" role="tab" :aria-selected="historyFilter === tab.key" class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-semibold transition" :class="historyFilter === tab.key ? 'border-[#C8102E] bg-[#FFF8F9] text-[#A10E24] ring-2 ring-[#C8102E]/10' : 'border-[#D9DBE0] bg-white text-[#44474E] hover:bg-[#F7F7F8]'" @click="historyFilter = tab.key">
										{{ tab.label }}
										<span class="rounded-full px-1.5 py-0.5 text-[10px]" :class="historyFilter === tab.key ? 'bg-white text-[#A10E24]' : 'bg-[#F4F5F7] text-[#62656D]'">{{ tab.count }}</span>
									</button>
								</div>

								<ol v-if="filteredHistory.length" class="space-y-3 border-t border-[#ECEDEF] bg-[#FCFCFD] p-4 sm:p-5">
									<li v-for="entry in filteredHistory" :key="entry.name" class="overflow-hidden rounded-xl border border-l-4 border-[#E4E6EA] bg-white" :class="entryBar(entry)">
										<button type="button" class="flex w-full items-center justify-between gap-4 px-4 py-3.5 text-left transition sm:px-5" :class="hasBody(entry) ? 'cursor-pointer hover:bg-[#FCFCFD]' : 'cursor-default'" :disabled="!hasBody(entry)" :aria-expanded="hasBody(entry) ? isOpen(entry) : undefined" :aria-controls="`entry-${entry.name}`" @click="toggleEntry(entry.name)">
											<span class="flex min-w-0 items-center gap-3">
												<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full" :class="entryIconTone(entry)">
													<ClipboardCheck v-if="entry.status === 'Completed'" :size="17" /><Ban v-else-if="entry.status === 'Cancelled'" :size="17" /><CalendarClock v-else :size="17" />
												</span>
												<span class="min-w-0">
													<span class="block text-sm font-semibold text-[#25272B]">{{ dateTime(entry.date_time) }}</span>
													<span class="mt-0.5 block truncate text-xs text-[#737780]">{{ entry.session_type }}<template v-if="entry.mode_of_contact"> · {{ entry.mode_of_contact }}</template><template v-if="entry.counsellor_name"> · {{ entry.counsellor_name }}</template></span>
												</span>
											</span>
											<span class="flex shrink-0 items-center gap-3">
												<Badge :label="entry.overdue ? 'Overdue' : entry.status" :theme="entry.overdue ? 'red' : statusTheme(entry.status)" />
												<ChevronDown v-if="hasBody(entry)" :size="16" class="text-[#737780] transition-transform" :class="isOpen(entry) ? 'rotate-180' : ''" />
											</span>
										</button>

										<div v-if="hasBody(entry) && isOpen(entry)" :id="`entry-${entry.name}`" class="space-y-3 border-t border-[#ECEDEF] px-4 py-4 sm:px-5">
											<div v-if="entry.status === 'Completed'" class="grid gap-3 sm:grid-cols-2">
												<div v-for="item in entryDetails(entry)" :key="item.label" class="rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-4" :class="item.wide ? 'sm:col-span-2' : ''">
													<span class="block text-[11px] font-semibold uppercase tracking-wide text-[#858891]">{{ item.label }}</span>
													<span class="mt-1.5 block whitespace-pre-line break-words text-sm font-medium text-[#2B2F36]">{{ item.value || '—' }}</span>
												</div>
											</div>

											<div v-if="entry.status === 'Completed' && entry.audio_recording" class="rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-4">
												<span class="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><Volume2 :size="14" /> Session audio</span>
								<audio controls preload="none" crossorigin="use-credentials" class="w-full max-w-md"><source :src="backendUrl(entry.audio_recording)" /></audio>
											</div>

											<p v-for="referral in entry.referral_history || []" :key="`ref-${referral.referred_on}`" class="rounded-lg bg-[#E0EAFD] px-3.5 py-2.5 text-xs leading-5 text-[#1B4DB1]">
												<span class="font-semibold">Referred</span> {{ referral.from_name }} → {{ referral.to_name }} on {{ dateTime(referral.referred_on) }}. {{ referral.reason }}
											</p>
											<p v-for="action in entry.management_history || []" :key="`manage-${action.event_time}`" class="rounded-lg bg-[#F4F5F7] px-3.5 py-2.5 text-xs leading-5 text-[#555860]">
												<span class="font-semibold">{{ action.event_type }}</span> by {{ action.manager_name }} on {{ dateTime(action.event_time) }}: {{ action.reason }}<span v-if="action.to_name"> · {{ action.from_name }} → {{ action.to_name }}</span>
											</p>
										</div>
									</li>
								</ol>

								<div v-else class="border-t border-[#ECEDEF] px-5 py-14 text-center">
									<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><BookOpen :size="22" /></span>
									<p class="mt-3 text-sm font-semibold text-[#33353A]">{{ history.length ? 'No entries for this status' : 'No session history yet' }}</p>
									<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ history.length ? 'Choose another status above to see more entries.' : 'Sessions will appear here once they are booked or recorded.' }}</p>
								</div>
							</div>

							<!-- ===== Baseline survey tab ===== -->
							<div v-else>
								<div class="flex flex-wrap items-center justify-between gap-3 px-5 py-4">
									<div>
										<h2 class="text-base font-semibold text-[#25272B]">Baseline survey</h2>
										<p class="mt-0.5 text-xs text-[#858891]">{{ baselineSurvey ? `Completed ${dateTime(baselineSurvey.completed_on)}` : 'Not yet submitted' }}</p>
									</div>
									<span v-if="baselineSurvey" class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="baselineSurvey.consent === 'Declined' ? 'bg-[#E4E6EA] text-[#3A3F47]' : 'bg-[#DCF3E4] text-[#146C3A]'">{{ baselineSurvey.status || (baselineSurvey.consent === 'Declined' ? 'Consent declined' : 'Recorded') }}</span>
								</div>

								<div v-if="!baselineSurvey" class="border-t border-[#ECEDEF] px-5 py-14 text-center">
									<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><FileText :size="22" /></span>
									<p class="mt-3 text-sm font-semibold text-[#33353A]">No baseline survey recorded</p>
									<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">No baseline survey has been submitted for this client.</p>
								</div>

								<div v-else-if="baselineSurvey.consent === 'Declined'" class="border-t border-[#ECEDEF] p-5">
									<div class="flex items-start gap-3 rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-4">
										<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#E4E6EA] text-[#3A3F47]"><Ban :size="17" /></span>
										<div>
											<p class="text-sm font-semibold text-[#33353A]">Consent declined</p>
											<p class="mt-1 text-sm text-[#737780]">{{ baselineSurvey.declined_reason || 'No reason was given.' }}</p>
										</div>
									</div>
								</div>

								<div v-else class="space-y-5 border-t border-[#ECEDEF] bg-[#FCFCFD] p-4 sm:p-5">
									<!-- Wellbeing highlight -->
									<div v-if="wellbeingScore !== null" class="rounded-xl border border-[#E4E6EA] bg-white p-4 sm:p-5">
										<div class="flex items-end justify-between gap-3">
											<div>
												<p class="text-[11px] font-semibold uppercase tracking-wide text-[#858891]">Wellbeing self-rating</p>
												<p class="mt-1 text-[28px] font-semibold leading-none tabular-nums text-[#25272B]">{{ wellbeingScore }}<span class="text-base font-medium text-[#858891]"> / 10</span></p>
											</div>
											<p v-if="baselineSurvey.stress_frequency" class="text-right text-xs text-[#737780]">Recent stress<span class="mt-0.5 block text-sm font-semibold text-[#33353A]">{{ baselineSurvey.stress_frequency }}</span></p>
										</div>
										<div class="mt-4 h-2 overflow-hidden rounded-full bg-[#E4E6EA]">
											<div class="h-full rounded-full bg-[#C8102E] transition-all" :style="{ width: `${Math.min(100, wellbeingScore * 10)}%` }"></div>
										</div>
									</div>

									<!-- Main concerns chips -->
									<div v-if="concernList.length || baselineSurvey.main_concerns_other" class="rounded-xl border border-[#E4E6EA] bg-white p-4 sm:p-5">
										<p class="text-[11px] font-semibold uppercase tracking-wide text-[#858891]">Main concerns</p>
										<div class="mt-3 flex flex-wrap gap-2">
											<span v-for="item in concernList" :key="item" class="rounded-full bg-[#FCE8EB] px-3 py-1 text-xs font-semibold text-[#A10E24]">{{ item }}</span>
											<span v-if="baselineSurvey.main_concerns_other" class="rounded-full bg-[#F4F5F7] px-3 py-1 text-xs font-semibold text-[#555860]">Other: {{ baselineSurvey.main_concerns_other }}</span>
										</div>
									</div>

									<!-- Grouped answers -->
									<section v-for="group in surveyGroups" :key="group.title" class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white">
										<div class="flex items-center gap-2.5 border-b border-[#ECEDEF] px-4 py-3 sm:px-5">
											<span class="flex h-7 w-7 items-center justify-center rounded-full bg-[#F4F5F7] text-[#62656D]"><component :is="group.icon" :size="14" /></span>
											<h3 class="text-sm font-semibold text-[#25272B]">{{ group.title }}</h3>
										</div>
										<dl class="grid gap-3 p-4 sm:grid-cols-2 sm:p-5">
											<div v-for="[label, value, wide] in group.rows" :key="label" class="rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-4" :class="wide ? 'sm:col-span-2' : ''">
												<dt class="text-[11px] font-semibold uppercase tracking-wide text-[#858891]">{{ label }}</dt>
												<dd class="mt-1.5 whitespace-pre-line break-words text-sm font-medium text-[#2B2F36]">{{ value }}</dd>
											</div>
										</dl>
									</section>
								</div>
							</div>
						</section>
					</div>
				</template>
				<ErrorMessage v-else :message="client.error" />
			</template>

			<!-- ============ Counsellor management ============ -->
			<template v-else-if="kind === 'counsellors'">
				<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
					<div>
						<p class="text-sm font-medium text-[#737780]">Programme</p>
						<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Counsellor management</h1>
						<p class="mt-1 text-sm text-[#737780]">Create and manage counsellor accounts for your programme.</p>
					</div>
					<button type="button" class="inline-flex items-center justify-center gap-2 self-start rounded-lg px-4 py-2.5 text-sm font-semibold shadow-sm transition sm:self-auto" :class="showCreate ? 'border border-[#D9DBE0] bg-white text-[#33353A] hover:bg-[#F7F7F8]' : 'bg-[#C8102E] text-white hover:bg-[#A10E24]'" :aria-expanded="showCreate" @click="showCreate = !showCreate">
						<X v-if="showCreate" :size="17" /><UserRoundPlus v-else :size="17" /> {{ showCreate ? 'Close' : 'Create counsellor' }}
					</button>
				</div>

				<!-- Create form -->
				<section v-if="showCreate" class="mt-6 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<div class="border-b border-[#ECEDEF] px-5 py-4">
						<h2 class="text-base font-semibold text-[#25272B]">New counsellor account</h2>
						<p class="mt-0.5 text-xs text-[#858891]">The counsellor signs in with this email and password.</p>
					</div>
					<form class="grid gap-4 p-5 sm:grid-cols-2 sm:p-6" @submit.prevent="createCounsellor">
						<div>
							<label for="new-first-name" class="mb-1.5 block text-xs font-semibold text-[#555860]">First name <span class="text-[#A10E24]">*</span></label>
							<input id="new-first-name" v-model="newUser.first_name" class="field" required placeholder="First name" />
						</div>
						<div>
							<label for="new-last-name" class="mb-1.5 block text-xs font-semibold text-[#555860]">Last name</label>
							<input id="new-last-name" v-model="newUser.last_name" class="field" placeholder="Last name" />
						</div>
						<div>
							<label for="new-email" class="mb-1.5 block text-xs font-semibold text-[#555860]">Email <span class="text-[#A10E24]">*</span></label>
							<input id="new-email" v-model="newUser.email" class="field" required type="email" placeholder="name@example.com" />
						</div>
						<div>
							<label for="new-password" class="mb-1.5 block text-xs font-semibold text-[#555860]">Password <span class="text-[#A10E24]">*</span></label>
							<div class="relative">
								<input id="new-password" v-model="newUser.password" class="field pr-11" required :type="showPassword ? 'text' : 'password'" minlength="8" placeholder="At least 8 characters" />
								<button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-[#858891] transition hover:bg-[#F4F5F7] hover:text-[#33353A]" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">
									<EyeOff v-if="showPassword" :size="16" /><Eye v-else :size="16" />
								</button>
							</div>
							<p class="mt-1.5 text-xs text-[#858891]">Use an uppercase letter, a number and a symbol.</p>
						</div>
						<ErrorMessage class="sm:col-span-2" :message="saveUser.error" />
						<div class="flex flex-col-reverse gap-2 border-t border-[#ECEDEF] pt-4 sm:col-span-2 sm:flex-row sm:justify-end">
							<button type="button" class="secondary" @click="showCreate = false">Cancel</button>
							<button class="primary" :disabled="saveUser.loading">
								<LoaderCircle v-if="saveUser.loading" :size="15" class="mr-2 animate-spin" />{{ saveUser.loading ? 'Creating…' : 'Create account' }}
							</button>
						</div>
					</form>
				</section>

				<!-- Search & filter -->
				<section class="mt-6 rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
					<div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_230px] md:items-end">
						<label class="block">
							<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Search counsellors</span>
							<span class="flex h-11 items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10">
								<Search :size="17" class="shrink-0 text-[#858891]" />
								<input v-model="term" type="search" placeholder="Name or email" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
								<button v-if="term" type="button" class="shrink-0 text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="term = ''">Clear</button>
							</span>
						</label>
						<div class="block">
							<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Account status</span>
							<div class="relative">
								<button type="button" class="flex h-11 w-full items-center justify-between rounded-lg border border-[#D9DBE0] bg-white px-3.5 text-left text-sm font-medium text-[#33353A] shadow-[0_1px_2px_rgba(20,25,35,0.03)] outline-none transition hover:border-[#BFC2C8] focus:border-[#C8102E] focus:ring-2 focus:ring-[#C8102E]/10" :aria-expanded="statusMenuOpen" aria-haspopup="listbox" @click="statusMenuOpen = !statusMenuOpen" @keydown.esc="statusMenuOpen = false">
									<span>{{ selectedStatus.label }}</span>
									<ChevronDown :size="16" class="shrink-0 text-[#737780] transition-transform" :class="statusMenuOpen ? 'rotate-180' : ''" />
								</button>
								<div v-if="statusMenuOpen" class="absolute left-0 right-0 z-20 mt-2 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" aria-label="Filter counsellors by status">
									<button v-for="option in statusOptions" :key="option.value" type="button" role="option" :aria-selected="status === option.value" class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition" :class="status === option.value ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click="chooseStatus(option.value)">
										{{ option.label }}
										<Check v-if="status === option.value" :size="16" class="text-[#C8102E]" />
									</button>
								</div>
							</div>
						</div>
					</div>
				</section>

				<ErrorMessage class="mt-4" :message="counsellors.error || (!showCreate ? saveUser.error : '')" />

				<!-- Counsellor list -->
				<section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#ECEDEF] px-5 py-4">
						<div>
							<h2 class="text-base font-semibold text-[#25272B]">{{ searching ? 'Search results' : status || 'Counsellor accounts' }}</h2>
							<p class="mt-0.5 text-xs text-[#858891]">Removing a counsellor disables their account and preserves their historical records.</p>
						</div>
						<div class="flex items-center gap-2">
							<LoaderCircle v-if="counsellors.loading || saveUser.loading" :size="16" class="animate-spin text-[#858891]" />
							<span v-if="searching || status" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ rows.length }} found</span>
							<span v-else class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ rows.length }} total</span>
						</div>
					</div>

					<div v-if="counsellors.loading && !counsellors.data" class="px-5 py-10"><PageLoader /></div>
					<div v-else-if="!rows.length" class="px-5 py-14 text-center">
						<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><UsersRound :size="22" /></span>
						<p class="mt-3 text-sm font-semibold text-[#33353A]">{{ searching || status ? 'No matching counsellors' : 'No counsellor accounts yet' }}</p>
						<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ searching || status ? 'Try another name, email or status.' : 'Create the first counsellor account to get started.' }}</p>
						<button v-if="!searching && !status" type="button" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-[#C8102E] px-4 py-2 text-sm font-semibold text-white hover:bg-[#A10E24]" @click="showCreate = true"><UserRoundPlus :size="16" /> Create counsellor</button>
					</div>

					<div v-else class="overflow-x-auto">
						<table class="w-full min-w-[760px] text-left">
							<thead><tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]"><th class="px-5 py-3">Counsellor</th><th class="px-4 py-3">Email</th><th class="px-4 py-3">Status</th><th class="px-4 py-3">Last login</th><th class="px-5 py-3 text-right">Account</th></tr></thead>
							<tbody class="divide-y divide-[#F0F1F3]">
								<tr v-for="row in rows" :key="row.name" class="transition hover:bg-[#FCFCFD]">
									<td class="px-5 py-3.5">
										<div class="flex items-center gap-3">
											<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]" aria-hidden="true">{{ initials(row.full_name) }}</span>
													<router-link :to="{ name: 'ProgrammeSessions', query: { counsellor: row.name } }" class="min-w-0 truncate text-sm font-semibold text-[#33353A] hover:text-[#A10E24] hover:underline">{{ row.full_name }}</router-link>
										</div>
									</td>
									<td class="max-w-[260px] px-4 py-3.5 text-sm text-[#555860]"><span class="block truncate">{{ row.name }}</span></td>
									<td class="px-4 py-3.5"><Badge :label="row.enabled ? 'Active' : 'Inactive'" :theme="row.enabled ? 'green' : 'gray'" /></td>
									<td class="whitespace-nowrap px-4 py-3.5 text-sm text-[#555860]">{{ dateTime(row.last_login) }}</td>
									<td class="px-5 py-3.5 text-right">
										<button v-if="row.enabled" type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 py-2 text-sm font-semibold text-[#33353A] shadow-sm transition hover:bg-[#F7F7F8] disabled:cursor-wait disabled:opacity-60" :disabled="saveUser.loading" @click="retireCounsellor(row, 'deactivate')"><UserX :size="15" /> Deactivate</button>
										<button v-else type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-[#F0C8CE] bg-[#FFF6F7] px-3.5 py-2 text-sm font-semibold text-[#A10E24] shadow-sm transition hover:bg-[#FCE8EB] disabled:cursor-wait disabled:opacity-60" :disabled="saveUser.loading" @click="retireCounsellor(row, 'remove')"><Trash2 :size="15" /> Remove</button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>

					<div v-if="allRows.length" class="flex flex-wrap items-center justify-between gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3">
						<p class="text-xs text-[#737780]">Showing {{ rows.length }} of {{ allRows.length }} counsellor accounts</p>
						<p class="text-xs text-[#858891]">Deactivate first, then remove to retire an account.</p>
					</div>
				</section>
			</template>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { ArrowLeft, Ban, BookOpen, CalendarClock, Check, ChevronDown, ChevronsUpDown, ClipboardCheck, ClipboardList, Eye, EyeOff, FileText, HeartPulse, Home, Layers, LifeBuoy, LoaderCircle, Search, Trash2, UserRoundPlus, UsersRound, UserX, Volume2, X } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"
import { backendUrl } from "../data/backend"

const props = defineProps({ kind: { type: String, required: true } })
const route = useRoute()
const kind = computed(() => props.kind)
const client = createResource({ url: "krcti_mhpss.api.oversight.programme_client_detail" })
const counsellors = createResource({ url: "krcti_mhpss.api.oversight.programme_counsellors" })
const saveUser = createResource({
	url: "krcti_mhpss.api.oversight.programme_save_counsellor",
	onSuccess: () => {
		showCreate.value = false
		newUser.first_name = newUser.last_name = newUser.email = newUser.password = ""
		counsellors.submit()
	},
})
const showCreate = ref(false)
const showPassword = ref(false)
const newUser = reactive({ first_name: "", last_name: "", email: "", password: "" })

const dateTime = (value) => value ? fmtDateTime(value) : "—"
const issueText = (value) => { try { const parsed = JSON.parse(value); return Array.isArray(parsed) ? parsed.join(", ") : value } catch { return value || "—" } }
const joinParts = (parts, sep = " · ") => parts.filter(Boolean).join(sep)
const statusTheme = (status) => ({ Scheduled: "blue", Completed: "green", Cancelled: "gray" })[status] || "gray"
const entryBar = (entry) => entry.overdue ? "border-l-[#A10E24]" : ({ Scheduled: "border-l-[#1B4DB1]", Completed: "border-l-[#146C3A]", Cancelled: "border-l-[#D5D8DE]" })[entry.status] || "border-l-[#D5D8DE]"
const entryIconTone = (entry) => entry.overdue ? "bg-[#FBE0E4] text-[#A10E24]" : ({ Scheduled: "bg-[#E0EAFD] text-[#1B4DB1]", Completed: "bg-[#DCF3E4] text-[#146C3A]", Cancelled: "bg-[#E4E6EA] text-[#3A3F47]" })[entry.status] || "bg-[#E4E6EA] text-[#3A3F47]"
const initials = (value) => {
	const parts = String(value || "").trim().split(/\s+/).filter(Boolean)
	if (!parts.length) return "?"
	return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase()
}

// ---- Client detail ----
const clientInfo = computed(() => {
	const c = client.data || {}
	return [
		{ label: "Phone", value: c.phone_number },
		{ label: "Age", value: c.age },
		{ label: "Sex", value: c.gender },
		{ label: "Institution", value: c.institution },
		{ label: "Counsellor", value: c.assigned_counsellor },
		{ label: "Referral source", value: joinParts([c.referral_source, c.referral_source_other], " — ") },
	]
})

const activeTab = ref("history")
const historyFilter = ref("all")
const history = computed(() => client.data?.case_history || [])
const baselineSurvey = computed(() => client.data?.baseline_survey || null)

const mainTabs = computed(() => [
	{ key: "history", label: "Case history", icon: ClipboardList, badge: history.value.length },
	{ key: "survey", label: "Baseline survey", icon: FileText, badge: baselineSurvey.value ? "Done" : "None" },
])

const summaryCards = computed(() => [
	{ label: "Total sessions", value: history.value.length, icon: Layers, tone: "bg-[#F4F5F7] text-[#62656D]" },
	{ label: "Completed", value: history.value.filter((e) => e.status === "Completed").length, icon: ClipboardCheck, tone: "bg-[#DCF3E4] text-[#146C3A]" },
	{ label: "Scheduled", value: history.value.filter((e) => e.status === "Scheduled" && !e.overdue).length, icon: CalendarClock, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
	{ label: "Overdue", value: history.value.filter((e) => e.overdue).length, icon: Ban, tone: "bg-[#FBE0E4] text-[#A10E24]" },
])

// ---- Baseline survey ----
const surveyValue = (value) => {
	if (Array.isArray(value)) return value.join(", ")
	if (typeof value === "string") {
		try {
			const parsed = JSON.parse(value)
			if (Array.isArray(parsed)) return parsed.join(", ")
		} catch {}
	}
	return value
}
const wellbeingScore = computed(() => {
	const n = Number(baselineSurvey.value?.wellbeing_self_rating)
	return Number.isFinite(n) && baselineSurvey.value?.wellbeing_self_rating ? n : null
})
const concernList = computed(() => {
	const raw = baselineSurvey.value?.main_concerns
	if (!raw) return []
	if (Array.isArray(raw)) return raw
	try {
		const parsed = JSON.parse(raw)
		if (Array.isArray(parsed)) return parsed
	} catch {}
	return String(raw).split(",").map((s) => s.trim()).filter(Boolean)
})
const yesNo = (value) => value === undefined || value === null || value === "" ? "" : (value ? "Yes" : "No")
const surveyGroups = computed(() => {
	const s = baselineSurvey.value || {}
	const groups = [
		{ title: "Coping & wellbeing", icon: HeartPulse, rows: [
			["Consent", s.consent],
			["Coping ability", s.coping_ability],
			["Coping behaviour", s.coping_behaviour === "Other" ? `Other: ${s.coping_behaviour_other || "Not specified"}` : s.coping_behaviour],
		] },
		{ title: "Support", icon: LifeBuoy, rows: [
			["Support available", s.support_availability],
			["Interested in support", yesNo(s.interest_in_support)],
			["Willing to follow up", yesNo(s.willingness_for_followup)],
			["Support that would be most helpful", s.preferred_support_type, true],
		] },
		{ title: "Background", icon: Home, rows: [
			["Marital status", s.marital_status],
			["Dependants", s.dependants],
			["Domestic situation", s.domestic_situation],
			["Conflict or disaster exposure", [s.conflict_exposure, s.exposure_details].filter(Boolean).join(": "), true],
		] },
	]
	return groups
		.map((group) => ({ ...group, rows: group.rows.filter(([, value]) => value !== undefined && value !== null && value !== "") }))
		.filter((group) => group.rows.length)
})

// ---- Case history ----
const historyTabs = computed(() => [
	{ key: "all", label: "All", count: history.value.length },
	{ key: "Completed", label: "Completed", count: history.value.filter((e) => e.status === "Completed").length },
	{ key: "Overdue", label: "Overdue", count: history.value.filter((e) => e.overdue).length },
	{ key: "Scheduled", label: "Scheduled", count: history.value.filter((e) => e.status === "Scheduled" && !e.overdue).length },
	{ key: "Cancelled", label: "Cancelled", count: history.value.filter((e) => e.status === "Cancelled").length },
])
const filteredHistory = computed(() => historyFilter.value === "all" ? history.value : historyFilter.value === "Overdue" ? history.value.filter((e) => e.overdue) : history.value.filter((e) => e.status === historyFilter.value && !e.overdue))
const hasBody = (entry) => entry.status === "Completed" || entry.referral_history?.length || entry.management_history?.length

const openEntries = ref(new Set())
const isOpen = (entry) => openEntries.value.has(entry.name)
function toggleEntry(name) {
	const next = new Set(openEntries.value)
	next.has(name) ? next.delete(name) : next.add(name)
	openEntries.value = next
}
const expandableIds = computed(() => filteredHistory.value.filter(hasBody).map((e) => e.name))
const allOpen = computed(() => expandableIds.value.length > 0 && expandableIds.value.every((id) => openEntries.value.has(id)))
function toggleAll() {
	openEntries.value = allOpen.value ? new Set() : new Set(expandableIds.value)
}

function entryDetails(entry) {
	const items = [
		{ label: "Mode", value: entry.mode_of_contact },
		{ label: "Presenting issues", value: issueText(entry.presenting_issues) },
		{ label: "Session details", value: entry.session_details, wide: true },
		{ label: "Interventions", value: entry.interventions_applied, wide: true },
		{ label: "Risk", value: joinParts([entry.urgency_level, entry.risk_assessment]), wide: true },
		{ label: "Follow-up", value: joinParts([entry.needs_follow_up, entry.follow_up_plan]), wide: true },
	]
	if (entry.session_type === "Follow-Up") {
		items.push(
			{ label: "Wellbeing", value: entry.followup_wellbeing_rating },
			{ label: "Stress frequency", value: entry.followup_stress_frequency },
			{ label: "Progress", value: entry.progress_previous_goals, wide: true },
			{ label: "Current concerns", value: entry.followup_new_issues, wide: true },
			{ label: "Coping and support", value: entry.followup_coping_support, wide: true },
			{ label: "Next steps", value: joinParts([entry.followup_recommendations, entry.followup_takeaways, entry.next_session_focus], " "), wide: true },
		)
	}
	return items
}

// ---- Counsellor management ----
const term = ref("")
const status = ref("")
const statusMenuOpen = ref(false)
const statusOptions = [
	{ label: "All statuses", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Inactive", value: "Inactive" },
]
const selectedStatus = computed(() => statusOptions.find((option) => option.value === status.value) || statusOptions[0])
const chooseStatus = (value) => {
	status.value = value
	statusMenuOpen.value = false
}
const searching = computed(() => term.value.trim().length > 0)
const allRows = computed(() => counsellors.data || [])
const rows = computed(() => {
	const q = term.value.trim().toLowerCase()
	return allRows.value.filter((row) => {
		if (status.value === "Active" && !row.enabled) return false
		if (status.value === "Inactive" && row.enabled) return false
		if (!q) return true
		return [row.full_name, row.name].some((value) => (value || "").toLowerCase().includes(q))
	})
})

function onOutsideClick(event) {
	if (!event.target.closest('[aria-haspopup="listbox"]') && !event.target.closest('[role="listbox"]')) statusMenuOpen.value = false
}
onMounted(() => document.addEventListener("click", onOutsideClick))
onUnmounted(() => document.removeEventListener("click", onOutsideClick))

function load() {
	if (kind.value === "client") {
		activeTab.value = "history"
		historyFilter.value = "all"
		openEntries.value = new Set()
		client.submit({ name: route.params.name })
	}
	if (kind.value === "counsellors") counsellors.submit()
}
watch([kind, () => route.params.name], load, { immediate: true })

function createCounsellor() { saveUser.submit({ ...newUser, action: "create" }) }
function retireCounsellor(row, action) {
	if (window.confirm(`${action === "deactivate" ? "Deactivate" : "Remove"} ${row.full_name}? Their history will remain available.`)) saveUser.submit({ user: row.name, action })
}
</script>

<style scoped>
.field { display: block; min-height: 44px; width: 100%; border: 1px solid #d9dbe0; border-radius: 10px; background: #fff; padding: 10px 12px; font-family: inherit; font-size: 14px; line-height: 20px; color: #33353a; transition: border-color 0.15s, box-shadow 0.15s; }
.field::placeholder { color: #a0a2a8; }
.field:hover { border-color: #bfc2c8; }
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }

.primary, .secondary { display: inline-flex; min-height: 42px; align-items: center; justify-content: center; border-radius: 10px; padding: 0 18px; font-size: 14px; font-weight: 600; transition: background 0.15s, border-color 0.15s; }
.primary { background: #c8102e; color: #fff; }
.primary:hover:not(:disabled) { background: #a10e24; }
.primary:disabled { opacity: 0.6; cursor: wait; }
.secondary { border: 1px solid #d9dbe0; background: #fff; color: #33353a; }
.secondary:hover { background: #f7f7f8; }
</style>
