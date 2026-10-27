<template>
  <div
    class="flex flex-col items-center justify-center gap-3 text-gp-muted"
    :class="fullscreen ? 'min-h-screen' : 'py-10'"
    role="status"
    aria-live="polite"
  >
    <Spinner :size="fullscreen ? 36 : 28" />
    <p class="text-sm">{{ label }}</p>
  </div>
</template>

<script setup>
import Spinner from "./Spinner.vue"

defineProps({
	label: { type: String, default: "Loading..." },
	fullscreen: { type: Boolean, default: false },
})
</script>