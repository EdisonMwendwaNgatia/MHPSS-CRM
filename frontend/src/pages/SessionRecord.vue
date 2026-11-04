<template>
	<main class="mx-auto max-w-7xl px-4 py-6 md:px-7 md:py-8">
		<PageLoader v-if="resource.loading && !resource.data" />

		<template v-else-if="record">
			<!-- Breadcrumb -->
			<div class="mb-5 text-sm text-[#5B616B]">
				<router-link :to="{ name: 'Clients' }" class="hover:text-[#A10E24]">Clients</router-link>
				<span class="px-2">/</span>
				<router-link v-if="record.client_id" :to="{ name: 'ClientProfile', params: { name: record.client_id } }" class="hover:text-[#A10E24]">{{ record.scholar_code || 'Client' }}</router-link>
				<span v-else>{{ record.scholar_code || 'Client' }}</span>
				<span class="px-2">/</span><span class="font-semibold text-[#2B2F36]">{{ isReadOnly ? 'Session Record' : 'In-session Record' }}</span>
			</div>

			<!-- Page header -->
			<div class="mb-5 flex flex-wrap items-start justify-between gap-4">
				<div>
					<h1 class="text-2xl font-semibold leading-8 text-[#2B2F36]">{{ isReadOnly ? 'Session Record' : 'In-session Record' }}</h1>
					<p class="mt-1 text-sm text-[#5B616B]">
						{{ record.scholar_code }} · {{ record.client_name }} · {{ fmtDateTime(record.date_time) }}
					</p>
				</div>
				<div class="flex items-center gap-2 rounded-lg border border-[#E4E6EA] bg-white px-3 py-2 text-sm text-[#5B616B]">
					<FileText :size="16" class="shrink-0" />
					{{ record.session_type }} · {{ record.name }}
				</div>
			</div>

			<!-- Session status banner -->
			<section class="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#E4E6EA] bg-white px-5 py-4" aria-label="Session status">
				<div class="text-sm text-[#2B2F36]">
					<strong class="mr-1">Session:</strong><span>{{ banner.text }}</span>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" :class="banner.pill">{{ banner.label }}</span>
			</section>

			<div class="flex items-start gap-5 max-[800px]:flex-col">
				<!-- Section navigation -->
				<nav v-if="sections.length > 1" class="w-[280px] shrink-0 rounded-xl border border-[#E4E6EA] bg-white p-5 max-[800px]:w-full" aria-label="Record sections">
					<div class="mb-2 text-xs text-[#5B616B]">Section {{ step }} of {{ sections.length }} · {{ Math.round((step / sections.length) * 100) }}% complete</div>
					<div class="mb-4 h-2 overflow-hidden rounded-full bg-[#E4E6EA]">
						<div class="h-full rounded-full bg-[#C8102E] transition-all" :style="{ width: `${(step / sections.length) * 100}%` }"></div>
					</div>
					<ol class="space-y-1">
						<li v-for="(section, index) in sections" :key="section.key">
							<button type="button" class="flex min-h-10 w-full items-center gap-2.5 rounded-lg px-2 text-left text-sm transition-colors"
								:class="step === index + 1 ? 'font-semibold text-[#A10E24]' : 'text-[#4A505A] hover:bg-[#F4F5F7]'"
								:aria-current="step === index + 1 ? 'step' : undefined" @click="goTo(index + 1)">
								<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
									:class="isDone(section, index) ? 'bg-[#DCF3E4] text-[#146C3A]' : step === index + 1 ? 'bg-[#C8102E] text-white' : 'bg-[#E4E6EA] text-[#3A3F47]'">
									<Check v-if="isDone(section, index)" :size="14" :stroke-width="2.5" />
									<template v-else>{{ index + 1 }}</template>
								</span>
								{{ section.title }}
							</button>
						</li>
					</ol>
				</nav>

				<!-- Section content -->
				<form class="min-w-0 flex-1 rounded-xl border border-[#E4E6EA] bg-white p-5 md:p-6" @submit.prevent="onSubmit">
					<h2 class="text-lg font-semibold text-[#2B2F36]">{{ currentSection.heading }}</h2>
					<p v-if="currentSection.description" class="mb-6 mt-1 text-sm text-[#5B616B]">{{ currentSection.description }}</p>

					<fieldset :disabled="!canSave" class="m-0 min-w-0 border-0 p-0">
						<!-- Case history -->
						<div v-if="currentSection.key === 'history'">
							<ol v-if="history.length" class="divide-y divide-[#E4E6EA] overflow-hidden rounded-xl border border-[#E4E6EA]">
								<li v-for="item in history" :key="item.name">
									<details v-if="item.status === 'Completed'" class="hist" :open="item.name === latestName">
										<summary class="hist-summary flex cursor-pointer items-center gap-3 px-4 py-3.5 transition hover:bg-[#F4F5F7]">
											<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#DCF3E4] text-[#146C3A]"><ClipboardCheck :size="17" /></span>
											<span class="min-w-0 flex-1">
												<span class="block text-sm font-semibold text-[#2B2F36]">{{ fmtDateTime(item.date_time) }}</span>
												<span class="mt-0.5 block text-xs text-[#5B616B]">{{ item.session_type }}<span v-if="item.mode_of_contact"> · {{ item.mode_of_contact }}</span></span>
											</span>
											<Badge label="Completed" theme="green" />
											<ChevronDown :size="17" class="hist-chev shrink-0 text-[#5B616B]" />
										</summary>

										<div class="space-y-3 px-4 pb-4 pt-1">
											<div class="grid gap-3 sm:grid-cols-2">
												<div v-for="[label, value, wide] in facts(item)" :key="label" class="rounded-lg bg-[#F4F5F7] p-4" :class="wide ? 'sm:col-span-2' : ''">
													<span class="block text-xs text-[#5B616B]">{{ label }}</span>
													<span class="fact-value mt-1 block text-sm font-medium text-[#2B2F36]">{{ value || 'Not recorded' }}</span>
												</div>
											</div>

											<template v-if="item.session_type === 'Follow-Up'">
												<div v-for="group in followupGroups(item)" :key="group.title" class="rounded-xl border border-[#E4E6EA] p-4">
													<h3 class="text-sm font-semibold text-[#2B2F36]">{{ group.title }}</h3>
													<div class="mt-3 grid gap-3 sm:grid-cols-2">
												<div v-for="[label, value] in group.rows" :key="label" class="rounded-lg bg-[#F4F5F7] p-4">
															<span class="block text-xs text-[#5B616B]">{{ label }}</span>
															<span class="fact-value mt-1 block text-sm font-medium text-[#2B2F36]">{{ value || 'Not recorded' }}</span>
														</div>
													</div>
												</div>
											</template>

											<div v-if="item.audio_recording" class="rounded-lg bg-[#F4F5F7] p-4">
												<span class="mb-2 block text-xs text-[#5B616B]">Session audio</span>
												<audio controls preload="none" class="w-full max-w-xl" :src="item.audio_recording">Your browser does not support audio playback.</audio>
											</div>

											<div v-if="item.referral_history?.length" class="space-y-2 rounded-lg bg-[#E0EAFD] px-4 py-3">
												<p v-for="referral in item.referral_history" :key="referral.name || referral.referred_on" class="text-xs leading-5 text-[#1B4DB1]">
													<span class="font-semibold">Referral:</span> {{ referral.from_name || referral.from_counsellor }} → {{ referral.to_name || referral.to_counsellor }} · {{ fmtDateTime(referral.referred_on) }}. {{ referral.reason }}
												</p>
											</div>
										</div>
									</details>

									<div v-else class="flex items-center gap-3 px-4 py-3.5">
										<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full" :class="item.status === 'Cancelled' ? 'bg-[#F4F5F7] text-[#5B616B]' : item.overdue ? 'bg-[#FBE0E4] text-[#A10E24]' : 'bg-[#E0EAFD] text-[#1B4DB1]'">
											<Ban v-if="item.status === 'Cancelled'" :size="17" /><CalendarClock v-else :size="17" />
										</span>
										<span class="min-w-0 flex-1">
											<span class="block text-sm font-semibold text-[#2B2F36]">{{ fmtDateTime(item.date_time) }}</span>
											<span class="mt-0.5 block text-xs text-[#5B616B]">{{ item.session_type }}<span v-if="item.mode_of_contact"> · {{ item.mode_of_contact }}</span> · {{ item.status === 'Scheduled' ? 'Session is scheduled.' : 'Session was cancelled.' }}</span>
										</span>
										<Badge :label="item.status === 'Scheduled' && item.overdue ? 'Overdue' : item.status" :theme="item.overdue ? 'red' : item.status === 'Cancelled' ? 'gray' : 'blue'" />
									</div>
									<div v-if="item.status !== 'Completed' && item.referral_history?.length" class="space-y-2 px-4 pb-4">
										<p v-for="referral in item.referral_history" :key="referral.name || referral.referred_on" class="rounded-lg bg-[#E0EAFD] px-4 py-3 text-xs leading-5 text-[#1B4DB1]">
											<span class="font-semibold">Referral:</span> {{ referral.from_name || referral.from_counsellor }} → {{ referral.to_name || referral.to_counsellor }} · {{ fmtDateTime(referral.referred_on) }}. {{ referral.reason }}
										</p>
									</div>
								</li>
							</ol>
							<p v-else class="rounded-lg bg-[#F4F5F7] p-4 text-sm text-[#5B616B]">No earlier sessions are recorded for this client.</p>
						</div>

						<!-- Follow-up counseling mode -->
						<div v-else-if="currentSection.key === 'mode'" class="max-w-2xl">
							<label id="mode-of-counseling-label" class="lbl">Mode of counselling <span class="req" aria-hidden="true">*</span></label>
							<div class="relative" data-mode-dropdown>
								<button type="button" class="field flex items-center justify-between gap-3 text-left" :class="form.mode_of_contact ? '' : 'is-empty'" aria-labelledby="mode-of-counseling-label mode-of-counseling-value" :aria-expanded="modeDropdownOpen" aria-haspopup="listbox" :disabled="!canSave" @click="modeDropdownOpen = !modeDropdownOpen" @keydown.esc="modeDropdownOpen = false">
									<span id="mode-of-counseling-value" class="truncate">{{ form.mode_of_contact || 'Select mode of counselling' }}</span>
									<ChevronDown :size="17" class="shrink-0 text-[#5B616B] transition-transform" :class="modeDropdownOpen ? 'rotate-180' : ''" />
								</button>
								<div v-if="modeDropdownOpen" class="issue-menu" role="listbox" aria-labelledby="mode-of-counseling-label">
									<button v-for="option in activeCounselingModes" :key="option" type="button" role="option" class="issue-option" :class="form.mode_of_contact === option ? 'issue-option-active' : ''" :aria-selected="form.mode_of_contact === option" @click="chooseCounselingMode(option)">{{ option }}<Check v-if="form.mode_of_contact === option" :size="16" /></button>
								</div>
							</div>
						</div>

						<!-- Mood summary since the previous session -->
						<div v-else-if="currentSection.key === 'mood'" class="max-w-2xl">
							<label class="lbl" for="f-session_details">How has the client been feeling since the last session? <span class="req" aria-hidden="true">*</span></label>
							<p class="mb-2 text-xs text-[#5B616B]">Brief summary of mood, behavior, or attitude.</p>
							<textarea id="f-session_details" v-model="form.session_details" class="field" rows="5" />
							<div class="mt-5"><label class="lbl" for="f-followup_wellbeing_rating">How would you rate your current emotional and psychological wellbeing? <span class="req" aria-hidden="true">*</span></label><select id="f-followup_wellbeing_rating" v-model="form.followup_wellbeing_rating" class="field"><option value="">Choose a rating</option><option v-for="option in wellbeingOptions" :key="option">{{ option }}</option></select></div>
							<div class="mt-5"><label class="lbl" for="f-followup_stress_frequency">In the past two weeks, have you experienced significant stress, anxiety, low mood, or difficulty concentrating? <span class="req" aria-hidden="true">*</span></label><select id="f-followup_stress_frequency" v-model="form.followup_stress_frequency" class="field"><option value="">Choose an answer</option><option v-for="option in stressFrequencyOptions" :key="option">{{ option }}</option></select></div>
						</div>

						<!-- Presenting issues -->
						<div v-else-if="currentSection.key === 'presenting'" class="max-w-2xl space-y-5">
							<fieldset v-if="isFollowUp" class="m-0 border-0 p-0">
								<legend class="lbl">Are there any new presenting issues? <span class="req" aria-hidden="true">*</span></legend>
								<div class="mb-4 grid gap-2 sm:grid-cols-2"><label v-for="answer in yesNoOptions" :key="answer" class="opt" :class="form.followup_new_presenting_issues === answer ? 'opt-on' : ''"><input type="radio" name="followup_new_presenting_issues" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="form.followup_new_presenting_issues === answer" @change="setNewPresentingAnswer(answer)" />{{ answer }}</label></div>
							</fieldset>
							<fieldset v-if="!isFollowUp || form.followup_new_presenting_issues === 'Yes'" class="m-0 border-0 p-0">
								<legend class="lbl">{{ isFollowUp ? 'Select new presenting issues' : 'Presenting issues' }} <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="issue in presentingIssueTypes" :key="issue" class="opt" :class="selectedPresentingIssues.includes(issue) ? 'opt-on' : ''"><input type="checkbox" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="selectedPresentingIssues.includes(issue)" @change="togglePresentingIssue(issue, $event.target.checked)" />{{ issue }}</label>
								</div>
							</fieldset>
							<div><label class="lbl" for="f-issue_subclassifications">Issue subclassifications</label><textarea id="f-issue_subclassifications" v-model="form.issue_subclassifications" class="field" rows="3" placeholder="Add relevant categories or descriptors" /></div>
							<div v-if="!isFollowUp"><label class="lbl" for="f-session_details">Session details<span class="req" aria-hidden="true"> *</span></label><textarea id="f-session_details" v-model="form.session_details" class="field" rows="5" /></div>
						</div>

						<!-- Interventions -->
						<div v-else-if="currentSection.key === 'interventions'" class="max-w-2xl space-y-5">
							<div><label class="lbl" for="f-interventions_applied">Interventions applied<span class="req" aria-hidden="true"> *</span></label><textarea id="f-interventions_applied" v-model="form.interventions_applied" class="field" rows="5" /></div>
							<div><label class="lbl" for="f-referrals_made">Referrals made</label><textarea id="f-referrals_made" v-model="form.referrals_made" class="field" rows="4" placeholder="Enter referral or write None" /></div>
						</div>

						<!-- Urgency and risk -->
						<div v-else-if="currentSection.key === 'urgency'" class="max-w-2xl space-y-6">
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Urgency level <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="level in urgencyLevels" :key="level" class="opt" :class="form.urgency_level === level ? 'opt-on' : ''">
										<input v-model="form.urgency_level" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="urgency_level" :value="level" />{{ level }}
									</label>
								</div>
							</fieldset>
							<div><label class="lbl" for="f-risk_assessment">Risk assessment<span class="req" aria-hidden="true"> *</span></label><textarea id="f-risk_assessment" v-model="form.risk_assessment" class="field" rows="5" /></div>
						</div>

						<!-- Follow-up plan -->
						<div v-else-if="currentSection.key === 'plan'" class="max-w-2xl">
							<fieldset class="mb-5 m-0 border-0 p-0"><legend class="lbl">Is there a need for follow-up? <span class="req" aria-hidden="true">*</span></legend><div class="grid gap-2 sm:grid-cols-2"><label v-for="answer in yesNoOptions" :key="answer" class="opt" :class="form.needs_follow_up === answer ? 'opt-on' : ''"><input type="radio" name="needs_follow_up" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="form.needs_follow_up === answer" @change="setNeedFollowUp(answer)" />{{ answer }}</label></div></fieldset>
							<div v-if="form.needs_follow_up === 'Yes'"><label class="lbl" for="f-follow_up_plan">Follow-up plan<span class="req" aria-hidden="true"> *</span></label><textarea id="f-follow_up_plan" v-model="form.follow_up_plan" class="field" rows="6" /></div>
							<p v-else-if="form.needs_follow_up === 'No'" class="rounded-lg bg-[#F4F5F7] p-3 text-sm text-[#5B616B]">The case will be closed when this session is saved.</p>
						</div>

						<!-- Follow-Up review sections -->
						<div v-else-if="currentSection.key === 'progress'" class="max-w-2xl space-y-5">
							<div><label class="lbl" for="f-followup_goals_discussed">Goals/issues discussed last time</label><textarea id="f-followup_goals_discussed" v-model="form.followup_goals_discussed" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-progress_previous_goals">What progress or changes has the student made?</label><textarea id="f-progress_previous_goals" v-model="form.progress_previous_goals" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_challenges">Any challenges or setbacks noted?</label><textarea id="f-followup_challenges" v-model="form.followup_challenges" class="field" rows="3" /></div>
						</div>
						<div v-else-if="currentSection.key === 'concerns'" class="max-w-2xl space-y-5">
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Any new issues or stressors? <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2"><label v-for="answer in yesNoOptions" :key="answer" class="opt" :class="form.followup_new_issues_present === answer ? 'opt-on' : ''"><input type="radio" name="followup_new_issues_present" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="form.followup_new_issues_present === answer" @change="setFollowupAnswer('followup_new_issues_present', 'followup_new_issues', answer)" />{{ answer }}</label></div>
							</fieldset>
							<div v-if="form.followup_new_issues_present === 'Yes'"><label class="lbl" for="f-followup_new_issues">Describe the new issue or stressor <span class="req" aria-hidden="true">*</span></label><textarea id="f-followup_new_issues" v-model="form.followup_new_issues" class="field" rows="3" /></div>
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Any evident changes? <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2"><label v-for="answer in yesNoOptions" :key="answer" class="opt" :class="form.followup_evident_changes_present === answer ? 'opt-on' : ''"><input type="radio" name="followup_evident_changes_present" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="form.followup_evident_changes_present === answer" @change="setFollowupAnswer('followup_evident_changes_present', 'followup_evident_changes', answer)" />{{ answer }}</label></div>
							</fieldset>
							<div v-if="form.followup_evident_changes_present === 'Yes'"><label class="lbl" for="f-followup_evident_changes">Describe evident changes <span class="req" aria-hidden="true">*</span></label><textarea id="f-followup_evident_changes" v-model="form.followup_evident_changes" class="field" rows="3" /></div>
						</div>
						<div v-else-if="currentSection.key === 'coping'" class="max-w-2xl space-y-5">
							<div><label class="lbl" for="f-followup_coping_support">What coping skills or supports is the client using?</label><textarea id="f-followup_coping_support" v-model="form.followup_coping_support" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_support_effectiveness">How effective do they seem?</label><textarea id="f-followup_support_effectiveness" v-model="form.followup_support_effectiveness" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_additional_support">Any additional support needed?</label><textarea id="f-followup_additional_support" v-model="form.followup_additional_support" class="field" rows="3" /></div>
						</div>
						<div v-else-if="currentSection.key === 'observation'" class="max-w-2xl space-y-6">
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Mood and affect <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="option in moodAffectOptions" :key="option" class="opt" :class="form.followup_mood_affect === option ? 'opt-on' : ''">
										<input v-model="form.followup_mood_affect" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="followup_mood_affect" :value="option" />{{ option }}
									</label>
								</div>
							</fieldset>
							<div v-if="form.followup_mood_affect === 'Other'"><label class="lbl" for="f-followup_mood_other">Describe other mood or affect</label><textarea id="f-followup_mood_other" v-model="form.followup_mood_other" class="field" rows="3" /></div>
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Engagement level <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="option in engagementLevels" :key="option" class="opt" :class="form.followup_engagement_level === option ? 'opt-on' : ''">
										<input v-model="form.followup_engagement_level" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="followup_engagement_level" :value="option" />{{ option }}
									</label>
								</div>
							</fieldset>
							<fieldset class="m-0 border-0 p-0">
								<legend class="lbl">Risk concerns <span class="req" aria-hidden="true">*</span></legend>
								<div class="grid gap-2 sm:grid-cols-2">
									<label v-for="option in followupRiskLevels" :key="option" class="opt" :class="form.followup_risk_concerns === option ? 'opt-on' : ''">
										<input v-model="form.followup_risk_concerns" class="h-[18px] w-[18px] accent-[#C8102E]" type="radio" name="followup_risk_concerns" :value="option" />{{ option }}
									</label>
								</div>
							</fieldset>
						</div>
						<div v-else-if="currentSection.key === 'nextsteps'" class="max-w-2xl space-y-5">
							<fieldset class="m-0 border-0 p-0"><legend class="lbl">Is there a need for follow-up? <span class="req" aria-hidden="true">*</span></legend><div class="grid gap-2 sm:grid-cols-2"><label v-for="answer in yesNoOptions" :key="answer" class="opt" :class="form.needs_follow_up === answer ? 'opt-on' : ''"><input type="radio" name="needs_follow_up_followup" class="h-[18px] w-[18px] accent-[#C8102E]" :checked="form.needs_follow_up === answer" @change="setNeedFollowUp(answer)" />{{ answer }}</label></div></fieldset>
							<div v-if="form.needs_follow_up === 'Yes'"><label class="lbl" for="f-follow_up_plan">Follow-up plan <span class="req" aria-hidden="true">*</span></label><textarea id="f-follow_up_plan" v-model="form.follow_up_plan" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_recommendations">Recommendations</label><textarea id="f-followup_recommendations" v-model="form.followup_recommendations" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_takeaways">Key takeaways or interventions used today <span class="req" aria-hidden="true">*</span></label><textarea id="f-followup_takeaways" v-model="form.followup_takeaways" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-referrals_made">Referrals made</label><textarea id="f-referrals_made" v-model="form.referrals_made" class="field" rows="3" placeholder="Enter referral or write None" /></div>
							<div><label class="lbl" for="f-next_session_focus">Focus for next session</label><textarea id="f-next_session_focus" v-model="form.next_session_focus" class="field" rows="3" /></div>
							<div><label class="lbl" for="f-followup_action">Follow-up action (if any)</label><textarea id="f-followup_action" v-model="form.followup_action" class="field" rows="3" /></div>
						</div>

						<!-- Session audio -->
						<div v-else-if="currentSection.key === 'audio'" class="max-w-xl">
							<div v-if="audioUrl" class="rounded-lg bg-[#F4F5F7] p-4">
								<audio controls preload="none" class="w-full" :src="audioUrl">Your browser does not support audio playback.</audio>
							</div>
							<p v-else-if="!canSave" class="rounded-lg bg-[#F4F5F7] p-4 text-sm text-[#5B616B]">No audio was recorded for this session.</p>

							<FileUploader v-if="canSave" :class="audioUrl ? 'mt-4' : ''" :fileTypes="['audio/*']" :validateFile="validateAudio" :uploadArgs="audioUploadArgs" @success="onAudioUploaded">
								<template #default="{ uploading, progress, openFileSelector, error }">
									<button type="button" :disabled="uploading" class="inline-flex h-11 items-center gap-2 rounded-[10px] border border-[#D5D8DE] bg-white px-5 text-sm font-semibold text-[#2B2F36] transition hover:bg-[#F4F5F7] disabled:cursor-wait disabled:opacity-60" @click="openFileSelector">
										<Loader2 v-if="uploading" :size="16" class="animate-spin" />
										<Upload v-else :size="16" />
										{{ uploading ? `Uploading ${progress}%` : audioUrl ? 'Replace audio file' : 'Upload audio file' }}
									</button>
									<p v-if="error" class="mt-2 text-sm text-[#A10E24]">{{ error }}</p>
								</template>
							</FileUploader>
						</div>
					</fieldset>

					<p v-if="formError" class="mt-5 text-sm text-[#A10E24]" role="alert">{{ formError }}</p>
					<ErrorMessage class="mt-5" :message="saver.error" />
					<p v-if="canSave && step === sections.length" class="mt-5 text-xs text-[#5B616B]">Once saved, the session record is locked and becomes read-only.</p>

					<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E4E6EA] pt-5">
						<Button v-if="sections.length > 1" type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#2B2F36]" :disabled="step === 1" @click="previous">Previous</Button>
						<span v-else></span>

						<router-link v-if="!canSave && step === sections.length" :to="backTo" class="inline-flex h-11 items-center rounded-[10px] bg-[#C8102E] px-5 text-sm font-semibold text-white transition hover:bg-[#A10E24]">Back</router-link>
						<Button v-else type="submit" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="saver.loading">
							{{ canSave && step === sections.length ? 'Save session record' : 'Next' }}
						</Button>
					</div>
				</form>
			</div>
		</template>

		<ErrorMessage v-else :message="resource.error" />
	</main>
