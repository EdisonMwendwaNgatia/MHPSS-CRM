<template>
  <div class="pointer-events-none fixed inset-x-0 top-0 z-[80]" role="progressbar" aria-label="Loading" :aria-busy="visible">
    <div v-if="visible" class="h-1 w-full overflow-hidden bg-gp/15">
      <div class="gp-bar-run h-full w-1/3 bg-gp"></div>
    </div>
  </div>

  <div v-if="slow" class="pointer-events-none fixed inset-x-0 top-3 z-[80] flex justify-center px-3" role="status">
    <p class="rounded-full border border-gp-line bg-white px-4 py-1.5 text-sm text-gp-ink shadow">
      Still working... this can take a while on a slow connection.
    </p>
  </div>

  <p
    v-if="offline"
    class="fixed inset-x-0 bottom-0 z-[80] bg-gp-ink px-4 py-2 text-center text-sm text-white"
    role="status"
  >
    You are offline. Things will work again when your connection returns.
  </p>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { busy } from "../data/busy"

const SHOW_AFTER = 150 // ms. Quick actions never flash the bar.
const MIN_VISIBLE = 400 // ms. Once shown, the bar stays long enough to be seen.
const SLOW_AFTER = 10000 // ms

const visible = ref(false)
const slow = ref(false)
const offline = ref(typeof navigator !== "undefined" && navigator.onLine === false)

let showTimer = null
let hideTimer = null
let slowTimer = null
let shownAt = 0

watch(busy, (isBusy) => {
	if (isBusy) {
		clearTimeout(hideTimer)
		if (!visible.value && !showTimer) {
			showTimer = setTimeout(() => {
				showTimer = null
				visible.value = true
				shownAt = Date.now()
			}, SHOW_AFTER)
		}
		if (!slowTimer) slowTimer = setTimeout(() => (slow.value = true), SLOW_AFTER)
		return
	}
	clearTimeout(showTimer)
	showTimer = null
	clearTimeout(slowTimer)
	slowTimer = null
	slow.value = false
	if (visible.value) {
		const wait = Math.max(0, MIN_VISIBLE - (Date.now() - shownAt))
		hideTimer = setTimeout(() => (visible.value = false), wait)
	}
})

const goOnline = () => (offline.value = false)
const goOffline = () => (offline.value = true)
onMounted(() => {
	window.addEventListener("online", goOnline)
	window.addEventListener("offline", goOffline)
})
onBeforeUnmount(() => {
	window.removeEventListener("online", goOnline)
	window.removeEventListener("offline", goOffline)
	clearTimeout(showTimer)
	clearTimeout(hideTimer)
	clearTimeout(slowTimer)
})
</script>

<style>
@keyframes gp-slide {
	0% {
		transform: translateX(-100%);
	}
	100% {
		transform: translateX(400%);
	}
}
.gp-bar-run {
	animation: gp-slide 1.1s ease-in-out infinite;
}
@media (prefers-reduced-motion: reduce) {
	.gp-bar-run {
		animation: none;
		width: 100%;
		opacity: 0.6;
	}
}
</style>