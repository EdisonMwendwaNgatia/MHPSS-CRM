<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 text-[#25272B] sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1040px]">
			<div class="flex items-start gap-3">
				<span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#FCE8EB] text-[#A10E24]"><Settings :size="20" /></span>
				<div>
					<p class="text-sm font-medium text-[#737780]">Programme oversight</p>
					<h1 class="mt-0.5 text-2xl font-semibold tracking-tight sm:text-[28px]">Programme settings</h1>
					<p class="mt-1 text-sm text-[#737780]">Manage which cohort receives new client registrations.</p>
				</div>
			</div>

			<ErrorMessage class="mt-5" :message="settings.error || saving.error" />
			<div v-if="savedMessage" class="mt-5 rounded-lg border border-[#B8E0C6] bg-[#F0FAF3] px-4 py-3 text-sm font-medium text-[#176B37]" role="status">{{ savedMessage }}</div>
			<PageLoader v-if="settings.loading && !settings.data" />
			<section v-else-if="settings.data" class="mt-6 rounded-xl border border-[#E4E6EA] bg-white p-5 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-6">
				<div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
					<div>
						<h2 class="text-base font-semibold">Client cohort allocation</h2>
						<p class="mt-1 max-w-2xl text-sm leading-6 text-[#737780]">Cohorts activate in order. You can move forward by one cohort at a time; previous cohorts cannot be reopened. Existing client records and codes remain unchanged.</p>
					</div>
					<span class="inline-flex w-fit shrink-0 items-center rounded-full bg-[#FCE8EB] px-3 py-1.5 text-xs font-semibold text-[#A10E24]">Active: Cohort {{ settings.data.active_cohort }}</span>
				</div>

				<div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					<button v-for="item in settings.data.cohorts" :key="item.cohort" type="button" :disabled="!canSelect(item)" class="rounded-xl border p-4 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30 disabled:cursor-not-allowed disabled:opacity-55" :class="selected === item.cohort ? 'border-[#C8102E] bg-[#FFF9FA] ring-1 ring-[#C8102E]/15' : 'border-[#E4E6EA] bg-white hover:border-[#C7A0A6] hover:bg-[#FCFCFD]'" :aria-pressed="selected === item.cohort" @click="selected = item.cohort; savedMessage = ''">
						<span class="flex items-center justify-between gap-2">
							<span class="font-semibold">Cohort {{ item.cohort }}</span>
							<span v-if="item.cohort === settings.data.active_cohort" class="rounded-full bg-[#FCE8EB] px-2 py-1 text-[11px] font-semibold text-[#A10E24]">Active</span>
							<span v-else-if="item.full" class="rounded-full bg-[#F1F2F4] px-2 py-1 text-[11px] font-semibold text-[#737780]">Full</span>
							<span v-else-if="item.cohort === nextCohort" class="rounded-full bg-[#FFF4E5] px-2 py-1 text-[11px] font-semibold text-[#8A5200]">Next</span>
							<span v-else-if="Number(item.cohort) < Number(settings.data.active_cohort)" class="rounded-full bg-[#F1F2F4] px-2 py-1 text-[11px] font-semibold text-[#737780]">Completed</span>
							<span v-else class="rounded-full bg-[#F1F2F4] px-2 py-1 text-[11px] font-semibold text-[#737780]">Locked</span>
						</span>
						<span class="mt-3 block text-sm text-[#737780]">{{ item.count }} of 99 clients</span>
						<span class="mt-2 block h-1.5 overflow-hidden rounded-full bg-[#EEF0F3]"><span class="block h-full rounded-full bg-[#C8102E]" :style="{ width: `${Math.min(100, item.count / 99 * 100)}%` }"></span></span>
						<span class="mt-2 block text-xs text-[#858891]">{{ item.remaining }} registration{{ item.remaining === 1 ? '' : 's' }} available</span>
					</button>
				</div>

				<div class="mt-5 flex flex-col-reverse justify-between gap-3 border-t border-[#ECEDEF] pt-5 sm:flex-row sm:items-center">
					<p class="text-xs leading-5 text-[#737780]">Each cohort is limited to 99 clients. Cohorts cannot be skipped or reactivated.</p>
					<button type="button" :disabled="!selected || selected !== nextCohort || saving.loading || selectedCount >= 99" class="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[#C8102E] px-4 text-sm font-semibold text-white transition hover:bg-[#A10E24] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E]/30 disabled:cursor-not-allowed disabled:bg-[#C9CBCD]" @click="activate">
						<LoaderCircle v-if="saving.loading" :size="16" class="animate-spin" />
						<Check v-else :size="16" />
						{{ saving.loading ? 'Saving…' : `Activate Cohort ${selected || '—'}` }}
					</button>
				</div>
			</section>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, ref } from "vue"
import { Check, LoaderCircle, Settings } from "lucide-vue-next"

const selected = ref("")
const savedMessage = ref("")
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
		settings.data = data
		selected.value = Number(data.active_cohort) < 9 ? String(Number(data.active_cohort) + 1) : ""
		savedMessage.value = Number(data.active_cohort) < 9
			? `Cohort ${data.active_cohort} is active. The next cohort available for activation is ${Number(data.active_cohort) + 1}. Existing client codes were not changed.`
			: "Cohort 9 is active. All cohorts have now been activated in order. Existing client codes were not changed."
	},
})
function activate() {
	savedMessage.value = ""
	saving.submit({ cohort: selected.value })
}
</script>
