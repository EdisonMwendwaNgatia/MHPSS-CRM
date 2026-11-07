<template>
  <div class="overflow-x-auto">
    <table class="w-full min-w-[620px] text-left text-sm">
      <thead class="bg-[#FAFAFB] text-[11px] uppercase tracking-wide text-[#858891]">
        <tr>
          <th class="px-5 py-3">User</th>
          <th class="px-4 py-3">Action</th>
          <th class="px-4 py-3">Record / module</th>
          <th class="px-4 py-3">Outcome</th>
          <th class="px-5 py-3">Date and time</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-[#F0F1F3]">
        <tr v-for="row in rows || []" :key="row.name" class="align-top">
          <td class="px-5 py-3 text-[#444850]">{{ row.actor_name || row.actor || "System" }}</td>
          <td class="px-4 py-3">
            <p class="font-medium text-[#33353A]">{{ row.action }}</p>
            <p v-if="row.details" class="mt-1 max-w-xs text-xs leading-5 text-[#737780]">{{ row.details }}</p>
          </td>
          <td class="px-4 py-3 text-[#555860]"><span v-if="row.affected_record">{{ row.affected_record }}</span><span
              v-if="row.module" class="block text-xs text-[#858891]">{{ row.module }}</span></td>
          <td class="px-4 py-3"><span class="rounded-full px-2 py-1 text-xs font-semibold"
              :class="row.outcome === 'Success' ? 'bg-[#EAF5EE] text-[#267344]' : 'bg-[#FDEBEC] text-[#A10E24]'">{{
                row.outcome }}</span></td>
          <td class="whitespace-nowrap px-5 py-3 text-xs text-[#737780]">{{ dateLabel(row.creation) }}</td>
        </tr>
        <tr v-if="loading">
          <td colspan="5" class="px-5 py-8 text-center text-sm text-[#737780]">Loading activity…</td>
        </tr>
        <tr v-else-if="!rows?.length">
          <td colspan="5" class="px-5 py-8 text-center text-sm text-[#737780]">No recorded activity yet.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
defineProps({ rows: { type: Array, default: () => [] }, loading: { type: Boolean, default: false } })
function dateLabel(value) { return value ? new Date(String(value).replace(" ", "T")).toLocaleString() : "" }
</script>
