<template>
  <main class="mx-auto max-w-5xl px-4 py-6 md:px-8 md:py-8">
    <h1 class="text-xl font-semibold text-gp-ink">Hello, {{ first }}</h1>

    <template v-if="role === 'counsellor'">
      <p class="mt-1 text-sm text-gp-muted">Here is your day.</p>
      <PageLoader v-if="home.loading && !home.data" />
      <ErrorMessage class="mt-3" :message="home.error" />

      <template v-if="home.data">
        <div class="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
          <router-link :to="{ name: 'Clients' }" class="rounded-lg border border-gp-line bg-white p-4 hover:border-gp">
            <span class="block text-2xl font-semibold text-gp">{{ home.data.active_clients }}</span>
            <span class="mt-1 block text-sm text-gp-muted">Active clients</span>
          </router-link>
          <router-link :to="{ name: 'Clients' }" class="rounded-lg border border-gp-line bg-white p-4 hover:border-gp">
            <span class="block text-2xl font-semibold" :class="home.data.baselines_outstanding ? 'text-orange-600' : 'text-gp'">
              {{ home.data.baselines_outstanding }}
            </span>
            <span class="mt-1 block text-sm text-gp-muted">Baselines still to record</span>
          </router-link>
          <router-link :to="{ name: 'Appointments' }" class="rounded-lg border border-gp-line bg-white p-4 hover:border-gp">
            <span class="block text-2xl font-semibold" :class="home.data.overdue ? 'text-red-600' : 'text-gp'">
              {{ home.data.overdue }}
            </span>
            <span class="mt-1 block text-sm text-gp-muted">Overdue appointments</span>
          </router-link>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <router-link :to="{ name: 'ClientNew' }" class="rounded-md bg-gp px-4 py-2 text-sm font-medium text-white hover:bg-gp-light">
            Register a client
          </router-link>
          <router-link :to="{ name: 'AppointmentNew' }" class="rounded-md border border-gp-line bg-white px-4 py-2 text-sm font-medium text-gp hover:border-gp">
            Book an appointment
          </router-link>
        </div>

        <section class="mt-6">
          <h2 class="font-semibold text-gp-ink">Today</h2>
          <p v-if="!home.data.today.length" class="mt-2 text-sm text-gp-muted">No appointments today.</p>
          <div v-else class="mt-2 space-y-2">
            <router-link v-for="row in home.data.today" :key="row.name" :to="{ name: 'AppointmentEdit', params: { name: row.name } }"
              class="flex items-center justify-between gap-3 rounded-lg border border-gp-line bg-white p-3 hover:border-gp">
              <span class="min-w-0 text-sm">
                <span class="block font-medium text-gp-ink">{{ fmtTime(row.date_time) }} &middot; {{ row.client_name }}</span>
                <span class="block text-xs text-gp-muted">{{ row.session_type }} &middot; {{ row.mode_of_contact }}</span>
              </span>
              <Badge :label="apptLabel(row)" :theme="apptTheme(row)" />
            </router-link>
          </div>
        </section>

        <section class="mt-6">
          <h2 class="font-semibold text-gp-ink">Coming up</h2>
          <p v-if="!home.data.upcoming.length" class="mt-2 text-sm text-gp-muted">Nothing booked.</p>
          <div v-else class="mt-2 space-y-2">
            <router-link v-for="row in home.data.upcoming" :key="row.name" :to="{ name: 'AppointmentEdit', params: { name: row.name } }"
              class="flex items-center justify-between gap-3 rounded-lg border border-gp-line bg-white p-3 hover:border-gp">
              <span class="min-w-0 text-sm">
                <span class="block font-medium text-gp-ink">{{ row.client_name }}</span>
                <span class="block text-xs text-gp-muted">{{ fmtDateTime(row.date_time) }} &middot; {{ row.session_type }}</span>
              </span>
              <Badge :label="row.mode_of_contact" theme="gray" />
            </router-link>
          </div>
        </section>
      </template>
    </template>

    <p v-else-if="role === 'client'" class="mt-4 rounded-lg border border-gp-line bg-white p-4 text-sm text-gp-ink">
      The client area is coming in a later release.
    </p>
    <PageLoader v-else-if="role" />
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onMounted, watch } from "vue"
import { useRouter } from "vue-router"
import { me } from "../data/me"
import { apptLabel, apptTheme, fmtDateTime, fmtTime } from "../data/format"

const router = useRouter()
const role = computed(() => me.data?.role)
const first = computed(() => (me.data?.full_name || "").split(" ")[0])

const home = createResource({ url: "krcti_mhpss.api.counsellor.home" })

onMounted(() => me.reload())
watch(
	role,
	(value) => {
		if (value === "counsellor") home.submit()
		else if (["krcti_pm", "woc_pm", "admin"].includes(value)) router.replace({ name: "Programme" })
	},
	{ immediate: true },
)
</script>