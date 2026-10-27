<template>
  <main class="mx-auto max-w-4xl px-4 py-6 md:px-8 md:py-8">
    <div class="flex items-end justify-between gap-3">
      <h1 class="text-xl font-semibold text-gp-ink">Clients</h1>
      <router-link :to="{ name: 'ClientNew' }" class="rounded-md bg-gp px-3 py-2 text-sm font-medium text-white hover:bg-gp-light">
        Register a client
      </router-link>
    </div>

    <div class="mt-4 grid gap-3 rounded-lg border border-gp-line bg-white p-4 sm:grid-cols-3">
      <FormControl class="sm:col-span-2" label="Search" type="text" v-model="term" placeholder="Code, name, phone or institution" />
      <FormControl label="Case status" type="select" :options="statusOptions" v-model="status" :disabled="searching" />
    </div>

    <ErrorMessage class="mt-3" :message="list.error || search.error" />
    <PageLoader v-if="(list.loading || search.loading) && !rows.length" />
    <p v-else-if="!rows.length" class="mt-3 rounded-lg border border-gp-line bg-white p-4 text-sm text-gp-muted">
      {{ searching ? "No client matches your search." : "You have no clients yet." }}
    </p>

    <div class="mt-3 space-y-2">
      <router-link v-for="row in rows" :key="row.name" :to="{ name: 'ClientProfile', params: { name: row.name } }"
        class="flex items-center justify-between gap-3 rounded-lg border border-gp-line bg-white p-4 hover:border-gp">
        <span class="min-w-0">
          <span class="block truncate font-medium text-gp-ink">{{ row.full_name }}</span>
          <span class="block text-xs text-gp-muted">{{ row.scholar_code }} &middot; {{ row.institution }} &middot; {{ row.phone_number }}</span>
        </span>
        <Badge :label="row.case_status" :theme="caseTheme(row.case_status)" />
      </router-link>
    </div>
    <p v-if="!searching && total > rows.length" class="mt-3 text-center text-xs text-gp-muted">
      Showing {{ rows.length }} of {{ total }}. Use the search to find the rest.
    </p>
  </main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { caseTheme } from "../data/format"

const term = ref("")
const status = ref("")
const statusOptions = [
	{ label: "All", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Follow-Up Pending", value: "Follow-Up Pending" },
	{ label: "Closed", value: "Closed" },
]

const list = createResource({ url: "krcti_mhpss.api.counsellor.list_clients" })
const search = createResource({ url: "krcti_mhpss.api.counsellor.search_clients" })

const searching = computed(() => term.value.trim().length >= 2)
const rows = computed(() => (searching.value ? search.data || [] : list.data?.data || []))
const total = computed(() => list.data?.total || 0)

let timer = null
watch([term, status], () => {
	clearTimeout(timer)
	timer = setTimeout(() => {
		if (searching.value) search.submit({ term: term.value.trim() })
		else list.submit({ status: status.value || undefined, page_length: 50 })
	}, 300)
})
onBeforeUnmount(() => clearTimeout(timer))
onMounted(() => list.submit({ page_length: 50 }))
</script>