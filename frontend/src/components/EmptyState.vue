<template>
	<div class="px-5 py-14 text-center">
		<span v-if="icon" class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><component :is="icon" :size="22" /></span>
		<p class="mt-3 text-sm font-semibold text-[#33353A]">{{ title }}</p>
		<p class="mx-auto mt-1 max-w-sm text-sm text-[#858891]">{{ description }}</p>
		<div v-if="$slots.default" class="mt-4 flex justify-center">
			<slot />
		</div>
	</div>
</template>

<script setup>
defineProps({
	title: { type: String, required: true },
	description: { type: String, required: true },
	icon: { type: [Object, Function], default: null },
})
</script>
