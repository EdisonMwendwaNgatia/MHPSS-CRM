<template>
	<router-link :to="{ name: routeName, params: { name: clientId } }" class="group flex min-w-0 items-center gap-3">
		<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-xs font-bold text-[#B30F2A]">{{ initials }}</span>
		<span class="min-w-0">
			<span class="block truncate text-sm font-semibold text-[#33353A] group-hover:text-[#B30F2A]">{{ clientName || clientId || "Client" }}</span>
			<span class="mt-0.5 block truncate text-xs text-[#858891]">{{ clientId || "—" }}</span>
		</span>
	</router-link>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	clientId: { type: String, default: "" },
	clientName: { type: String, default: "" },
	routeName: { type: String, default: "ClientProfile" },
})

const initials = computed(() => (props.clientName || "Client").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase())
</script>