</template>

<script setup>
import { createResource, FileUploader } from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Ban, CalendarClock, Check, ChevronDown, ClipboardCheck, FileText, Loader2, Upload } from "lucide-vue-next"
import { fmtDateTime } from "../data/format"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const name = computed(() => props.name || route.params.name || "")
const urgencyLevels = ["Low", "Moderate", "High", "Immediate"]
const moodAffectOptions = ["Stable", "Improved", "Low", "Anxious", "Withdrawn", "Other"]
const engagementLevels = ["Active", "Moderate", "Passive"]
const followupRiskLevels = ["None", "Mild", "Moderate", "High"]
const followUpCounselingModes = ["Physical Individual", "Tele-counselling"]
const firstSessionCounselingModes = ["Tele counselling Session", "Physical Session"]
const yesNoOptions = ["Yes", "No"]
const wellbeingOptions = ["Very good", "Good", "Fair", "Poor", "Very poor"]
const stressFrequencyOptions = ["Never", "Sometimes", "Often", "Almost always"]
const presentingIssueTypes = [
	"Substance-Related and Addictive Disorders",
	"Anxiety Disorders",
	"Trauma and Stressor-Related Disorders",
	"GBV / safeguarding issues",
	"Depressive Disorders",
	"Other Presenting Issues",
]
function presentingText(value) {
	if (!value) return ""
	try {
		const parsed = JSON.parse(value)
		return Array.isArray(parsed) ? parsed.join(", ") : String(parsed)
	} catch { return value }
}
const modeDropdownOpen = ref(false)
const recordFields = [
	"mode_of_contact", "session_details", "presenting_issues", "issue_subclassifications", "interventions_applied", "referrals_made",
	"urgency_level", "risk_assessment", "needs_follow_up", "follow_up_plan", "progress_previous_goals", "followup_goals_discussed",
	"followup_challenges", "followup_new_issues_present", "followup_new_issues", "followup_new_presenting_issues", "followup_evident_changes_present", "followup_evident_changes", "followup_coping_support",
	"followup_support_effectiveness", "followup_additional_support", "followup_mood_affect", "followup_mood_other", "followup_wellbeing_rating", "followup_stress_frequency",
	"followup_engagement_level", "followup_risk_concerns", "counsellor_observations", "followup_recommendations",
	"followup_takeaways", "next_session_focus", "followup_action",
]
const form = reactive({
	mode_of_contact: "", session_details: "", presenting_issues: "", issue_subclassifications: "", interventions_applied: "", needs_follow_up: "",
	referrals_made: "", urgency_level: "", risk_assessment: "", follow_up_plan: "",
	progress_previous_goals: "", followup_goals_discussed: "", followup_challenges: "", followup_new_issues_present: "",
	followup_new_issues: "", followup_new_presenting_issues: "", followup_evident_changes_present: "", followup_evident_changes: "", followup_coping_support: "", followup_support_effectiveness: "",
	followup_additional_support: "", followup_mood_affect: "", followup_mood_other: "", followup_wellbeing_rating: "", followup_stress_frequency: "", followup_engagement_level: "",
	followup_risk_concerns: "", counsellor_observations: "", followup_recommendations: "", followup_takeaways: "",
	next_session_focus: "", followup_action: "",
})
const uploadedAudio = ref("")
const audioUrl = computed(() => uploadedAudio.value || record.value?.audio_recording || "")
const audioUploadArgs = computed(() => ({
	doctype: "Appointment",
	docname: name.value,
	fieldname: "audio_recording",
	private: true,
}))
const resource = createResource({
	url: "krcti_mhpss.api.records.session_record_detail",
	onSuccess(data) {
		for (const field of recordFields) form[field] = data.appointment[field] ?? ""
		if (data.appointment.status === "Scheduled" && !activeCounselingModes.value.includes(form.mode_of_contact)) form.mode_of_contact = ""
	},
})
const record = computed(() => resource.data?.appointment)
const isFollowUp = computed(() => record.value?.session_type === "Follow-Up")
const isTermination = computed(() => record.value?.session_type === "Termination")
const activeCounselingModes = computed(() => isFollowUp.value ? followUpCounselingModes : firstSessionCounselingModes)
const selectedPresentingIssues = computed(() => {
	try {
		const parsed = JSON.parse(form.presenting_issues || "[]")
		if (Array.isArray(parsed)) return parsed
	} catch { if (form.presenting_issues) return [form.presenting_issues] }
	return []
})
const history = computed(() => resource.data?.history || [])
const caseClosed = computed(() => resource.data?.case_status === "Closed")
const canManage = computed(() => resource.data?.can_manage === true)
const isReadOnly = computed(() => record.value?.status === "Completed" || record.value?.status === "Cancelled" || caseClosed.value || !canManage.value)
const showForm = computed(() => record.value?.status === "Completed" || (!caseClosed.value && record.value?.status === "Scheduled" && canManage.value))
const canSave = computed(() => showForm.value && !isReadOnly.value)
const backTo = computed(() => !canManage.value
	? { name: "ClientProfile", params: { name: record.value?.client_id } }
	: record.value?.status === "Completed"
		? { name: "SessionRecords" }
	: record.value?.status === "Scheduled" && record.value?.session_type === "Follow-Up"
		? { name: "FollowUps" }
		: { name: "Appointments" })
