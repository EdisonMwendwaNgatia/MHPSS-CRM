<template>
  <main class="mx-auto max-w-xl px-4 py-6 md:px-8 md:py-8">
    <router-link :to="{ name: 'Appointments' }" class="text-sm text-gp">&larr; Appointments</router-link>
    <h1 class="mt-1 text-xl font-semibold text-gp-ink">{{ isNew ? "Book an appointment" : "Edit appointment" }}</h1>
    <PageLoader v-if="loading" />

    <form v-else class="mt-4 space-y-4 rounded-lg border border-gp-line bg-white p-5" @submit.prevent="save">
      <div v-if="isNew">
        <FormControl label="Client" type="text" v-model="term" placeholder="Search by code, name or phone" />
        <p v-if="chosen" class="mt-1 text-sm font-medium text-gp">Selected: {{ chosen.full_name }} ({{ chosen.scholar_code }})</p>
        <div v-else-if="found.length" class="mt-1 divide-y divide-gp-line rounded-md border border-gp-line">
          <button v-for="row in found" :key="row.name" type="button" class="block w-full px-3 py-2 text-left text-sm hover:bg-gp-bg" @click="choose(row)">
            {{ row.full_name }} <span class="text-gp-muted">&middot; {{ row.scholar_code }} &middot; {{ row.institution }}</span>
          </button>
        </div>
        <button v-if="chosen" type="button" class="mt-1 text-xs text-gp" @click="chosen = null">Choose a different client</button>
      </div>
      <p v-else class="text-sm text-gp-ink">Client: <span class="font-medium">{{ clientLabel }}</span></p>

      <FormControl label="Date and time" type="datetime-local" v-model="form.date_time" />
      <FormControl label="Duration (minutes)" type="number" v-model="form.duration_minutes" />
      <FormControl label="Session type" type="select" :options="SESSION_TYPES" v-model="form.session_type" />
      <FormControl label="Mode of contact" type="select" :options="MODES" v-model="form.mode_of_contact" />
      <FormControl v-if="physical" label="Physical location" type="text" v-model="form.location" />
      <FormControl label="Notes (optional)" type="textarea" v-model="form.notes" />

      <ErrorMessage :message="saver.error || updater.error" />
      <Button type="submit" variant="solid" class="w-full !bg-gp hover:!bg-gp-light" :loading="saver.loading || updater.loading">
        {{ isNew ? "Book appointment" : "Save changes" }}
      </Button>
    </form>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { fromInput, toInput } from "../data/format"
import { MODES, PHYSICAL_MODES, SESSION_TYPES } from "../data/options"

const props = defineProps({ name: { type: String, default: "" } })
const route = useRoute()
const router = useRouter()
const apptName = computed(() => props.name || route.params.name || "")
const isNew = computed(() => !apptName.value)

const form = reactive({ date_time: "", duration_minutes: 60, session_type: "", mode_of_contact: "", location: "", notes: "" })
const physical = computed(() => PHYSICAL_MODES.includes(form.mode_of_contact))
const loading = ref(false)
const clientLabel = ref("")
const clientId = ref("")

// Choosing a client when booking
const term = ref("")
const chosen = ref(null)
const found = ref([])
const search = createResource({
	url: "krcti_mhpss.api.counsellor.search_clients",
	onSuccess(rows) {
		found.value = rows
	},
})
let timer = null
watch(term, (value) => {
	clearTimeout(timer)
	if (chosen.value || value.trim().length < 2) return (found.value = [])
	timer = setTimeout(() => search.submit({ term: value.trim() }), 300)
})
onBeforeUnmount(() => clearTimeout(timer))
function choose(row) {
	chosen.value = row
	clientId.value = row.name
	found.value = []
}

// Editing
const existing = createResource({
	url: "krcti_mhpss.api.records.appointment_detail",
	onSuccess(doc) {
		clientId.value = doc.client_id
		clientLabel.value = `${doc.client_name} (${doc.scholar_code})`
		Object.assign(form, {
			date_time: toInput(doc.date_time), duration_minutes: doc.duration_minutes, session_type: doc.session_type,
			mode_of_contact: doc.mode_of_contact, location: doc.location || "", notes: doc.notes || "",
		})
		loading.value = false
	},
})

onMounted(() => {
	if (!isNew.value) {
		loading.value = true
		existing.submit({ name: apptName.value })
	} else if (route.query.client) {
		search.submit({ term: String(route.query.client) })
		const stop = watch(found, (rows) => {
			const match = rows.find((r) => r.name === route.query.client)
			if (match) {
				choose(match)
				stop()
			}
		})
	}
})

const toValues = () => ({
	date_time: fromInput(form.date_time),
	duration_minutes: Number(form.duration_minutes) || 60,
	session_type: form.session_type,
	mode_of_contact: form.mode_of_contact,
	location: physical.value ? form.location : "",
	notes: form.notes,
})

const saver = createResource({
	url: "krcti_mhpss.api.records.save_appointment",
	onSuccess() {
		router.replace({ name: "Appointments" })
	},
})
const updater = saver // the template may still mention it

function save() {
	saver.submit({ name: apptName.value || undefined, client: clientId.value, data: toValues() })
}
</script>