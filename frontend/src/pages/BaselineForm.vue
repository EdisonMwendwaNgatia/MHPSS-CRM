<template>
	<main class="mx-auto max-w-7xl px-4 py-6 md:px-7 md:py-8">
		<!-- Breadcrumb -->
		<nav class="mb-6 flex flex-wrap items-center gap-1.5 text-sm text-[#5B616B]" aria-label="Breadcrumb">
			<router-link v-if="!isPublic && !isProgrammeFill" :to="{ name: 'Clients' }" class="rounded-md px-1.5 py-0.5 transition-colors hover:bg-white hover:text-[#A10E24]">Clients</router-link>
			<router-link v-else-if="isProgrammeFill" :to="{ name: 'ProgrammeClientDetail', params: { name: clientName } }" class="rounded-md px-1.5 py-0.5 transition-colors hover:bg-white hover:text-[#A10E24]">Programme client</router-link>
			<svg v-if="!isPublic" class="h-3.5 w-3.5 text-[#B4B9C1]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 6 6 6-6 6" /></svg>
			<router-link v-if="!isPublic && !isProgrammeFill" :to="{ name: 'ClientProfile', params: { name: clientName } }" class="rounded-md px-1.5 py-0.5 transition-colors hover:bg-white hover:text-[#A10E24]">
				{{ profile.data?.client?.scholar_code || 'Client' }}
			</router-link>
			<span v-else class="px-1.5 py-0.5 font-semibold text-[#2B2F36]">{{ profile.data?.client?.scholar_code || 'Client' }}</span>
			<svg class="h-3.5 w-3.5 text-[#B4B9C1]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 6 6 6-6 6" /></svg>
			<span class="px-1.5 py-0.5 font-semibold text-[#2B2F36]">Baseline Survey</span>
		</nav>

		<PageLoader v-if="profile.loading && !profile.data" />
		<template v-else-if="profile.data">
			<!-- Page header -->
			<header class="mb-6 flex flex-wrap items-start justify-between gap-4">
				<div class="flex items-start gap-4">
					<div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#FDECEF] text-[#C8102E]">
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
							<path d="M9 4h6a1 1 0 0 1 1 1v1H8V5a1 1 0 0 1 1-1Z" /><path d="M8 6H6.5A1.5 1.5 0 0 0 5 7.5v12A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5v-12A1.5 1.5 0 0 0 17.5 6H16" /><path d="m9 14 2 2 4-4.5" />
						</svg>
					</div>
					<div>
						<h1 class="text-2xl font-semibold leading-8 text-[#2B2F36]">Baseline Survey</h1>
						<p class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-[#5B616B]">
							<span class="rounded-md bg-white px-2 py-0.5 text-xs font-semibold text-[#2B2F36] ring-1 ring-[#E4E6EA]">{{ profile.data.client.scholar_code }}</span>
							<span class="font-medium text-[#3A3F47]">{{ profile.data.client.full_name }}</span>
							<span v-if="profile.data.client.assigned_counsellor" class="text-[#5B616B]">Counsellor: {{ profile.data.client.assigned_counsellor }}</span>
						</p>
					</div>
				</div>
				<div class="flex items-center gap-2.5 rounded-xl border border-[#E4E6EA] bg-white px-3.5 py-2.5 text-sm text-[#5B616B] shadow-[0_1px_2px_rgba(23,25,29,0.04)]">
					<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#F4F5F7] text-[#5B616B]">
						<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
							<rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" />
						</svg>
					</span>
					{{ isPublic ? 'Secure one-time form · submission locks this cycle' : isProgrammeFill ? `Programme Manager entry · cycle ${profile.data.cycle}` : 'Confidential · counsellor access only' }}
				</div>
			</header>

			<!-- Already submitted -->
			<div v-if="profile.data.survey" class="overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(23,25,29,0.04)]">
				<div class="h-1 bg-[#146C3A]/70"></div>
				<div class="p-6 md:p-8">
					<div class="flex items-start gap-4">
						<span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#DCF3E4] text-[#146C3A]">
							<svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
						</span>
						<div>
							<div class="mb-2 inline-flex items-center gap-1.5 rounded-full bg-[#E0EAFD] px-3 py-1 text-xs font-semibold text-[#1B4DB1]">
								<svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
								Read only
							</div>
							<h2 class="text-lg font-semibold text-[#2B2F36]">{{ isPublic ? 'Thank you — your baseline survey was submitted' : 'Baseline survey already recorded' }}</h2>
							<p class="mt-1 text-sm text-[#5B616B]">This form cycle has been submitted and is locked.</p>
						</div>
					</div>
					<div class="mt-6 grid gap-3 sm:grid-cols-2">
						<div class="rounded-xl bg-[#F4F5F7] p-4 text-sm"><span class="block text-xs text-[#5B616B]">Consent</span><span class="mt-1 block font-semibold text-[#2B2F36]">{{ profile.data.survey.consent }}</span></div>
						<div v-if="profile.data.survey.wellbeing_self_rating" class="rounded-xl bg-[#F4F5F7] p-4 text-sm"><span class="block text-xs text-[#5B616B]">Wellbeing rating</span><span class="mt-1 block font-semibold text-[#2B2F36]">{{ profile.data.survey.wellbeing_self_rating }}</span></div>
					</div>
				</div>
			</div>

			<template v-else>
				<!-- Consent bar -->
				<section class="mb-5 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-[#E4E6EA] bg-white px-5 py-4 shadow-[0_1px_2px_rgba(23,25,29,0.04)]" aria-label="Survey consent">
					<div class="flex items-center gap-3.5 text-sm text-[#2B2F36]">
						<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-colors"
							:class="form.consent === 'Consented' ? 'bg-[#DCF3E4] text-[#146C3A]' : form.consent === 'Declined' ? 'bg-[#FDECEF] text-[#A10E24]' : 'bg-[#F4F5F7] text-[#5B616B]'">
							<svg v-if="form.consent === 'Consented'" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
							<svg v-else-if="form.consent === 'Declined'" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>
							<svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 4.5 6v5.5c0 4.4 3.1 8.3 7.5 9.5 4.4-1.2 7.5-5.1 7.5-9.5V6L12 3Z" /><path d="M12 8.5v4M12 15.5h.01" /></svg>
						</span>
						<div>
							<strong class="block font-semibold">Consent</strong>
							<span v-if="form.consent === 'Consented'" class="text-[#5B616B]">The client has agreed to take part in the baseline survey.</span>
							<span v-else-if="form.consent === 'Declined'" class="text-[#5B616B]">The client has declined to take part in the baseline survey.</span>
							<span v-else class="text-[#5B616B]">Please record the client’s consent before continuing.</span>
						</div>
					</div>
					<div class="flex flex-wrap items-center gap-3">
						<FormControl label="Consent decision" type="select" :options="consentOptions" v-model="form.consent" />
					</div>
				</section>

				<!-- Declined -->
				<section v-if="form.consent === 'Declined'" class="rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(23,25,29,0.04)] md:p-6">
					<h2 class="text-lg font-semibold text-[#2B2F36]">Record declined consent</h2>
					<p class="mb-5 mt-1 text-sm text-[#5B616B]">Declining is recorded. The client can still receive and record support sessions.</p>
					<div class="max-w-xl">
						<FormControl label="Reason (optional)" type="textarea" v-model="form.declined_reason" />
					</div>
					<ErrorMessage class="mt-4" :message="activeSaver.error" />
					<div class="mt-6 flex justify-end border-t border-[#E4E6EA] pt-5">
						<Button type="button" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="activeSaver.loading" @click="submit">
							Record the declination
						</Button>
					</div>
				</section>

				<!-- Consented: stepper + form -->
				<div v-else-if="form.consent === 'Consented'" class="flex items-start gap-5 max-[800px]:flex-col">
					<nav class="w-[280px] shrink-0 rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(23,25,29,0.04)] min-[801px]:sticky min-[801px]:top-6 max-[800px]:w-full" aria-label="Survey sections">
						<div class="mb-2 flex items-baseline justify-between text-xs text-[#5B616B]">
							<span>Section {{ step }} of {{ sections.length }}</span>
							<span class="font-semibold text-[#A10E24]">{{ Math.round((step / sections.length) * 100) }}%</span>
						</div>
						<div class="mb-5 h-2 overflow-hidden rounded-full bg-[#E4E6EA]" role="progressbar" :aria-valuenow="Math.round((step / sections.length) * 100)" aria-valuemin="0" aria-valuemax="100">
							<div class="h-full rounded-full bg-[#C8102E] transition-all duration-500 ease-out" :style="{ width: `${(step / sections.length) * 100}%` }"></div>
						</div>
						<ol>
							<li v-for="(section, index) in sections" :key="section.title" class="relative">
								<span v-if="index < sections.length - 1" class="absolute left-5 top-[34px] h-[calc(100%-24px)] w-px transition-colors" :class="index + 1 < step ? 'bg-[#BFE5CD]' : 'bg-[#E4E6EA]'" aria-hidden="true"></span>
								<button type="button" class="relative flex min-h-11 w-full items-center gap-3 rounded-lg px-2 text-left text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/40"
									:class="step === index + 1 ? 'bg-[#FFF8F9] font-semibold text-[#A10E24]' : 'text-[#4A505A] hover:bg-[#F4F5F7]'"
									:aria-current="step === index + 1 ? 'step' : undefined" @click="goTo(index + 1)">
									<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-colors"
										:class="index + 1 < step ? 'bg-[#DCF3E4] text-[#146C3A]' : step === index + 1 ? 'bg-[#C8102E] text-white ring-4 ring-[#C8102E]/15' : 'bg-[#E4E6EA] text-[#3A3F47]'">
										<svg v-if="index + 1 < step" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m5 12 5 5L20 7" /></svg>
										<template v-else>{{ index + 1 }}</template>
									</span>
									{{ section.title }}
								</button>
							</li>
						</ol>
					</nav>

					<form class="min-w-0 flex-1 rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(23,25,29,0.04)]" @submit.prevent="step === sections.length ? submit() : next()">
						<!-- Section header -->
						<div class="border-b border-[#E4E6EA] px-5 py-5 md:px-6">
							<div class="min-w-0">
								<h2 class="text-lg font-semibold leading-7 text-[#2B2F36]">{{ currentSection.heading }}</h2>
								<p v-if="currentSection.description" class="mt-0.5 text-sm text-[#5B616B]">{{ currentSection.description }}</p>
							</div>
						</div>

						<div class="p-5 md:p-6">
							<Transition name="step" mode="out-in">
								<!-- Step 1 -->
								<div v-if="step === 1" key="s1" class="grid gap-3 sm:grid-cols-2">
									<div v-for="item in clientSummary" :key="item.label" class="rounded-xl border border-[#EEF0F3] bg-[#F4F5F7] p-4">
										<span class="block text-xs text-[#5B616B]">{{ item.label }}</span>
										<span class="mt-1 block text-sm font-semibold text-[#2B2F36]" :class="!item.value && '!font-normal italic text-[#8A9099]'">{{ item.value || 'Not recorded' }}</span>
									</div>
								</div>

								<!-- Step 2 -->
								<div v-else-if="step === 2" key="s2" class="max-w-xl space-y-7">
									<div class="space-y-5">
										<h3 class="text-sm font-semibold text-[#2B2F36]">Relationships and children</h3>
										<FormControl label="What is your current marital status?" type="select" :options="MARITAL" v-model="form.marital_status" />
										<p v-if="fieldErrors.marital_status" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.marital_status }}</p>
										<FormControl label="Do you have a child or children?" type="select" :options="YES_NO" v-model="form.has_children" @update:model-value="syncChildrenAnswer" />
										<template v-if="form.has_children === 'Yes'">
											<FormControl label="How many children do you have?" type="number" v-model="form.number_of_children" @update:model-value="syncChildCount" />
											<p v-if="fieldErrors.number_of_children" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.number_of_children }}</p>
											<fieldset v-if="childAgeFields.length" class="space-y-4 rounded-xl border border-[#E4E6EA] bg-[#FAFAFB] p-4">
												<legend class="px-1.5 text-sm font-semibold text-[#2B2F36]">Child details</legend>
												<div v-for="index in childAgeFields" :key="index">
													<FormControl :label="`Age of child ${index} (in years; enter 0 if under 1 year)`" type="number" :min="0" step="1" v-model="childAges[index - 1]" />
													<p v-if="fieldErrors[`child_age_${index}`]" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors[`child_age_${index}`] }}</p>
												</div>
											</fieldset>
										</template>
									</div>

									<div class="space-y-5 border-t border-[#E4E6EA] pt-6">
										<h3 class="text-sm font-semibold text-[#2B2F36]">Family and home</h3>
										<FormControl label="Family status" type="select" :options="FAMILY_STATUS" v-model="form.family_status" />
										<FormControl label="Have you been abandoned or neglected by your family?" type="select" :options="YES_NO" v-model="form.family_abandonment_neglect" />
										<FormControl label="Have you been a victim of domestic abuse?" type="select" :options="YES_NO" v-model="form.domestic_abuse_victim" />
										<FormControl label="How many people depend on you for financial or other support?" type="number" v-model="form.dependants" />
										<p v-if="fieldErrors.dependants" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.dependants }}</p>
										<FormControl label="Would you like to describe your current home or living situation?" type="textarea" v-model="form.domestic_situation" />
										<p v-if="fieldErrors.domestic_situation" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.domestic_situation }}</p>
									</div>

									<div class="space-y-5 border-t border-[#E4E6EA] pt-6">
										<h3 class="text-sm font-semibold text-[#2B2F36]">Conflict or disaster</h3>
										<FormControl label="Have you been affected by conflict or a disaster?" type="select" :options="EXPOSURE" v-model="form.conflict_exposure" />
										<p v-if="fieldErrors.conflict_exposure" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.conflict_exposure }}</p>
										<FormControl v-if="form.conflict_exposure === 'Yes'" label="Exposure details" type="textarea" v-model="form.exposure_details" />
									</div>
								</div>

								<!-- Step 3 -->
								<div v-else-if="step === 3" key="s3" class="max-w-xl">
									<FormControl label="How would you rate your current emotional and psychological wellbeing?" type="select" :options="RATINGS" v-model="form.wellbeing_self_rating" />
									<p v-if="fieldErrors.wellbeing_self_rating" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.wellbeing_self_rating }}</p>
								</div>

								<!-- Step 4 -->
								<div v-else-if="step === 4" key="s4" class="max-w-xl">
									<fieldset class="border-0 p-0">
										<legend class="mb-4 text-sm font-medium leading-6 text-[#2B2F36]">In the past two weeks, how often have you experienced significant stress, anxiety, low mood, or difficulty concentrating?</legend>
										<label v-for="option in stressOptions" :key="option.value"
											class="mb-2.5 flex min-h-12 cursor-pointer items-center gap-3 rounded-[10px] border px-4 text-sm transition-all focus-within:ring-2 focus-within:ring-[#C8102E]/30"
											:class="form.stress_frequency === option.value ? 'border-[#C8102E] bg-[#FFF8F9] font-medium text-[#2B2F36] shadow-[0_0_0_1px_#C8102E]' : 'border-[#D5D8DE] bg-white text-[#3A3F47] hover:border-[#C8102E] hover:bg-[#FFFBFB]'">
											<input v-model="form.stress_frequency" class="h-[18px] w-[18px] shrink-0 accent-[#C8102E]" type="radio" :value="option.value" />{{ option.label }}
										</label>
									</fieldset>
									<p v-if="fieldErrors.stress_frequency" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.stress_frequency }}</p>
								</div>

								<!-- Step 5 -->
								<div v-else-if="step === 5" key="s5" class="max-w-xl">
									<fieldset class="border-0 p-0">
										<legend class="mb-4 text-sm font-medium leading-6 text-[#2B2F36]">What are your main current concerns? <span class="font-normal text-[#5B616B]">(select all that apply)</span></legend>
										<div class="grid gap-2.5 sm:grid-cols-2">
											<label v-for="concern in mainConcernOptions" :key="concern"
												class="flex min-h-12 cursor-pointer items-center gap-3 rounded-[10px] border px-3.5 text-sm transition-all focus-within:ring-2 focus-within:ring-[#C8102E]/30"
												:class="selectedMainConcerns.includes(concern) ? 'border-[#C8102E] bg-[#FFF8F9] font-medium text-[#2B2F36] shadow-[0_0_0_1px_#C8102E]' : 'border-[#D5D8DE] bg-white text-[#3A3F47] hover:border-[#C8102E] hover:bg-[#FFFBFB]'">
												<input v-model="selectedMainConcerns" class="h-[18px] w-[18px] shrink-0 accent-[#C8102E]" type="checkbox" :value="concern" @change="syncConcernDetails" />
												{{ concern }}
											</label>
										</div>
									</fieldset>
									<p v-if="fieldErrors.main_concerns" class="mt-2 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.main_concerns }}</p>
									<div v-if="selectedMainConcerns.includes('Other')" class="mt-5">
										<FormControl label="Describe the other concern" type="textarea" v-model="form.main_concerns_other" />
									</div>
									<p v-if="fieldErrors.main_concerns_other" class="mt-1 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.main_concerns_other }}</p>
								</div>

								<!-- Step 6 -->
								<div v-else-if="step === 6" key="s6" class="max-w-xl space-y-5">
									<FormControl label="Do you have someone you can rely on when facing challenges?" type="select" :options="SUPPORT" v-model="form.support_availability" />
									<p v-if="fieldErrors.support_availability" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.support_availability }}</p>
									<FormControl label="What type of support would be most helpful to you?" type="select" :options="SUPPORT_TYPES" v-model="form.preferred_support_type" />
									<p v-if="fieldErrors.preferred_support_type" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.preferred_support_type }}</p>
								</div>

								<!-- Step 7 -->
								<div v-else-if="step === 7" key="s7" class="max-w-xl space-y-5">
									<FormControl label="How would you rate your ability to cope with stress?" type="select" :options="COPING" v-model="form.coping_ability" />
									<p v-if="fieldErrors.coping_ability" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.coping_ability }}</p>
									<FormControl label="When you feel stressed or upset, which best describes how you usually cope?" type="select" :options="COPING_BEHAVIOURS" v-model="form.coping_behaviour" @update:model-value="formError = ''" />
									<p v-if="fieldErrors.coping_behaviour" class="-mt-4 text-xs text-[#A10E24]" role="alert">{{ fieldErrors.coping_behaviour }}</p>
									<FormControl label="What are your main goals, dreams, or plans for your future?" type="textarea" v-model="form.future_goals" />
								</div>

								<!-- Step 8 -->
								<div v-else-if="step === 8" key="s8" class="max-w-xl space-y-4">
									<label class="flex min-h-14 cursor-pointer items-start gap-3.5 rounded-[10px] border px-4 py-3.5 transition-all focus-within:ring-2 focus-within:ring-[#C8102E]/30"
										:class="form.interest_in_support ? 'border-[#C8102E] bg-[#FFF8F9] shadow-[0_0_0_1px_#C8102E]' : 'border-[#D5D8DE] bg-white hover:border-[#C8102E]'">
										<input v-model="form.interest_in_support" type="checkbox" class="mt-0.5 h-[18px] w-[18px] shrink-0 accent-[#C8102E]" />
										<span class="text-sm font-medium leading-5 text-[#2B2F36]">Would you be interested in receiving MHPSS support during the programme?</span>
									</label>
									<label class="flex min-h-14 cursor-pointer items-start gap-3.5 rounded-[10px] border px-4 py-3.5 transition-all focus-within:ring-2 focus-within:ring-[#C8102E]/30"
										:class="form.willingness_for_followup ? 'border-[#C8102E] bg-[#FFF8F9] shadow-[0_0_0_1px_#C8102E]' : 'border-[#D5D8DE] bg-white hover:border-[#C8102E]'">
										<input v-model="form.willingness_for_followup" type="checkbox" class="mt-0.5 h-[18px] w-[18px] shrink-0 accent-[#C8102E]" />
										<span class="text-sm font-medium leading-5 text-[#2B2F36]">Would you be willing to take part in voluntary follow-up during the programme?</span>
									</label>
									<div class="pt-1">
										<FormControl label="Is there anything else you would like the MHPSS team to know about your wellbeing or support needs?" type="textarea" v-model="form.additional_support_needs" />
									</div>
								</div>
							</Transition>

							<div v-if="formError" class="mt-6 flex items-start gap-2.5 rounded-[10px] border border-[#F3C5CD] bg-[#FFF8F9] px-3.5 py-3 text-sm text-[#A10E24]" role="alert">
								<svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16.5h.01" /></svg>
								{{ formError }}
							</div>
							<ErrorMessage class="mt-5" :message="activeSaver.error" />
							<p v-if="step === sections.length" class="mt-6 flex items-start gap-2 rounded-[10px] bg-[#F4F5F7] px-3.5 py-3 text-xs leading-5 text-[#5B616B]">
								<svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></svg>
								This form cycle can be submitted once. Review your answers carefully before continuing.
							</p>
						</div>

						<!-- Footer -->
						<div class="flex flex-wrap items-center justify-between gap-3 rounded-b-xl border-t border-[#E4E6EA] bg-[#FAFAFB] px-5 py-4 md:px-6">
							<Button type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#2B2F36] hover:!bg-[#F4F5F7]" :disabled="step === 1" @click="previous">Previous</Button>
							<Button type="submit" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-6 shadow-[0_1px_2px_rgba(161,14,36,0.3)] hover:!bg-[#A10E24]" :loading="activeSaver.loading">
								{{ step === sections.length ? 'Submit survey' : 'Next' }}
							</Button>
						</div>
					</form>
				</div>
			</template>
		</template>
		<ErrorMessage v-if="!profile.loading && !profile.data" :message="profile.error || programmeContext.error || publicContext.error || 'The baseline form could not be loaded.'" />

		<!-- Confirm dialog -->
		<Transition name="dialog">
			<div v-if="confirmOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-[#17191D]/50 p-4 backdrop-blur-[2px]" @click.self="confirmOpen = false">
				<section class="dialog-card w-full max-w-md rounded-xl bg-white p-6 shadow-[0_20px_50px_-12px_rgba(23,25,29,0.35)]" role="alertdialog" aria-modal="true" aria-labelledby="submit-confirm-title">
					<div class="flex items-start gap-4">
						<span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#FDECEF] text-[#C8102E]">
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
						</span>
						<div>
							<h2 id="submit-confirm-title" class="text-lg font-semibold text-[#25272B]">Submit baseline survey?</h2>
							<p class="mt-2 text-sm leading-6 text-[#555860]">You can submit this form only once for this cycle. Please review your answers carefully. After submission, the form will be locked and cannot be edited.</p>
						</div>
					</div>
					<div class="mt-6 flex justify-end gap-2.5">
						<Button type="button" class="!h-11 !rounded-[10px] !border-[#D5D8DE] !bg-white !text-[#33353A] hover:!bg-[#F4F5F7]" @click="confirmOpen = false">Review answers</Button>
						<Button type="button" variant="solid" class="!h-11 !rounded-[10px] !bg-[#C8102E] px-5 hover:!bg-[#A10E24]" :loading="activeSaver.loading" @click="confirmSubmit">Confirm submit</Button>
					</div>
				</section>
			</div>
		</Transition>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { COPING, COPING_BEHAVIOURS, EXPOSURE, MARITAL, RATINGS, STRESS, SUPPORT, SUPPORT_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const clientName = computed(() => props.name || route.params.name)
const token = computed(() => String(route.params.token || ""))
const isPublic = computed(() => !!token.value)
const isProgrammeFill = computed(() => route.name === "ProgrammeBaseline")
const step = ref(1)
const formError = ref("")
const confirmOpen = ref(false)
const surveyId = ref("")
const fieldErrors = reactive({})
const childAges = ref([])
const childAgeFields = computed(() => {
	const count = Number(form.number_of_children)
	return Number.isInteger(count) && count > 0 && count <= 50 ? Array.from({ length: count }, (_, i) => i + 1) : []
})
const stressOptions = computed(() => STRESS.filter((item) => item.value))

const sections = [
	{ title: "Student information", heading: "Student information", description: "Confirm the client record before beginning the survey." },
	{ title: "Family background", heading: "Section 2: Family background", description: "Record the family and home context shared by the client." },
	{ title: "Wellbeing", heading: "Section 3: Wellbeing", description: "Record the client’s current self-rating." },
	{ title: "Stress frequency", heading: "Section 4: Stress frequency", description: "How often has the client felt stressed recently?" },
	{ title: "Concerns", heading: "Section 5: Concerns", description: "Record the concerns shared by the client." },
	{ title: "Support systems", heading: "Section 6: Support systems", description: "Record the support currently available to the client." },
	{ title: "Coping mechanisms", heading: "Section 7: Coping mechanisms", description: "Record how the client is coping and the strategies they use." },
	{ title: "Interest in MHPSS support", heading: "Section 8: Interest in MHPSS support", description: "Record the client’s support preferences and follow-up consent." },
]
const mainConcernOptions = [
	"Academic pressure", "Financial challenges", "Family issues", "Relationships",
	"Loneliness", "Health Concerns", "Substance/Gambling", "Other",
]
const currentSection = computed(() => sections[step.value - 1])
const consentOptions = [
	{ label: "Select consent decision", value: "" },
	{ label: "Client consented", value: "Consented" },
	{ label: "Client declined", value: "Declined" },
]
const YES_NO = [{ label: "Choose an answer", value: "" }, { label: "Yes", value: "Yes" }, { label: "No", value: "No" }]
const FAMILY_STATUS = [{ label: "Choose family status", value: "" }, { label: "Both parents", value: "Both parents" }, { label: "Single parent", value: "Single parent" }, { label: "Orphan", value: "Orphan" }]
const form = reactive({
	consent: "", wellbeing_self_rating: "", dependants: "", interest_in_support: false, willingness_for_followup: false,
	declined_reason: "", stress_frequency: "", main_concerns: "", main_concerns_other: "", support_availability: "", coping_ability: "",
	coping_behaviour: "", coping_behaviour_other: "", preferred_support_type: "", marital_status: "", domestic_situation: "", conflict_exposure: "", exposure_details: "",
	has_children: "", number_of_children: "", children_ages: "", family_status: "", family_abandonment_neglect: "", domestic_abuse_victim: "", future_goals: "", additional_support_needs: "",
})
const selectedMainConcerns = ref([])

const profile = createResource({ url: "krcti_mhpss.api.counsellor.client_profile" })
const programmeContext = createResource({
	url: "krcti_mhpss.api.baseline_workflow.programme_baseline_context",
	onSuccess(data) { surveyId.value = data.survey_id; profile.data = { client: data.client, survey: null, cycle: data.cycle }; profile.loading = false },
	onError() { profile.loading = false },
})
const publicContext = createResource({
	url: "krcti_mhpss.api.baseline_workflow.public_baseline_context",
	onSuccess(data) { surveyId.value = data.survey_id; profile.data = { client: data.client, survey: null, cycle: data.cycle }; profile.loading = false },
	onError() { profile.loading = false },
})
const counsellorSaver = createResource({
	url: "krcti_mhpss.api.records.record_baseline",
	onSuccess() {
		router.replace({ name: "ClientProfile", params: { name: clientName.value } })
	},
})
const programmeSaver = createResource({
	url: "krcti_mhpss.api.baseline_workflow.programme_baseline_submit",
	onSuccess() { router.replace({ name: "ProgrammeClientDetail", params: { name: clientName.value } }) },
})
const publicSaver = createResource({
	url: "krcti_mhpss.api.baseline_workflow.public_baseline_submit",
	onSuccess() { profile.data = { ...profile.data, survey: { consent: form.consent, status: form.consent === "Declined" ? "Declined" : "Completed" } }; confirmOpen.value = false },
})
const activeSaver = computed(() => isPublic.value ? publicSaver : isProgrammeFill.value ? programmeSaver : counsellorSaver)

onMounted(() => {
	if (isPublic.value) { profile.loading = true; publicContext.submit({ token: token.value }) }
	else if (isProgrammeFill.value) { profile.loading = true; programmeContext.submit({ client: clientName.value, survey: route.query.survey }) }
	else profile.submit({ name: clientName.value })
})

const clientSummary = computed(() => {
	const client = profile.data?.client || {}
	return [
		{ label: "Participant code", value: client.scholar_code },
		{ label: "Full name", value: client.full_name },
		{ label: "Institution", value: client.institution },
		{ label: "Course / programme", value: client.course_programme },
		{ label: "Year of study", value: client.year_of_study },
		{ label: "Programme stream", value: client.programme_stream },
	]
})

function goTo(target) {
	if (target <= step.value || target === step.value + 1) step.value = target
}
function next() {
	if (step.value < sections.length) step.value += 1
}
function previous() {
	if (step.value > 1) step.value -= 1
}
function syncConcernDetails() {
	formError.value = ""
	if (!selectedMainConcerns.value.includes("Other")) form.main_concerns_other = ""
}
function syncChildrenAnswer() {
	delete fieldErrors.number_of_children
	for (const key of Object.keys(fieldErrors)) if (key.startsWith("child_age_")) delete fieldErrors[key]
	if (form.has_children !== "Yes") {
		form.number_of_children = ""
		childAges.value = []
	}
}
function syncChildCount() {
	delete fieldErrors.number_of_children
	const count = Number(form.number_of_children)
	if (Number.isInteger(count) && count > 0 && count <= 50) childAges.value = Array.from({ length: count }, (_, i) => childAges.value[i] ?? "")
	else childAges.value = []
	for (const key of Object.keys(fieldErrors)) if (key.startsWith("child_age_")) delete fieldErrors[key]
}
function submit() {
	formError.value = ""
	for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
	if (!form.consent) { formError.value = "Record the client’s consent before submitting."; return }
	if (form.consent === "Consented") {
		const required = ["wellbeing_self_rating", "stress_frequency", "support_availability", "coping_ability", "preferred_support_type", "coping_behaviour", "marital_status", "domestic_situation", "conflict_exposure"]
		const missing = required.filter((key) => form[key] === "" || form[key] === null || form[key] === undefined)
		for (const key of missing) fieldErrors[key] = "This answer is required."
		if (!selectedMainConcerns.value.length) fieldErrors.main_concerns = "Select at least one concern."
		if (form.has_children === "Yes") {
			if (!Number.isInteger(Number(form.number_of_children)) || Number(form.number_of_children) < 1 || Number(form.number_of_children) > 50) fieldErrors.number_of_children = "Enter a whole number from 1 to 50."
			else childAges.value.forEach((age, index) => {
				if (age === "" || age === null || age === undefined || !Number.isInteger(Number(age)) || Number(age) < 0) fieldErrors[`child_age_${index + 1}`] = "Enter a whole number of 0 or more."
			})
		}
		if (missing.length || fieldErrors.main_concerns || fieldErrors.number_of_children || Object.keys(fieldErrors).some((key) => key.startsWith("child_age_"))) {
			formError.value = "Complete the highlighted answers before submitting."
			step.value = sectionForField(missing[0] || (fieldErrors.number_of_children || Object.keys(fieldErrors).some((key) => key.startsWith("child_age_")) ? "has_children" : "main_concerns"))
			return
		}
		if (!RATINGS.some((option) => option.value === form.wellbeing_self_rating && option.value)) { fieldErrors.wellbeing_self_rating = "Choose a wellbeing rating."; step.value = 3; formError.value = "Correct the highlighted answer."; return }
		if (form.dependants !== "" && (!Number.isInteger(Number(form.dependants)) || Number(form.dependants) < 0)) { fieldErrors.dependants = "Enter a whole number of zero or more."; step.value = 2; formError.value = "Correct the highlighted answer."; return }
		const textFields = ["main_concerns", "main_concerns_other", "coping_behaviour_other", "domestic_situation", "exposure_details", "future_goals", "additional_support_needs"]
		const tooLong = textFields.find((key) => String(form[key] || "").length > 2000)
		if (tooLong) { fieldErrors[tooLong] = "Keep this answer to 2000 characters or fewer."; step.value = sectionForField(tooLong); formError.value = "Correct the highlighted answer."; return }
	}
	if (form.consent === "Consented" && selectedMainConcerns.value.includes("Other") && !form.main_concerns_other.trim()) {
		step.value = 5
		fieldErrors.main_concerns_other = "Describe the other concern."
		formError.value = "Describe the other concern before submitting."
		return
	}
	confirmOpen.value = true
}
function sectionForField(field) {
	if (["marital_status", "has_children", "number_of_children", "children_ages", "family_status", "family_abandonment_neglect", "domestic_abuse_victim", "dependants", "domestic_situation", "conflict_exposure", "exposure_details"].includes(field) || field.startsWith("child_age_")) return 2
	if (field === "wellbeing_self_rating") return 3
	if (field === "stress_frequency") return 4
	if (["main_concerns", "main_concerns_other"].includes(field)) return 5
	if (["support_availability", "preferred_support_type"].includes(field)) return 6
	if (["coping_ability", "coping_behaviour", "coping_behaviour_other", "future_goals"].includes(field)) return 7
	return 8
}
function confirmSubmit() {
	const data = { consent: form.consent }
	if (form.consent === "Declined") {
		data.declined_reason = form.declined_reason
	} else {
		for (const key of ["stress_frequency", "main_concerns_other", "support_availability", "coping_ability", "coping_behaviour", "preferred_support_type", "marital_status", "domestic_situation", "conflict_exposure", "exposure_details", "has_children", "family_status", "family_abandonment_neglect", "domestic_abuse_victim", "future_goals", "additional_support_needs"]) {
			data[key] = form[key]
		}
		if (form.has_children === "Yes") {
			data.number_of_children = Number(form.number_of_children)
			data.children_ages = childAges.value.map(Number).join(", ")
		}
		data.main_concerns = selectedMainConcerns.value.join(", ")
		data.wellbeing_self_rating = form.wellbeing_self_rating
		data.dependants = form.dependants === "" ? 0 : Number(form.dependants)
		data.interest_in_support = form.interest_in_support ? 1 : 0
		data.willingness_for_followup = form.willingness_for_followup ? 1 : 0
	}
	if (isPublic.value) publicSaver.submit({ token: token.value, data })
	else if (isProgrammeFill.value) programmeSaver.submit({ survey: surveyId.value, data })
	else counsellorSaver.submit({ client: clientName.value, data })
}
</script>

<style scoped>
.step-enter-active,
.step-leave-active {
	transition: opacity 0.18s ease, transform 0.18s ease;
}
.step-enter-from {
	opacity: 0;
	transform: translateX(8px);
}
.step-leave-to {
	opacity: 0;
	transform: translateX(-8px);
}
.dialog-enter-active,
.dialog-leave-active {
	transition: opacity 0.18s ease;
}
.dialog-enter-active .dialog-card,
.dialog-leave-active .dialog-card {
	transition: transform 0.18s ease;
}
.dialog-enter-from,
.dialog-leave-to {
	opacity: 0;
}
.dialog-enter-from .dialog-card,
.dialog-leave-to .dialog-card {
	transform: translateY(8px) scale(0.98);
}
@media (prefers-reduced-motion: reduce) {
	.step-enter-active,
	.step-leave-active,
	.dialog-enter-active,
	.dialog-leave-active,
	.dialog-enter-active .dialog-card,
	.dialog-leave-active .dialog-card {
		transition: none;
	}
}
</style>