onMounted(() => resource.submit({ name: name.value }))
function closeIssueDropdown(event) {
	if (!event.target.closest("[data-mode-dropdown]")) modeDropdownOpen.value = false
}
onMounted(() => document.addEventListener("click", closeIssueDropdown))
onUnmounted(() => document.removeEventListener("click", closeIssueDropdown))
function togglePresentingIssue(issue, selected) {
	const values = new Set(selectedPresentingIssues.value)
	selected ? values.add(issue) : values.delete(issue)
	form.presenting_issues = JSON.stringify([...values])
}
function setNewPresentingAnswer(answer) {
	form.followup_new_presenting_issues = answer
	if (answer === "No") form.presenting_issues = ""
}
function setNeedFollowUp(answer) {
	form.needs_follow_up = answer
	if (answer === "No") form.follow_up_plan = ""
}
function chooseCounselingMode(mode) {
	form.mode_of_contact = mode
	modeDropdownOpen.value = false
}
function setFollowupAnswer(answerField, detailField, answer) {
	form[answerField] = answer
	if (answer === "No") form[detailField] = ""
}

const saver = createResource({
	url: "krcti_mhpss.api.records.record_session",
	onSuccess() { router.replace({ name: "SessionRecords" }) },
})
function save() {
	saver.submit({ name: name.value, data: Object.fromEntries(recordFields.map((field) => [field, form[field]])) })
}
function onAudioUploaded(file) {
	uploadedAudio.value = file?.file_url || ""
}
function validateAudio(file) {
	return file.type?.startsWith("audio/") ? "" : "Choose an audio file."
}

