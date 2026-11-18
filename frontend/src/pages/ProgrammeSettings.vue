<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 text-[#25272B] sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- Header -->
			<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
				<div>
					<p class="text-sm font-medium text-[#737780]">Programme oversight</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Programme settings</h1>
					<p class="mt-1 text-sm text-[#737780]">Manage which cohort receives new client registrations.</p>
				</div>
				<span v-if="settings.data" class="inline-flex items-center gap-2 self-start rounded-lg border border-[#E4E6EA] bg-white px-3 py-2 text-sm text-[#555860] shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:self-auto">
					<Layers :size="16" class="text-[#858891]" /> Active: Cohort {{ settings.data.active_cohort }}
				</span>
			</div>

			<ErrorMessage class="mt-5" :message="settings.error || (!confirmOpen ? saving.error : '')" />

			<!-- Saved message -->
			<div v-if="savedMessage" class="mt-5 flex items-start gap-3 rounded-xl border border-[#BFE3CB] bg-[#F0FAF3] px-4 py-3.5 text-sm text-[#146C3A]" role="status">
				<CheckCircle2 :size="19" class="mt-0.5 shrink-0" />
				<p class="min-w-0 flex-1 font-medium">{{ savedMessage }}</p>
				<button type="button" class="shrink-0 rounded-md p-1 text-[#146C3A]/70 transition hover:bg-[#DCF3E4] hover:text-[#146C3A]" aria-label="Dismiss" @click="savedMessage = ''"><X :size="16" /></button>
			</div>

			<div v-if="settings.loading && !settings.data" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white px-5 py-12"><PageLoader /></div>

			<template v-else-if="settings.data">
				<!-- Summary cards -->
				<section class="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Cohort summary">
					<div v-for="card in cards" :key="card.label" class="rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs font-semibold text-[#555860]">{{ card.label }}</span>
							<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full" :class="card.tone"><component :is="card.icon" :size="17" /></span>
						</div>
						<span class="mt-3 block text-[28px] font-semibold leading-none tabular-nums text-[#25272B]">{{ card.value }}</span>
						<span class="mt-2 block text-xs text-[#858891]">{{ card.hint }}</span>
					</div>
				</section>

				<!-- Cohort allocation -->
				<section class="mt-5 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
					<div class="flex flex-col justify-between gap-3 border-b border-[#ECEDEF] px-5 py-4 sm:flex-row sm:items-center">
						<div>
							<h2 class="text-base font-semibold text-[#25272B]">Client cohort allocation</h2>
							<p class="mt-0.5 max-w-3xl text-xs leading-5 text-[#858891]">Cohorts activate in order. You can move forward by one cohort at a time; previous cohorts cannot be reopened. Existing client records and codes remain unchanged.</p>
						</div>
						<span class="w-fit shrink-0 rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ settings.data.cohorts?.length || 0 }} cohorts</span>
					</div>

					<div class="grid gap-3 p-4 sm:grid-cols-2 sm:p-5 lg:grid-cols-3">
						<button
							v-for="item in settings.data.cohorts"
							:key="item.cohort"
							type="button"
							:disabled="!canSelect(item)"
							class="group rounded-xl border p-4 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30 disabled:cursor-not-allowed"
							:class="cardClass(item)"
							:aria-pressed="selected === item.cohort"
							@click="selected = item.cohort; savedMessage = ''"
						>
							<span class="flex items-center justify-between gap-2">
								<span class="flex items-center gap-2.5">
									<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold" :class="statusOf(item).avatar">{{ item.cohort }}</span>
									<span class="text-sm font-semibold text-[#25272B]">Cohort {{ item.cohort }}</span>
								</span>
								<span class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold" :class="statusOf(item).pill">
									<component :is="statusOf(item).icon" :size="12" /> {{ statusOf(item).label }}
								</span>
							</span>

							<span class="mt-4 flex items-baseline justify-between gap-2">
								<span class="text-sm text-[#555860]"><span class="text-lg font-semibold tabular-nums text-[#25272B]">{{ item.count }}</span> of 99 clients</span>
								<span class="text-xs font-semibold tabular-nums text-[#858891]">{{ percent(item.count) }}%</span>
							</span>
							<span class="mt-2 block h-2 overflow-hidden rounded-full bg-[#F4F5F7]">
								<span class="block h-full rounded-full transition-[width] duration-500" :class="item.full ? 'bg-[#858891]' : 'bg-[#C8102E]'" :style="{ width: `${percent(item.count)}%` }"></span>
							</span>
							<span class="mt-2.5 block text-xs text-[#858891]">{{ item.remaining }} registration{{ item.remaining === 1 ? '' : 's' }} available</span>
						</button>
					</div>

					<!-- Action bar -->
					<div class="flex flex-col-reverse justify-between gap-3 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-4 sm:flex-row sm:items-center">
						<p class="flex items-start gap-2 text-xs leading-5 text-[#737780]"><Info :size="14" class="mt-0.5 shrink-0 text-[#858891]" /> Each cohort is limited to 99 clients. Cohorts cannot be skipped or reactivated.</p>
						<button type="button" class="btn btn-primary" :disabled="!selected || selected !== nextCohort || saving.loading || selectedCount >= 99" @click="activate">
							<LoaderCircle v-if="saving.loading" :size="16" class="animate-spin" />
							<Check v-else :size="16" />
							{{ `Activate Cohort ${selected || '—'}` }}
						</button>
					</div>
				</section>
			</template>
		</div>

		<!-- Confirmation modal -->
		<Transition name="modal-fade">
			<div v-if="confirmOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1F232D]/45 p-4 backdrop-blur-[2px]" @click.self="closeConfirmation">
				<form class="w-full max-w-lg overflow-hidden rounded-xl border border-[#E4E6EA] bg-white shadow-[0_24px_60px_rgba(31,35,45,0.25)]" role="dialog" aria-modal="true" aria-labelledby="cohort-confirm-title" @submit.prevent="confirmActivation">
					<div class="flex items-start justify-between gap-4 border-b border-[#ECEDEF] px-5 py-4">
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-[#A10E24]">Confirm cohort change</p>
							<h2 id="cohort-confirm-title" class="mt-1 text-base font-semibold text-[#25272B]">Activate Cohort {{ selected }}?</h2>
						</div>
						<button type="button" class="rounded-lg p-1.5 text-[#858891] transition hover:bg-[#F4F5F7] hover:text-[#33353A]" aria-label="Close confirmation" :disabled="saving.loading" @click="closeConfirmation"><X :size="18" /></button>
					</div>

					<div class="space-y-5 px-5 py-5">
						<div class="flex items-start gap-3 rounded-lg border border-[#F0D7A8] bg-[#FFFAF0] p-4 text-sm leading-6 text-[#5D4A25]">
							<AlertTriangle :size="18" class="mt-0.5 shrink-0 text-[#8A4B00]" />
							<div>
								<p>After activation, new client registrations will be assigned to Cohort {{ selected }} and receive codes from that cohort.</p>
								<p class="mt-2">The current active cohort will not be available for new registrations. Existing clients and their codes will stay unchanged. Cohorts activate in order and earlier cohorts cannot be reopened.</p>
							</div>
						</div>

						<!-- Before / after -->
						<div class="grid grid-cols-[1fr_auto_1fr] items-center gap-3 rounded-lg border border-[#ECEDEF] bg-[#FAFAFB] p-3.5">
							<div class="text-center">
								<p class="text-[11px] font-semibold uppercase tracking-wide text-[#858891]">Currently active</p>
								<p class="mt-1 text-sm font-semibold text-[#33353A]">Cohort {{ settings.data?.active_cohort }}</p>
							</div>
							<ArrowRight :size="16" class="text-[#A0A2A8]" />
							<div class="text-center">
								<p class="text-[11px] font-semibold uppercase tracking-wide text-[#A10E24]">Will be active</p>
								<p class="mt-1 text-sm font-semibold text-[#A10E24]">Cohort {{ selected }}</p>
							</div>
						</div>

						<label class="block">
							<span class="mb-1.5 block text-xs font-semibold text-[#555860]">Confirm with your password <span class="text-[#A10E24]">*</span></span>
							<span class="relative block">
								<input v-model="password" class="field pr-11" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required placeholder="Enter your password" />
								<button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-[#858891] transition hover:bg-[#F4F5F7] hover:text-[#33353A]" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">
									<EyeOff v-if="showPassword" :size="16" /><Eye v-else :size="16" />
								</button>
							</span>
						</label>

						<ErrorMessage :message="saving.error" />
					</div>

					<div class="flex flex-col-reverse gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3.5 sm:flex-row sm:justify-end">
						<button type="button" class="btn btn-secondary" :disabled="saving.loading" @click="closeConfirmation">Cancel</button>
						<button type="submit" class="btn btn-primary" :disabled="saving.loading || !password">
							<LoaderCircle v-if="saving.loading" :size="15" class="animate-spin" />
							{{ saving.loading ? 'Activating…' : 'Confirm and activate' }}
						</button>
					</div>
				</form>
			</div>
		</Transition>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, ref } from "vue"
import { AlertTriangle, ArrowRight, Check, CheckCircle2, CircleCheck, Eye, EyeOff, Info, Layers, LoaderCircle, Lock, Users, UserRoundPlus, X } from "lucide-vue-next"

const selected = ref("")
const savedMessage = ref("")
const confirmOpen = ref(false)
const password = ref("")
const showPassword = ref(false)
const nextCohort = computed(() => {
	const active = Number(settings.data?.active_cohort || 0)
	return active >= 9 ? "" : String(active + 1)
})
const settings = createResource({
	url: "krcti_mhpss.api.oversight.programme_cohort_settings",
	auto: true,
	onSuccess(data) { selected.value = Number(data.active_cohort) < 9 ? String(Number(data.active_cohort) + 1) : "" },
})
const selectedCount = computed(() => settings.data?.cohorts?.find((item) => item.cohort === selected.value)?.count || 0)
function canSelect(item) {
	return item.cohort === settings.data?.active_cohort || (item.cohort === nextCohort.value && !item.full)
}
const saving = createResource({
	url: "krcti_mhpss.api.oversight.set_active_cohort",
	method: "POST",
	onSuccess(data) {
		confirmOpen.value = false
		password.value = ""
		showPassword.value = false
		settings.data = data
		selected.value = Number(data.active_cohort) < 9 ? String(Number(data.active_cohort) + 1) : ""
		savedMessage.value = Number(data.active_cohort) < 9
			? `Cohort ${data.active_cohort} is active. The next cohort available for activation is ${Number(data.active_cohort) + 1}. Existing client codes were not changed.`
			: "Cohort 9 is active. All cohorts have now been activated in order. Existing client codes were not changed."
	},
})
function activate() {
	savedMessage.value = ""
	password.value = ""
	showPassword.value = false
	confirmOpen.value = true
}
function closeConfirmation() {
	if (saving.loading) return
	confirmOpen.value = false
	password.value = ""
	showPassword.value = false
}
function confirmActivation() {
	if (!selected.value || !password.value) return
	saving.submit({ cohort: selected.value, password: password.value })
}

// ---- Display helpers ----
const percent = (count) => Math.round(Math.min(100, ((count || 0) / 99) * 100))

function statusOf(item) {
	if (item.cohort === settings.data?.active_cohort) return { label: "Active", pill: "bg-[#FCE8EB] text-[#A10E24]", avatar: "bg-[#FCE8EB] text-[#B30F2A]", icon: CircleCheck }
	if (item.full) return { label: "Full", pill: "bg-[#E4E6EA] text-[#3A3F47]", avatar: "bg-[#F4F5F7] text-[#62656D]", icon: Users }
	if (item.cohort === nextCohort.value) return { label: "Next", pill: "bg-[#FDECC8] text-[#8A4B00]", avatar: "bg-[#FDECC8] text-[#8A4B00]", icon: ArrowRight }
	if (Number(item.cohort) < Number(settings.data?.active_cohort)) return { label: "Completed", pill: "bg-[#DCF3E4] text-[#146C3A]", avatar: "bg-[#DCF3E4] text-[#146C3A]", icon: Check }
	return { label: "Locked", pill: "bg-[#F4F5F7] text-[#737780]", avatar: "bg-[#F4F5F7] text-[#858891]", icon: Lock }
}
function cardClass(item) {
	if (selected.value === item.cohort) return "border-[#C8102E] bg-[#FFF8F9] ring-2 ring-[#C8102E]/10"
	if (!canSelect(item)) return "border-[#E4E6EA] bg-[#FAFAFB] opacity-80"
	return "border-[#E4E6EA] bg-white hover:border-[#BFC2C8] hover:bg-[#FCFCFD]"
}

const activeItem = computed(() => settings.data?.cohorts?.find((item) => item.cohort === settings.data?.active_cohort))
const cards = computed(() => {
	const active = activeItem.value
	const total = (settings.data?.cohorts || []).reduce((sum, item) => sum + (item.count || 0), 0)
	return [
		{ label: "Active cohort", value: `Cohort ${settings.data?.active_cohort ?? "—"}`, hint: "Receiving new registrations", icon: Layers, tone: "bg-[#FCE8EB] text-[#A10E24]" },
		{ label: "Clients in active cohort", value: `${active?.count ?? 0} / 99`, hint: `${percent(active?.count)}% of capacity used`, icon: Users, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
		{ label: "Registrations available", value: active?.remaining ?? 0, hint: "Left in the active cohort", icon: UserRoundPlus, tone: "bg-[#DCF3E4] text-[#146C3A]" },
		{ label: "Next to activate", value: nextCohort.value ? `Cohort ${nextCohort.value}` : "None", hint: `${total} clients across all cohorts`, icon: ArrowRight, tone: "bg-[#FDECC8] text-[#8A4B00]" },
	]
})

function onKeydown(event) {
	if (event.key === "Escape" && confirmOpen.value) closeConfirmation()
}
onMounted(() => document.addEventListener("keydown", onKeydown))
onUnmounted(() => document.removeEventListener("keydown", onKeydown))
</script>

<style scoped>
/* ---- Button system ---- */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid transparent; border-radius: 8px; padding: 10px 16px; font-size: 14px; font-weight: 600; line-height: 20px; white-space: nowrap; transition: background 0.15s, border-color 0.15s, color 0.15s, box-shadow 0.15s; }
.btn:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.2); }
.btn:disabled { cursor: not-allowed; }
.btn-primary { background: #c8102e; color: #fff; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.12); }
.btn-primary:hover:not(:disabled) { background: #a10e24; }
.btn-primary:disabled { background: #c9cbcd; box-shadow: none; }
.btn-secondary { border-color: #d9dbe0; background: #fff; color: #33353a; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.04); }
.btn-secondary:hover:not(:disabled) { border-color: #c8102e; color: #a10e24; }
.btn-secondary:disabled { border-color: #e4e6ea; background: #f7f7f8; color: #a0a2a8; box-shadow: none; }

.field { display: block; width: 100%; min-height: 44px; border: 1px solid #d9dbe0; border-radius: 10px; background: #fff; padding: 10px 12px; font-family: inherit; font-size: 14px; line-height: 20px; color: #33353a; transition: border-color 0.15s, box-shadow 0.15s; }
.field::placeholder { color: #a0a2a8; }
.field:hover { border-color: #bfc2c8; }
.field:focus { outline: none; border-color: #c8102e; box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12); }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.18s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
