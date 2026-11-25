<template>
	<div class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1F232D]/50 p-3 backdrop-blur-[2px] sm:p-5" @click.self="$emit('close')">
		<section class="flex max-h-[94vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-[#E4E6EA] bg-white shadow-[0_24px_70px_rgba(20,25,35,0.3)]" role="dialog" aria-modal="true" aria-labelledby="export-title">
			<header class="flex items-start justify-between gap-4 border-b border-[#ECEDEF] px-5 py-4 sm:px-6">
				<div><p class="text-xs font-semibold uppercase tracking-wide text-[#A10E24]">Programme data</p><h2 id="export-title" class="mt-1 text-lg font-semibold">Export Excel workbook</h2><p class="mt-1 text-sm text-[#737780]">Choose records, filters, and fields. Charts are not included.</p></div>
				<button type="button" class="rounded-lg p-2 text-[#737780] hover:bg-[#F4F5F7]" aria-label="Close" @click="$emit('close')"><X :size="18" /></button>
			</header>

			<div class="min-h-0 flex-1 space-y-5 overflow-y-auto px-5 py-5 sm:px-6">
				<ErrorMessage :message="options.error || preview.error" />
				<div class="grid gap-4 sm:grid-cols-2">
					<label class="block"><span class="mb-1.5 block text-xs font-semibold text-[#555860]">Data to export</span><select v-model="dataType" class="export-field"><option v-for="(dataset, key) in datasets" :key="key" :value="key">{{ dataset.label }}</option></select></label>
					<div class="rounded-lg border border-[#E4E6EA] bg-[#FAFAFB] px-3.5 py-3 text-sm text-[#555860]">
						<LoaderCircle v-if="preview.loading" :size="16" class="mr-2 inline animate-spin text-[#858891]" />
						<strong class="text-[#25272B]">{{ preview.data?.count ?? "—" }}</strong> matching records
						<p v-if="preview.data?.truncated" class="mt-1 text-xs text-[#A10E24]">Exports are limited to {{ preview.data.limit.toLocaleString() }} records. Add filters to narrow the results.</p>
					</div>
				</div>

				<section class="rounded-xl border border-[#E4E6EA] p-4">
					<h3 class="text-sm font-semibold">Filters</h3>
					<div v-if="dataType === 'clients'" class="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
						<label class="block"><span class="export-label">Cohort</span><select v-model="filters.cohort" class="export-field"><option value="">All cohorts</option><option v-for="cohort in optionData.cohorts" :key="cohort" :value="cohort">Cohort {{ cohort }}</option></select></label>
						<label class="block"><span class="export-label">Case status</span><select v-model="filters.case_status" class="export-field"><option value="">All statuses</option><option v-for="status in optionData.case_statuses" :key="status" :value="status">{{ status }}</option></select></label>
						<label class="block"><span class="export-label">Counsellor</span><select v-model="filters.assigned_counsellor" class="export-field"><option value="">All counsellors</option><option v-for="person in optionData.counsellors" :key="person.value" :value="person.value">{{ person.label }}</option></select></label>
						<label class="block"><span class="export-label">Programme stream</span><select v-model="filters.programme_stream" class="export-field"><option value="">All streams</option><option v-for="stream in optionData.programme_streams" :key="stream" :value="stream">{{ stream }}</option></select></label>
						<label class="block"><span class="export-label">Institution</span><input v-model="filters.institution" class="export-field" placeholder="Exact institution name" /></label>
						<label class="block"><span class="export-label">Search</span><input v-model="filters.search" class="export-field" placeholder="Name, code, phone, institution" /></label>
					</div>
					<div v-else-if="dataType === 'counsellors'" class="mt-3 grid gap-3 sm:grid-cols-2">
						<label class="block"><span class="export-label">Account status</span><select v-model="filters.enabled" class="export-field"><option value="">All counsellors</option><option value="1">Enabled</option><option value="0">Disabled</option></select></label>
						<label class="block"><span class="export-label">Search</span><input v-model="filters.search" class="export-field" placeholder="Name, email, user ID" /></label>
					</div>
					<div v-else class="mt-3 space-y-3">
						<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
							<label class="block"><span class="export-label">{{ dataType === 'sessions' ? 'Session status' : 'Baseline status' }}</span><select v-model="filters.status" class="export-field"><option value="">All statuses</option><option v-for="status in (dataType === 'sessions' ? optionData.session_statuses : optionData.baseline_statuses)" :key="status" :value="status">{{ status }}</option></select></label>
							<label v-if="dataType === 'sessions'" class="block"><span class="export-label">Session type</span><select v-model="filters.session_type" class="export-field"><option value="">All types</option><option v-for="type in optionData.session_types" :key="type" :value="type">{{ type }}</option></select></label>
							<label v-if="dataType === 'sessions'" class="block"><span class="export-label">Counsellor</span><select v-model="filters.counsellor_id" class="export-field"><option value="">All counsellors</option><option v-for="person in optionData.counsellors" :key="person.value" :value="person.value">{{ person.label }}</option></select></label>
							<label v-if="dataType === 'baselines'" class="block"><span class="export-label">Cycle</span><select v-model="filters.cycle" class="export-field"><option value="">All cycles</option><option v-for="cycle in optionData.baseline_cycles" :key="cycle" :value="cycle">{{ cycle }}</option></select></label>
							<label v-if="dataType === 'baselines'" class="block"><span class="export-label">Review status</span><select v-model="filters.review_status" class="export-field"><option value="">All review statuses</option><option v-for="status in optionData.baseline_review_statuses" :key="status" :value="status">{{ status }}</option></select></label>
							<label class="block"><span class="export-label">From</span><input v-model="filters.date_from" type="date" class="export-field" /></label>
							<label class="block"><span class="export-label">To</span><input v-model="filters.date_to" type="date" class="export-field" /></label>
						</div>
						<div>
							<label class="export-label">Specific clients <span class="font-normal text-[#858891]">(leave empty for all matching clients)</span></label>
							<input v-model="clientSearch" class="export-field" placeholder="Search by client name, code, or ID" />
							<div v-if="clientOptions.data?.length" class="mt-2 max-h-36 overflow-y-auto rounded-lg border border-[#E4E6EA]">
								<label v-for="client in clientOptions.data" :key="client.name" class="flex cursor-pointer items-center gap-2.5 border-b border-[#F0F1F3] px-3 py-2 text-sm last:border-0 hover:bg-[#FAFAFB]">
									<input type="checkbox" :checked="filters.client_ids.includes(client.name)" @change="toggleClient(client.name)" />
									<span class="min-w-0 flex-1 truncate">{{ client.full_name || client.name }} <span class="text-xs text-[#858891]">{{ client.scholar_code || client.name }}</span></span>
								</label>
							</div>
							<div v-if="filters.client_ids.length" class="mt-2 flex flex-wrap gap-1.5"><button v-for="id in filters.client_ids" :key="id" type="button" class="rounded-full bg-[#FCE8EB] px-2.5 py-1 text-xs font-medium text-[#A10E24]" @click="toggleClient(id)">{{ clientLabels[id] || id }} ×</button></div>
						</div>
					</div>
				</section>

				<section class="rounded-xl border border-[#E4E6EA] p-4">
					<div class="flex flex-wrap items-center justify-between gap-3">
						<div><h3 class="text-sm font-semibold">Fields to include</h3><p class="mt-1 text-xs text-[#737780]">Timestamps such as Created On and Modified are selectable fields.</p></div>
						<div class="flex gap-3 text-xs font-semibold"><button type="button" class="text-[#A10E24] hover:underline" @click="selectedFields = visibleFields.map((field) => field.field)">Select shown</button><button type="button" class="text-[#A10E24] hover:underline" @click="selectedFields = []">Clear</button></div>
					</div>
					<input v-model="fieldSearch" class="export-field mt-3" placeholder="Find a field" />
					<div class="mt-3 grid max-h-56 gap-1 overflow-y-auto sm:grid-cols-2 lg:grid-cols-3">
						<label v-for="field in visibleFields" :key="field.field" class="flex min-w-0 cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-[#FAFAFB]">
							<input v-model="selectedFields" type="checkbox" :value="field.field" />
							<span class="truncate" :title="field.label">{{ field.label }}</span>
							<span v-if="['Date', 'Datetime', 'Time'].includes(field.fieldtype)" class="shrink-0 text-[10px] text-[#858891]">time</span>
						</label>
					</div>
					<p class="mt-2 text-xs text-[#737780]">{{ selectedFields.length }} field{{ selectedFields.length === 1 ? '' : 's' }} selected</p>
				</section>
			</div>

			<footer class="flex flex-col-reverse gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
				<p class="text-xs text-[#737780]">Exports are limited to {{ preview.data?.limit?.toLocaleString?.() || '25,000' }} rows per workbook.</p>
				<div class="flex justify-end gap-2"><button type="button" class="export-secondary" @click="$emit('close')">Cancel</button><button type="button" class="export-primary" :disabled="!selectedFields.length || !preview.data?.count || preview.data?.truncated" @click="download"><Download :size="16" /> Download Excel</button></div>
			</footer>
		</section>
	</div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue"