// ---- Wizard ----
const step = ref(1)
const formError = ref("")
const visited = ref(new Set([1]))

// Fields that must be filled before the record can be saved, per section
const REQUIRED = {
	mode: ["mode_of_contact"],
	mood: ["session_details", "followup_wellbeing_rating", "followup_stress_frequency"],
	presenting: ["session_details"],
	interventions: ["interventions_applied"],
	urgency: ["urgency_level", "risk_assessment"],
	plan: ["needs_follow_up"],
	nextsteps: ["needs_follow_up", "followup_takeaways"],
	observation: ["followup_mood_affect", "followup_engagement_level", "followup_risk_concerns"],
}

const sections = computed(() => {
	const client = record.value?.client_name || "this client"
	const list = [
		{ key: "history", title: "Case history", heading: "Case history", description: `Chronological history for ${client}. Review earlier sessions before recording this one.` },
	]
	if (showForm.value) {
		if (isFollowUp.value) {
			list.push(
				{ key: "mode", title: "Mode of counseling", heading: "Mode of counseling", description: "Choose how this counseling session is being held." },
				{ key: "mood", title: "Feeling since last session", heading: "How has the client been feeling since the last session?", description: "Briefly summarize the client’s mood, behavior, or attitude." },
				{ key: "progress", title: "Progress on goals", heading: "Progress on previous goals", description: "This entry will be added to the client’s chronological case history." },
				{ key: "concerns", title: "Current concerns", heading: "Current concerns / new issues", description: "Record any new issues and changes since the last session." },
				{ key: "coping", title: "Coping and support", heading: "Coping and support", description: "Record what is helping the client and what else they need." },
				{ key: "observation", title: "Observation", heading: "Counsellor’s observation", description: "Record mood, engagement and risk concerns." },
				{ key: "presenting", title: "Presenting issues", heading: "Presenting issues", description: "Select the issues discussed in this follow-up." },
				{ key: "urgency", title: "Urgency and risk", heading: "Urgency and risk", description: "Record how urgent the case is and the risk assessment." },
				{ key: "nextsteps", title: "Next steps", heading: "Next steps / plan", description: "Record recommendations and the focus for next time." },
			)
		} else {
			list.push(
				{ key: "mode", title: "Mode of counselling", heading: "Mode of counselling", description: "Choose how this first counselling session is being held." },
				{ key: "presenting", title: "Presenting issues", heading: "Presenting issues", description: "Record what brought the client in and what was discussed." },
				{ key: "interventions", title: "Interventions", heading: "Interventions", description: "Record the support given and any referrals made." },
				{ key: "urgency", title: "Urgency and risk", heading: "Urgency and risk", description: "Record how urgent the case is and the risk assessment." },
			)
			if (!isTermination.value) {
				list.push({ key: "plan", title: "Follow-up plan", heading: "Follow-up plan", description: "Record what happens next for this client." })
			}
		}
		list.push({ key: "audio", title: "Session audio", heading: "Session audio (optional)", description: "Upload an audio recording if one is available. The file is stored privately with this session." })
	}
	return list.map((section, index) => ({ ...section, heading: index === 0 ? section.heading : `Section ${index + 1}: ${section.heading}` }))
})
const currentSection = computed(() => sections.value[Math.min(step.value, sections.value.length) - 1] || sections.value[0])

