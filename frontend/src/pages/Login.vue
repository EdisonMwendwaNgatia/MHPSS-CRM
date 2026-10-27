<template>
  <div class="flex min-h-screen items-center justify-center bg-gp-bg px-4">
    <form class="w-full max-w-sm space-y-4 rounded-lg border border-gp-line bg-white p-6" @submit.prevent="submit">
      <div class="text-center">
        <h1 class="text-xl font-semibold text-gp">KRCTI MHPSS</h1>
        <p class="text-sm text-gp-muted">Case Management System</p>
      </div>
      <FormControl label="Email" type="text" v-model="email" autocomplete="username" />
      <FormControl label="Password" type="password" v-model="password" autocomplete="current-password" />
      <ErrorMessage :message="session.login.error" />
      <Button class="w-full !bg-gp hover:!bg-gp-light" variant="solid" type="submit" :loading="session.login.loading">
        Log in
      </Button>
      <p class="text-center text-xs text-gp-muted">
        For authorised KRCTI, WoC and KRCS staff only. What you do here is recorded.
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { session } from "../data/session"

const email = ref("")
const password = ref("")

function submit() {
	session.login.submit({ email: email.value.trim(), password: password.value })
}
</script>