import { Download, LoaderCircle, X } from "lucide-vue-next"

defineEmits(["close"])

const options = createResource({ url: "krcti_mhpss.api.oversight.programme_export_options", auto: true })
const preview = createResource({ url: "krcti_mhpss.api.oversight.programme_export_preview" })
const clientOptions = createResource({ url: "krcti_mhpss.api.oversight.programme_export_client_options" })
const dataType = ref("clients")
const selectedFields = ref([])
const filters = reactive({ cohort: "", case_status: "", assigned_counsellor: "", programme_stream: "", institution: "", search: "", enabled: "", status: "", session_type: "", counsellor_id: "", cycle: "", review_status: "", date_from: "", date_to: "", client_ids: [] })
const clientSearch = ref("")
const clientLabels = reactive({})
const fieldSearch = ref("")
let previewTimer
let clientTimer

const optionData = computed(() => options.data || {})
const datasets = computed(() => optionData.value.datasets || {})
const fields = computed(() => datasets.value[dataType.value]?.fields || [])
const visibleFields = computed(() => {
	const query = fieldSearch.value.trim().toLowerCase()
	return fields.value.filter((field) => !query || field.label.toLowerCase().includes(query) || field.field.toLowerCase().includes(query))
})
const exportFilters = computed(() => {
	const result = {}
	for (const [key, value] of Object.entries(filters)) {
		if (key === "client_ids") {
			if (value.length) result.client_ids = value
		} else if (value !== "") result[key] = value
	}
	return result
})