watch(step, (value) => {
	visited.value = new Set([...visited.value, value])
	formError.value = ""
})

const sectionComplete = (section) => {
	if (section.key === "concerns") {
		return [
			form.followup_new_issues_present,
			form.followup_evident_changes_present,
			form.followup_new_issues_present !== "Yes" || form.followup_new_issues.trim(),
			form.followup_evident_changes_present !== "Yes" || form.followup_evident_changes.trim(),
		].every(Boolean)
	}
	if (section.key === "plan" || section.key === "nextsteps") {
		return Boolean(form.needs_follow_up) && (form.needs_follow_up === "No" || Boolean(form.follow_up_plan.trim())) &&
			(section.key !== "nextsteps" || Boolean(form.followup_takeaways.trim()))
	}
	const required = REQUIRED[section.key] || []
	if (section.key === "presenting") return isFollowUp.value
		? Boolean(form.followup_new_presenting_issues) && (form.followup_new_presenting_issues === "No" || selectedPresentingIssues.value.length > 0)
		: selectedPresentingIssues.value.length > 0 && (!isFollowUp.value || Boolean(form.session_details.trim()))
	return required.every((key) => String(form[key] ?? "").trim() !== "")
}
const isDone = (section, index) => index + 1 !== step.value && visited.value.has(index + 1) && sectionComplete(section)

