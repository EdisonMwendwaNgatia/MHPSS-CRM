<template>
  <svg
    class="animate-spin motion-reduce:animate-none"
    :class="color"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-opacity="0.2" stroke-width="3" />
    <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
  </svg>
</template>

<script setup>
defineProps({
	size: { type: Number, default: 24 },
	color: { type: String, default: "text-gp" },
})
</script>