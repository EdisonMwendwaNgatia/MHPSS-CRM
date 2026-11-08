<template>
	<svg
		class="spinner-rotate"
		:class="color"
		:width="size"
		:height="size"
		viewBox="0 0 24 24"
		fill="none"
		role="img"
		aria-label="Loading"
	>
		<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-opacity="0.18" stroke-width="2.5" />
		<path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
	</svg>
</template>

<script setup>
defineProps({
	size: { type: Number, default: 24 },
	// Any Tailwind text colour class works, e.g. "text-white" on a red button
	color: { type: String, default: "text-[#C8102E]" },
})
</script>

<style scoped>
.spinner-rotate { animation: spinner-rotate 0.8s linear infinite; }
@keyframes spinner-rotate {
	to { transform: rotate(360deg); }
}
@media (prefers-reduced-motion: reduce) {
	.spinner-rotate { animation-duration: 2.4s; }
}
</style>