function goTo(target) {
	step.value = target
}
function next() {
	if (step.value < sections.value.length) step.value += 1
}
function previous() {
	if (step.value > 1) step.value -= 1
}
function onSubmit() {
	if (step.value < sections.value.length) return next()
	if (canSave.value) submit()
}
function submit() {
	formError.value = ""
	const missing = sections.value.findIndex((section) => !sectionComplete(section))
	if (missing !== -1) {
		step.value = missing + 1
		formError.value = `Complete the required fields in “${sections.value[missing].title}” before saving.`
		return
	}
	save()
}

// Banner above the wizard
const TONES = {
	green: "bg-[#DCF3E4] text-[#146C3A]",
	amber: "bg-[#FDECC8] text-[#8A4B00]",
	blue: "bg-[#E0EAFD] text-[#1B4DB1]",
	gray: "bg-[#E4E6EA] text-[#3A3F47]",
}
const banner = computed(() => {
	const r = record.value || {}
	if (caseClosed.value) return { text: "This case is closed. Its session records are available in read-only mode.", label: "Read only", pill: TONES.gray }
	if (r.status === "Completed") return { text: "This session has been recorded. The summary is locked and read-only.", label: "Recorded", pill: TONES.green }
	if (r.status === "Cancelled") return { text: "This appointment was cancelled, so it cannot be recorded.", label: "Cancelled", pill: TONES.gray }
	if (!canManage.value) return { text: `This appointment was referred to ${r.counsellor_name || r.counsellor_id} and is now on their schedule.`, label: "Referred", pill: TONES.blue }
	if (r.session_type === "Termination") return { text: "Review the case history, then record the termination session. Saving this session will close the case.", label: "Scheduled", pill: TONES.blue }
	return r.overdue
		? { text: "This session has passed. Review the case history, then record it below.", label: "Overdue", pill: TONES.amber }
		: { text: "Review the case history, then record the session details, issues, interventions, urgency, risk and follow-up plan.", label: "Scheduled", pill: TONES.blue }
})

