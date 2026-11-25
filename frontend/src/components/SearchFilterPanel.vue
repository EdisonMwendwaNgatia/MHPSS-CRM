<template>
	<section class="rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)] sm:p-5">
		<div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_230px] md:items-end">
			<label class="block">
				<span class="mb-1.5 block text-xs font-semibold text-[#555860]">{{ searchLabel }}</span>
				<span class="flex h-11 items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3.5 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10">
					<Search :size="17" class="shrink-0 text-[#858891]" />
					<input v-model="searchModel" type="search" :placeholder="placeholder" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
					<button v-if="searchModel" type="button" class="shrink-0 text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="searchModel = ''">Clear</button>
				</span>
			</label>
			<div class="block">
				<span class="mb-1.5 block text-xs font-semibold text-[#555860]">{{ filterLabel }}</span>
				<div class="relative">
					<button type="button" :disabled="disableFilterWhenSearching && isSearching" class="flex h-11 w-full items-center justify-between rounded-lg border border-[#D9DBE0] bg-white px-3.5 text-left text-sm font-medium text-[#33353A] shadow-[0_1px_2px_rgba(20,25,35,0.03)] outline-none transition hover:border-[#BFC2C8] focus:border-[#C8102E] focus:ring-2 focus:ring-[#C8102E]/10 disabled:cursor-not-allowed disabled:border-[#E4E6EA] disabled:bg-[#F7F7F8] disabled:text-[#A0A2A8]" :aria-expanded="menuOpen" aria-haspopup="listbox" @click="menuOpen = !menuOpen" @keydown.esc="menuOpen = false">
						<span class="truncate">{{ selectedOption.label }}</span>
						<ChevronDown :size="16" class="shrink-0 text-[#737780] transition-transform" :class="menuOpen ? 'rotate-180' : ''" />
					</button>
					<div v-if="menuOpen && !(disableFilterWhenSearching && isSearching)" class="absolute left-0 right-0 z-20 mt-2 max-h-72 overflow-y-auto rounded-xl border border-[#E4E6EA] bg-white p-1.5 shadow-[0_12px_30px_rgba(31,35,45,0.14)]" role="listbox" :aria-label="filterAriaLabel">
						<button v-for="option in options" :key="option.value" type="button" role="option" :aria-selected="filterModel === option.value" class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition" :class="filterModel === option.value ? 'bg-[#FCE8EB] font-semibold text-[#A10E24]' : 'text-[#44474E] hover:bg-[#F7F7F8]'" @click="selectOption(option.value)">
							{{ option.label }}
							<Check v-if="filterModel === option.value" :size="16" class="text-[#C8102E]" />
						</button>
					</div>
				</div>
			</div>
		</div>
		<p v-if="isSearching && searchHint" class="mt-3 text-xs text-[#858891]">{{ searchHint }}</p>
	</section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { Check, ChevronDown, Search } from "lucide-vue-next"

const props = defineProps({
	search: { type: String, default: "" },
	filter: { type: [String, Number], default: "" },
	options: { type: Array, required: true },
	searchLabel: { type: String, required: true },
	placeholder: { type: String, required: true },
	filterLabel: { type: String, required: true },
	filterAriaLabel: { type: String, required: true },
	searchHint: { type: String, default: "" },
	searchThreshold: { type: Number, default: 1 },
	disableFilterWhenSearching: { type: Boolean, default: false },
})

const emit = defineEmits(["update:search", "update:filter"])
const menuOpen = ref(false)
const searchModel = computed({ get: () => props.search, set: (value) => emit("update:search", value) })
const filterModel = computed({ get: () => props.filter, set: (value) => emit("update:filter", value) })
const selectedOption = computed(() => props.options.find((option) => option.value === props.filter) || props.options[0] || { label: "" })
const isSearching = computed(() => props.search.trim().length >= props.searchThreshold)

function selectOption(value) {
	filterModel.value = value
	menuOpen.value = false
}

function onOutsideClick(event) {
	if (!event.target.closest('[aria-haspopup="listbox"]') && !event.target.closest('[role="listbox"]')) menuOpen.value = false
}

watch(isSearching, (searching) => {
	if (searching && props.disableFilterWhenSearching) menuOpen.value = false
})
onMounted(() => document.addEventListener("click", onOutsideClick))
onBeforeUnmount(() => document.removeEventListener("click", onOutsideClick))
</script>
