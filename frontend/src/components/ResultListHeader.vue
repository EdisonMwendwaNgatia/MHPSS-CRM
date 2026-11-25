<template>
	<div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#ECEDEF] px-5 py-4">
		<div>
			<h2 class="text-base font-semibold text-[#25272B]">{{ title }}</h2>
			<p class="mt-0.5 text-xs text-[#858891]">{{ description }}</p>
		</div>
		<div v-if="countLabel !== null || loading" class="flex items-center gap-2">
			<LoaderCircle v-if="loading" :size="16" class="animate-spin text-[#858891]" />
			<span v-if="countLabel !== null" class="rounded-full bg-[#F4F5F7] px-2.5 py-1 text-xs font-semibold text-[#62656D]">{{ count }} {{ countLabel }}</span>
		</div>
	</div>
</template>

<script setup>
import { LoaderCircle } from "lucide-vue-next"

defineProps({
	title: { type: String, required: true },
	description: { type: String, required: true },
	count: { type: [String, Number], default: 0 },
	countLabel: { type: String, default: null },
	loading: { type: Boolean, default: false },
})
</script>
