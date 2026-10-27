<template>
  <LoadingBar />
  <AppShell v-if="route.meta.app"><router-view /></AppShell>
  <router-view v-else />
</template>

<script setup>
import { useRoute } from "vue-router"
import AppShell from "./components/AppShell.vue"
import LoadingBar from "./components/LoadingBar.vue"

const route = useRoute()
</script>