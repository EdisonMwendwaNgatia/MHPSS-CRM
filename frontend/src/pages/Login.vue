<template>
	<main class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#F4F5F7] px-4 py-8 sm:px-8">
		<div class="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-white/70 blur-3xl"></div>
		<div class="pointer-events-none absolute -bottom-32 -right-20 h-96 w-96 rounded-full bg-[#FCE8EB]/70 blur-3xl"></div>

		<div class="relative grid w-full max-w-[1000px] overflow-hidden rounded-2xl border border-[#E4E6EA] bg-white shadow-[0_24px_80px_rgba(43,47,54,0.12)] md:min-h-[610px] md:grid-cols-[0.92fr_1.08fr]">
			<aside class="relative isolate flex min-h-[250px] flex-col justify-between overflow-hidden bg-gradient-to-br from-[#A10E24] via-[#C8102E] to-[#8F1022] p-7 text-white sm:p-10 md:min-h-full md:p-12">
				<div class="pointer-events-none absolute inset-0 -z-10 opacity-[0.12]" style="background-image: radial-gradient(#fff 0.8px, transparent 0.8px); background-size: 20px 20px"></div>
				<div class="pointer-events-none absolute -right-20 top-24 -z-10 h-64 w-64 rounded-full border border-white/20"></div>
				<div class="pointer-events-none absolute -right-8 top-36 -z-10 h-40 w-40 rounded-full border border-white/20"></div>

				<div class="flex items-center gap-3">
					<div class="leading-5">
						<p class="text-[15px] font-semibold tracking-wide">KRCTI MHPSS</p>
						<p class="text-xs text-white/75">Case Management</p>
					</div>
				</div>

				<div class="relative my-8 max-w-sm md:my-0">
					<h1 class="text-[30px] font-semibold leading-[1.15] tracking-[-0.03em] sm:text-[36px]">Care starts with being heard.</h1>
					<p class="mt-4 max-w-[340px] text-sm leading-6 text-white/80">A thoughtful, confidential space to support student wellbeing and coordinate care.</p>
					<div class="mt-8 flex items-center gap-3 border-t border-white/20 pt-5">
						<div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10" aria-hidden="true">
							<svg class="h-[18px] w-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
								<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/><path d="M7 12h3l1.5-2.5L14 15l1.5-3H18"/>
							</svg>
						</div>
						<p class="text-xs leading-5 text-white/80">Supporting KRCTI, WoC and KRCS teams with care and accountability.</p>
					</div>
				</div>
				<p class="text-[11px] tracking-wide text-white/55">CONFIDENTIAL · AUTHORISED ACCESS ONLY</p>
			</aside>

			<section class="flex flex-col justify-center px-6 py-9 sm:px-12 sm:py-12 md:px-14">
				<div class="mb-8">
					<p class="text-xs font-semibold uppercase tracking-[0.14em] text-[#A10E24]">Welcome back</p>
					<h2 class="mt-2 text-[28px] font-semibold leading-9 tracking-[-0.025em] text-[#2B2F36]">Sign in to your account</h2>
					<p class="mt-2 text-sm leading-5 text-[#5B616B]">Enter your staff credentials to continue.</p>
				</div>

				<form class="space-y-5" @submit.prevent="submit">
					<FormControl label="Email or username" type="text" v-model="email" autocomplete="username" placeholder="you@organisation.org" required />
					<div>
						<div>
							<FormControl label="Password" :type="showPassword ? 'text' : 'password'" v-model="password" autocomplete="current-password" placeholder="Enter your password" required>
								<template #suffix>
									<button type="button" class="rounded p-1 text-[#737A84] hover:text-[#2B2F36] focus:outline-none focus:ring-2 focus:ring-[#C8102E]/30" :aria-label="showPassword ? 'Hide password' : 'Show password'" :aria-pressed="showPassword" @click="showPassword = !showPassword">
								<svg v-if="!showPassword" class="h-[18px] w-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
								<svg v-else class="h-[18px] w-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8"/><path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a16 16 0 0 1-3.1 3.8M6.2 6.2C3.5 8 2 12 2 12s3.6 7 10 7c1.3 0 2.5-.3 3.5-.7"/></svg>
										</button>
								</template>
							</FormControl>
						</div>
					</div>

					<ErrorMessage :message="session.login.error" />
					<Button class="!h-12 w-full !rounded-[10px] !bg-[#C8102E] !font-semibold !shadow-[0_5px_12px_rgba(200,16,46,0.18)] hover:!bg-[#A10E24]" variant="solid" type="submit" :loading="session.login.loading">
						<span class="inline-flex items-center justify-center gap-2">
							Sign in securely
							<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
						</span>
					</Button>
				</form>

				<div class="mt-7 flex items-start gap-3 rounded-lg bg-[#F4F5F7] p-4 text-xs leading-[18px] text-[#5B616B]">
					<svg class="mt-0.5 h-4 w-4 shrink-0 text-[#A10E24]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>
					<p>Your account activity is recorded to help protect sensitive client information. For authorised KRCTI, WoC and KRCS staff only.</p>
				</div>
				<p class="mt-6 text-center text-xs text-[#737A84]">Need access? Contact your system manager.</p>
			</section>
		</div>
	</main>
</template>

<script setup>
import { ref } from "vue"
import { session } from "../data/session"

const email = ref("")
const password = ref("")
const showPassword = ref(false)

function submit() {
	session.login.submit({ email: email.value.trim(), password: password.value })
}
</script>
