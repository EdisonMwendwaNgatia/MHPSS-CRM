<template>
	<!-- Top progress bar -->
	<div class="pointer-events-none fixed inset-x-0 top-0 z-[80]" role="progressbar" aria-label="Loading" :aria-busy="visible">
		<Transition name="gp-fade">
			<div v-if="visible" class="relative h-[3px] w-full overflow-hidden bg-[#C8102E]/15">
				<div class="gp-bar-run absolute inset-y-0 left-0 w-1/3 rounded-full bg-gradient-to-r from-[#C8102E]/0 via-[#C8102E] to-[#A10E24] shadow-[0_0_10px_rgba(200,16,46,0.55)]"></div>
			</div>
		</Transition>
	</div>

	<!-- Slow connection notice -->
	<Transition name="gp-drop">
		<div v-if="slow" class="pointer-events-none fixed inset-x-0 top-4 z-[80] flex justify-center px-3" role="status" aria-live="polite">
			<div class="flex max-w-md items-start gap-3 rounded-xl border border-[#E4E6EA] bg-white px-4 py-3 shadow-[0_12px_30px_rgba(31,35,45,0.14)]">
				<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#FCE8EB] text-[#C8102E]">
					<LoaderCircle :size="17" class="gp-spin" />
				</span>
				<div class="min-w-0">
					<p class="text-sm font-semibold text-[#25272B]">Still working…</p>
					<p class="mt-0.5 text-xs leading-5 text-[#737780]">This is taking longer than usual, possibly because of a slow connection.</p>
				</div>
			</div>
		</div>
	</Transition>

	<!-- Offline / back online -->
	<Transition name="gp-rise">
		<div v-if="offline || reconnected" class="pointer-events-none fixed inset-x-0 bottom-4 z-[80] flex justify-center px-3" role="status" aria-live="polite">
			<div class="flex max-w-md items-center gap-3 rounded-xl px-4 py-3 shadow-[0_12px_30px_rgba(31,35,45,0.25)]" :class="offline ? 'bg-[#25272B] text-white' : 'bg-[#146C3A] text-white'">
				<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/15">
					<WifiOff v-if="offline" :size="16" /><Wifi v-else :size="16" />
				</span>
				<div class="min-w-0">
					<p class="text-sm font-semibold">{{ offline ? 'You are offline' : 'Back online' }}</p>
					<p class="mt-0.5 text-xs leading-5 text-white/75">{{ offline ? 'Things will work again when your connection returns.' : 'Your connection has been restored.' }}</p>
				</div>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { LoaderCircle, Wifi, WifiOff } from "lucide-vue-next"
import { busy } from "../data/busy"

const SHOW_AFTER = 150 // ms. Quick actions never flash the bar.
const MIN_VISIBLE = 400 // ms. Once shown, the bar stays long enough to be seen.
const SLOW_AFTER = 10000 // ms
const RECONNECT_NOTICE = 3000 // ms. How long "Back online" stays.

const visible = ref(false)
const slow = ref(false)
const offline = ref(typeof navigator !== "undefined" && navigator.onLine === false)
const reconnected = ref(false)

let showTimer = null
let hideTimer = null
let slowTimer = null
let reconnectTimer = null
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

const goOnline = () => {
	offline.value = false
	reconnected.value = true
	clearTimeout(reconnectTimer)
	reconnectTimer = setTimeout(() => (reconnected.value = false), RECONNECT_NOTICE)
}
const goOffline = () => {
	clearTimeout(reconnectTimer)
	reconnected.value = false
	offline.value = true
}
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
	clearTimeout(reconnectTimer)
})
</script>

<style>
@keyframes gp-slide {
	0% { transform: translateX(-100%); }
	100% { transform: translateX(300%); }
}
@keyframes gp-rotate {
	to { transform: rotate(360deg); }
}
.gp-bar-run { animation: gp-slide 1.1s ease-in-out infinite; }
.gp-spin { animation: gp-rotate 0.9s linear infinite; }

.gp-fade-enter-active, .gp-fade-leave-active { transition: opacity 0.2s ease; }
.gp-fade-enter-from, .gp-fade-leave-to { opacity: 0; }

.gp-drop-enter-active, .gp-drop-leave-active,
.gp-rise-enter-active, .gp-rise-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.gp-drop-enter-from, .gp-drop-leave-to { opacity: 0; transform: translateY(-10px); }
.gp-rise-enter-from, .gp-rise-leave-to { opacity: 0; transform: translateY(10px); }

@media (prefers-reduced-motion: reduce) {
	.gp-bar-run { animation: none; width: 100%; opacity: 0.6; }
	.gp-spin { animation: none; }
	.gp-drop-enter-active, .gp-drop-leave-active,
	.gp-rise-enter-active, .gp-rise-leave-active { transition: opacity 0.2s ease; }
	.gp-drop-enter-from, .gp-drop-leave-to,
	.gp-rise-enter-from, .gp-rise-leave-to { transform: none; }
}
</style>
