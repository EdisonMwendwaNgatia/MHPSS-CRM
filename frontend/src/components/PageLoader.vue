<template>
	<div
		class="flex flex-col items-center justify-center text-center"
		:class="fullscreen ? 'min-h-screen bg-[#F4F5F7] px-4' : 'py-8'"
		role="status"
		aria-live="polite"
	>
		<span
			class="relative flex items-center justify-center rounded-full bg-[#FCE8EB]"
			:class="fullscreen ? 'h-20 w-20' : 'h-14 w-14'"
		>
			<svg
				class="pl-spin"
				:class="fullscreen ? 'h-9 w-9' : 'h-6 w-6'"
				viewBox="0 0 24 24"
				fill="none"
				aria-hidden="true"
			>
				<circle cx="12" cy="12" r="9" stroke="#C8102E" stroke-opacity="0.18" stroke-width="2.5" />
				<path d="M21 12a9 9 0 0 0-9-9" stroke="#C8102E" stroke-width="2.5" stroke-linecap="round" />
			</svg>
		</span>

		<p class="mt-4 font-semibold text-[#33353A]" :class="fullscreen ? 'text-base' : 'text-sm'">{{ label }}</p>
		<p v-if="fullscreen" class="mt-1 text-sm text-[#858891]">Please wait a moment.</p>
	</div>
</template>

<script setup>
defineProps({
	label: { type: String, default: "Loading..." },
	fullscreen: { type: Boolean, default: false },
})
</script>

<style scoped>
.pl-spin { animation: pl-rotate 0.8s linear infinite; }
@keyframes pl-rotate {
	to { transform: rotate(360deg); }
}
@media (prefers-reduced-motion: reduce) {
	.pl-spin { animation-duration: 2.4s; }
}
</style>
