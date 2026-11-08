<template>
	<div class="overflow-x-auto">
		<table class="w-full min-w-[720px] text-left">
			<thead>
				<tr class="bg-[#FAFAFB] text-[11px] font-semibold uppercase tracking-wide text-[#858891]">
					<th class="px-5 py-3">User</th>
					<th class="px-4 py-3">Action</th>
					<th class="px-4 py-3">Record / module</th>
					<th class="px-4 py-3">Outcome</th>
					<th class="px-5 py-3 text-right">Date &amp; time</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-[#F0F1F3]">
				<tr v-for="row in rows || []" :key="row.name" class="align-top transition hover:bg-[#FCFCFD]">
					<td class="px-5 py-3.5">
						<div class="flex items-center gap-3">
							<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold" :class="isSystem(row) ? 'bg-[#F4F5F7] text-[#62656D]' : 'bg-[#FCE8EB] text-[#B30F2A]'">
								<Cog v-if="isSystem(row)" :size="15" /><template v-else>{{ initials(actorLabel(row)) }}</template>
							</span>
							<span class="min-w-0 truncate text-sm font-semibold text-[#33353A]">{{ actorLabel(row) }}</span>
						</div>
					</td>
					<td class="px-4 py-3.5">
						<p class="text-sm font-semibold text-[#33353A]">{{ row.action }}</p>
						<p v-if="row.details" class="mt-1 max-w-xs text-xs leading-5 text-[#858891]">{{ row.details }}</p>
					</td>
					<td class="px-4 py-3.5 text-sm text-[#555860]">
						<span v-if="row.affected_record" class="font-medium">{{ row.affected_record }}</span>
						<span v-else class="text-[#A0A2A8]">—</span>
						<span v-if="row.module" class="mt-1 inline-block rounded-full bg-[#F4F5F7] px-2 py-0.5 text-[11px] font-semibold text-[#62656D]">{{ row.module }}</span>
					</td>
					<td class="px-4 py-3.5">
						<span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="row.outcome === 'Success' ? 'bg-[#DCF3E4] text-[#146C3A]' : 'bg-[#FBE0E4] text-[#A10E24]'">
							<span class="h-1.5 w-1.5 rounded-full" :class="row.outcome === 'Success' ? 'bg-[#146C3A]' : 'bg-[#A10E24]'"></span>{{ row.outcome || '—' }}
						</span>
					</td>
					<td class="whitespace-nowrap px-5 py-3.5 text-right">
						<span class="block text-sm font-medium text-[#555860]">{{ dayLabel(row.creation) }}</span>
						<span class="mt-0.5 block text-xs text-[#858891]">{{ timeLabel(row.creation) }}</span>
					</td>
				</tr>

				<tr v-if="loading">
					<td colspan="5" class="px-5 py-2"><PageLoader label="Loading activity…" /></td>
				</tr>
				<tr v-else-if="!rows?.length">
					<td colspan="5" class="px-5 py-14 text-center">
						<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><Activity :size="22" /></span>
						<p class="mt-3 text-sm font-semibold text-[#33353A]">No recorded activity yet</p>
						<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">Actions will appear here as they happen.</p>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>

<script setup>
import { Activity, Cog } from "lucide-vue-next"

defineProps({ rows: { type: Array, default: () => [] }, loading: { type: Boolean, default: false } })

const actorLabel = (row) => row.actor_name || row.actor || "System"
const isSystem = (row) => !(row.actor_name || row.actor)
const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase()

function toDate(value) {
	if (!value) return null
	const date = new Date(String(value).replace(" ", "T"))
	return Number.isNaN(date.getTime()) ? null : date
}
const dayLabel = (value) => toDate(value)?.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) || "—"
const timeLabel = (value) => toDate(value)?.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" }) || ""
</script>