// ---- Case history helpers ----
// The most recent completed session is opened by default
const latestName = computed(() => {
	const done = history.value.filter((item) => item.status === "Completed")
	return done.length ? [...done].sort((a, b) => String(b.date_time).localeCompare(String(a.date_time)))[0].name : ""
})

const facts = (item) => item.session_type === "Follow-Up"
	? [
												["Mode of counseling", item.mode_of_contact],
												["How the client has been feeling since the last session", item.session_details, true],
												["Presenting issues", presentingText(item.presenting_issues)],
												["Current wellbeing", item.followup_wellbeing_rating],
												["Recent stress frequency", item.followup_stress_frequency],
		["Issue subclassifications", item.issue_subclassifications],
		["Urgency level", item.urgency_level],
		["Risk assessment", item.risk_assessment, true],
	]
	: [
												["Presenting issues", presentingText(item.presenting_issues)],
		["Issue subclassifications", item.issue_subclassifications],
		["Interventions applied", item.interventions_applied],
		["Referrals made", item.referrals_made],
		["Urgency level", item.urgency_level],
		["Risk assessment", item.risk_assessment],
		["Session details", item.session_details, true],
												["Follow-up needed", item.needs_follow_up],
												["Follow-up plan", item.follow_up_plan, true],
	]

const followupGroups = (item) => [
	{ title: "Progress on previous goals", rows: [
		["Goals or issues discussed last time", item.followup_goals_discussed],
		["Progress or changes", item.progress_previous_goals],
		["Challenges or setbacks", item.followup_challenges],
	] },
	{ title: "Current concerns / new issues", rows: [
												["Any new issues or stressors?", item.followup_new_issues_present],
		...(item.followup_new_issues_present === "Yes" ? [["New issues or stressors", item.followup_new_issues]] : []),
												["Any new presenting issues?", item.followup_new_presenting_issues],
												...(item.followup_new_presenting_issues === "Yes" ? [["New presenting issues", presentingText(item.presenting_issues)]] : []),
												["Any evident changes?", item.followup_evident_changes_present],
		...(item.followup_evident_changes_present === "Yes" ? [["Evident changes", item.followup_evident_changes]] : []),
	] },
	{ title: "Coping and support", rows: [
		["Coping skills or supports", item.followup_coping_support],
		["Effectiveness", item.followup_support_effectiveness],
		["Additional support needed", item.followup_additional_support],
	] },
	{ title: "Counsellor’s observation", rows: [
		["Mood and affect", [item.followup_mood_affect, item.followup_mood_other].filter(Boolean).join(" — ")],
		["Engagement level", item.followup_engagement_level],
		["Risk concerns", item.followup_risk_concerns],
	] },
	{ title: "Next steps / plan", rows: [
		["Recommendations", item.followup_recommendations],
		["Key takeaways or interventions used today", item.followup_takeaways],
		["Referrals made", item.referrals_made],
		["Focus for next session", item.next_session_focus],
		["Follow-up action", item.followup_action],
	] },
]