function refreshPreview() {
	clearTimeout(previewTimer)
	previewTimer = setTimeout(() => preview.submit({ data_type: dataType.value, filters: JSON.stringify(exportFilters.value) }), 250)
}

function toggleClient(id) {
	const selected = new Set(filters.client_ids)
	if (selected.has(id)) selected.delete(id)
	else selected.add(id)
	filters.client_ids = [...selected]
}

function download() {
	const params = new URLSearchParams({ data_type: dataType.value, filters: JSON.stringify(exportFilters.value), fields: JSON.stringify(selectedFields.value) })
	window.location.assign(`/api/method/krcti_mhpss.api.oversight.export_programme_data?${params.toString()}`)
}

watch(dataType, (type) => {
	Object.assign(filters, { cohort: "", case_status: "", assigned_counsellor: "", programme_stream: "", institution: "", search: "", enabled: "", status: "", session_type: "", counsellor_id: "", cycle: "", review_status: "", date_from: "", date_to: "", client_ids: [] })
	selectedFields.value = [...(datasets.value[type]?.defaults || [])]
	refreshPreview()
})
watch(filters, refreshPreview, { deep: true })
watch(clientSearch, (search) => {
	clearTimeout(clientTimer)
	clientTimer = setTimeout(() => clientOptions.submit({ search }), 250)
})
watch(() => clientOptions.data, (rows) => {
	for (const row of rows || []) clientLabels[row.name] = row.full_name || row.name
})
watch(() => options.data, (data) => {
	selectedFields.value = [...(data?.datasets?.[dataType.value]?.defaults || [])]
	refreshPreview()
})

onMounted(() => {
	clientOptions.submit({ search: "" })
})
onBeforeUnmount(() => {
	clearTimeout(previewTimer)
	clearTimeout(clientTimer)
})
</script>

<style scoped>
.export-label { display: block; margin-bottom: 6px; color: #555860; font-size: 12px; font-weight: 600; }
.export-field { display: block; width: 100%; min-height: 40px; border: 1px solid #d9dbe0; border-radius: 8px; background: #fff; padding: 8px 10px; color: #33353a; font-size: 13px; }
.export-field:focus { border-color: #c8102e; outline: 2px solid rgba(200, 16, 46, 0.1); }
.export-primary, .export-secondary { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border-radius: 8px; padding: 9px 14px; font-size: 13px; font-weight: 600; }
.export-primary { background: #c8102e; color: #fff; }
.export-primary:hover:not(:disabled) { background: #a10e24; }
.export-primary:disabled { cursor: not-allowed; background: #c9cbcd; }
.export-secondary { border: 1px solid #d9dbe0; background: #fff; color: #33353a; }
</style>
