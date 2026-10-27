<template>
  <main class="mx-auto max-w-4xl px-4 py-6 md:px-8 md:py-8">
    <div class="flex items-end justify-between gap-3">
      <h1 class="text-xl font-semibold text-gp-ink">Appointments</h1>
      <router-link :to="{ name: 'AppointmentNew' }" class="rounded-md bg-gp px-3 py-2 text-sm font-medium text-white hover:bg-gp-light">Book an appointment</router-link>
    </div>

    <div class="mt-4 flex items-center justify-between rounded-lg border border-gp-line bg-white p-3">
      <Button @click="shift(-14)">&larr; Earlier</Button>
      <p class="text-sm font-medium text-gp-ink">{{ fmtDate(from) }} to {{ fmtDate(to) }}</p>
      <Button @click="shift(14)">Later &rarr;</Button>
    </div>

    <p v-if="data?.overdue_total" class="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-gp-ink">
      {{ data.overdue_total }} appointment{{ data.overdue_total === 1 ? " has" : "s have" }} passed without being completed. Complete or cancel {{ data.overdue_total === 1 ? "it" : "them" }}.
    </p>

    <ErrorMessage class="mt-3" :message="list.error || action.error" />
    <PageLoader v-if="list.loading && !data" />
    <p v-else-if="data && !data.appointments.length" class="mt-3 rounded-lg border border-gp-line bg-white p-4 text-sm text-gp-muted">Nothing booked in this period.</p>

    <section v-for="day in days" :key="day.key" class="mt-4">
      <h2 class="text-sm font-semibold text-gp-ink">{{ fmtDate(day.key) }}</h2>
      <div class="mt-2 space-y-2">
        <div v-for="a in day.rows" :key="a.name" class="rounded-lg border border-gp-line bg-white p-3">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 text-sm">
              <router-link :to="{ name: 'ClientProfile', params: { name: a.client_id } }" class="font-medium text-gp">{{ a.client_name }}</router-link>
              <p class="text-xs text-gp-muted">{{ fmtTime(a.date_time) }} &middot; {{ a.session_type }} &middot; {{ a.mode_of_contact }}<span v-if="a.location"> &middot; {{ a.location }}</span></p>
            </div>
            <Badge :label="apptLabel(a)" :theme="apptTheme(a)" />
          </div>
          <div v-if="a.status === 'Scheduled'" class="mt-3 flex flex-wrap gap-2">
            <Button :loading="action.loading" @click="setStatus(a, 'Completed')">Mark completed</Button>
            <router-link :to="{ name: 'AppointmentEdit', params: { name: a.name } }" class="rounded-md border border-gp-line px-3 py-1.5 text-sm font-medium text-gp hover:border-gp">Edit</router-link>
            <Button theme="red" :loading="action.loading" @click="cancel(a)">Cancel</Button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { apptLabel, apptTheme, dayKey, fmtDate, fmtTime } from "../data/format"

const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const addDays = (value, n) => {
	const d = new Date(`${value}T00:00:00`)
	d.setDate(d.getDate() + n)
	return iso(d)
}

const from = ref(iso(new Date()))
const to = computed(() => addDays(from.value, 13))

const list = createResource({ url: "krcti_mhpss.api.counsellor.my_appointments" })
const data = computed(() => list.data)
const load = () => list.submit({ date_from: from.value, date_to: to.value })
onMounted(load)

function shift(n) {
	from.value = addDays(from.value, n)
	load()
}

const days = computed(() => {
	const groups = {}
	for (const a of data.value?.appointments || []) (groups[dayKey(a.date_time)] ||= []).push(a)
	return Object.keys(groups).sort().map((key) => ({ key, rows: groups[key] }))
})

const action = createResource({ url: "krcti_mhpss.api.records.set_appointment_status", onSuccess: load })
const setStatus = (a, status) => action.submit({ name: a.name, status })
function cancel(a) {
	if (window.confirm(`Cancel the appointment with ${a.client_name}?`)) setStatus(a, "Cancelled")
}
</script>