</script>

<style scoped>
/* No font-family is set here: the page inherits the app font, like the baseline survey. */

.lbl { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; line-height: 20px; color: #2b2f36; }
.req { color: #a10e24; }

.field { display: block; width: 100%; min-height: 44px; border: 1px solid #d5d8de; border-radius: 10px; background: #fff; padding: 10px 12px; font-family: inherit; font-size: 14px; line-height: 20px; color: #2b2f36; resize: vertical; transition: border-color 0.15s, box-shadow 0.15s; }
.field::placeholder { color: #6b717b; }
.field.is-empty { color: #6b717b; }
.field:hover:not(:disabled) { border-color: #b5bac3; }
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }
fieldset:disabled .field { background: #f4f5f7; color: #5b616b; }
.field:disabled { cursor: default; }

/* Radio option cards (same pattern as the baseline survey) */
.opt { font-family: inherit; display: flex; min-height: 44px; cursor: pointer; align-items: center; gap: 12px; border: 1px solid #d5d8de; border-radius: 10px; background: #fff; padding: 0 14px; font-size: 14px; color: #2b2f36; transition: border-color 0.15s, background 0.15s; }
.opt:hover { border-color: #c8102e; }
.opt-on { border-color: #c8102e; background: #fff8f9; }
fieldset:disabled .opt { cursor: default; }
fieldset:disabled .opt:not(.opt-on) { background: #f4f5f7; color: #5b616b; }
fieldset:disabled .opt:hover:not(.opt-on) { border-color: #d5d8de; }

/* Presenting-issue dropdown */
.issue-menu { position: absolute; z-index: 30; top: calc(100% + 8px); left: 0; width: 100%; max-height: 260px; overflow-y: auto; border: 1px solid #e4e6ea; border-radius: 12px; background: #fff; padding: 6px; box-shadow: 0 12px 30px rgba(31, 35, 45, 0.14); }
.issue-option { font-family: inherit; display: flex; min-height: 44px; width: 100%; align-items: center; justify-content: space-between; gap: 10px; border-radius: 8px; padding: 8px 12px; text-align: left; font-size: 14px; color: #2b2f36; }
.issue-option:hover { background: #f4f5f7; }
.issue-option-active, .issue-option-active:hover { background: #fce8eb; color: #a10e24; font-weight: 600; }

/* Case history */
.fact-value { white-space: pre-line; overflow-wrap: anywhere; }
.hist-summary { list-style: none; }
.hist-summary::-webkit-details-marker { display: none; }
.hist-chev { transition: transform 0.15s; }
.hist[open] .hist-chev { transform: rotate(180deg); }
</style>
