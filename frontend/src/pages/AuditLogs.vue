<template>
  <main class="min-h-[calc(100vh-72px)] bg-[#F4F5F7] px-4 py-6 sm:px-6 lg:px-8"><div class="mx-auto max-w-[1440px]"><div class="flex flex-wrap items-end justify-between gap-4"><div><p class="text-sm text-[#737780]">Restricted · System Administrator and Data Protection Officer</p><h1 class="mt-1 text-2xl font-semibold text-[#25272B]">Audit logs</h1><p class="mt-1 text-sm text-[#737780]">Append-only record of account and application activity.</p></div><input v-model="search" class="field max-w-sm" type="search" placeholder="Search user, action, or record" aria-label="Search audit logs" /></div><ErrorMessage class="mt-4" :message="logs.error" /><section class="mt-6 overflow-hidden rounded-xl border border-[#E4E6EA] bg-white"><ActivityTable :rows="logs.data?.logs || []" :loading="logs.loading" /><div class="flex items-center justify-between border-t border-[#ECEDEF] px-5 py-3 text-xs text-[#737780]"><span>{{ logs.data?.total || 0 }} entries</span><button v-if="(logs.data?.total || 0) > start + 100" class="quiet" @click="start += 100; load()">Load more</button></div></section></div></main>
</template>
<script setup>
import { createResource } from "frappe-ui"
import { onMounted, ref, watch } from "vue"
import ActivityTable from "../components/ActivityTable.vue"
const logs = createResource({ url: "krcti_mhpss.api.system_admin.admin_audit_logs" })
const search = ref("")
const start = ref(0)
let timer
function load() { logs.submit({ search: search.value, start: start.value, page_length: 100 }) }
watch(search, () => { clearTimeout(timer); start.value = 0; timer = setTimeout(load, 250) })
onMounted(load)
</script>
<style scoped>
.field{display:block;width:100%;height:42px;border:1px solid #d9dbe0;border-radius:9px;background:#fff;padding:0 11px;color:#33353a;font-size:14px}.field:focus{outline:none;border-color:#c8102e;box-shadow:0 0 0 2px #c8102e22}.quiet{border-radius:8px;padding:8px 10px;font-size:13px;font-weight:600;color:#a10e24}.quiet:hover{background:#fce8eb}
</style>
