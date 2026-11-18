<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 text-[#25272B] sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1200px]">
			<header>
				<p class="text-sm text-[#737780]">{{ analysis.data?.scope || 'Programme' }} aggregate reporting</p>
				<h1 class="mt-1 text-2xl font-semibold tracking-tight">Analysis</h1>
				<p class="mt-1 text-sm text-[#737780]">Counts and distributions for client profiles, verified baselines, and completed sessions.</p>
			</header>
			<section class="export-panel mt-4" aria-label="Export analysis data">
				<div class="flex flex-wrap items-center gap-x-5 gap-y-2">
					<span class="text-sm font-semibold">Download data:</span>
					<label v-for="item in exportOptions" :key="item.key" class="inline-flex items-center gap-2 text-sm">
						<input v-model="selectedGroups" type="checkbox" :value="item.key" /> {{ item.label }}
					</label>
					<div class="ml-auto flex gap-2">
						<button type="button" class="download-button" :disabled="!selectedGroups.length || !analysis.data" @click="downloadCsv">CSV</button>
						<button type="button" class="download-button primary" :disabled="!selectedGroups.length || !analysis.data" @click="downloadExcel">Excel</button>
					</div>
				</div>
				<p class="mt-2 text-xs text-[#737780]">Exports include the selected aggregate tables shown below. Free-text clinical notes and identifying client records are excluded.</p>
			</section>
			<ErrorMessage class="mt-4" :message="analysis.error" />
			<PageLoader v-if="analysis.loading && !analysis.data" />
			<template v-if="analysis.data">
				<p class="mt-4 text-xs text-[#737780]">Client and session figures use all available records. Baseline responses use each client’s latest verified, consented baseline. Missing answers are excluded from that field’s response denominator.</p>
				<section class="panel mt-5">
					<h2>Clients <span class="count">{{ analysis.data.clients.total }} total</span></h2>
					<div class="stats"><div><b>{{ analysis.data.clients.age.mean ?? '—' }}</b><span>Mean age</span></div><div><b>{{ analysis.data.clients.age.median ?? '—' }}</b><span>Median age</span></div><div><b>{{ analysis.data.clients.age.min ?? '—' }}–{{ analysis.data.clients.age.max ?? '—' }}</b><span>Age range (n={{ analysis.data.clients.age.n }})</span></div><div><b>{{ analysis.data.clients.assigned }}</b><span>Assigned counsellor</span></div><div><b>{{ analysis.data.clients.unassigned }}</b><span>Unassigned</span></div></div>
					<DistributionTable title="Age bands" :counts="analysis.data.clients.age_bands" />
					<div class="grid">
						<DistributionTable v-for="(counts, field) in analysis.data.clients.distributions" :key="`client-${field}`" :title="clientLabels[field] || label(field)" :counts="counts" :boolean-values="['disability_status', 'refugee_status'].includes(field)" :value-labels="field === 'cohort' ? cohortLabels : field === 'year_of_study' ? yearLabels : null" />
					</div>
				</section>
				<section class="panel mt-5">
					<h2>Baseline <span class="count">{{ analysis.data.baseline.verified_clients }} latest verified responses</span></h2>
					<div class="stats"><div><b>{{ analysis.data.baseline.dependants.mean ?? '—' }}</b><span>Mean dependants</span></div><div><b>{{ analysis.data.baseline.dependants.median ?? '—' }}</b><span>Median dependants (n={{ analysis.data.baseline.dependants.n }})</span></div><div v-for="(score, field) in analysis.data.baseline.ordinal_scores" :key="field"><b>{{ score.mean }} / 5</b><span>{{ label(field) }} coded mean (n={{ score.n }})</span></div></div>
					<p class="note">Coded means map ordered answers from 1 (lowest) to 5 (highest); category distributions remain the primary result.</p>
					<div class="grid"><DistributionTable title="Latest baseline cycle status" :counts="analysis.data.baseline.latest_cycle_status" /></div>
					<div class="grid">
						<DistributionTable v-for="(counts, field) in analysis.data.baseline.distributions" :key="`baseline-${field}`" :title="baselineLabels[field] || label(field)" :counts="counts" :boolean-values="['interest_in_support', 'willingness_for_followup'].includes(field)" />
					</div>
				</section>
				<section class="panel mt-5">
					<h2>Sessions <span class="count">{{ analysis.data.sessions.completed_sessions }} completed records · {{ analysis.data.sessions.clients_served }} clients</span></h2>
					<div class="stats"><div><b>{{ analysis.data.sessions.duration_minutes.mean ?? '—' }}</b><span>Mean duration minutes</span></div><div><b>{{ analysis.data.sessions.duration_minutes.median ?? '—' }}</b><span>Median duration (n={{ analysis.data.sessions.duration_minutes.n }})</span></div></div>
					<div class="grid">
						<DistributionTable v-for="(counts, field) in analysis.data.sessions.distributions" :key="`session-${field}`" :title="sessionLabels[field] || label(field)" :counts="counts" />
					</div>
					<div class="distribution mt-3">
						<h3>Session form fields recorded</h3>
						<table class="w-full text-sm"><tbody>
							<tr v-for="(count, field) in analysis.data.sessions.form_completion" :key="field" class="border-t border-[#ECEDEF]">
								<td class="py-1.5 pr-2">{{ sessionLabels[field] || label(field) }}</td>
								<td class="py-1.5 text-right tabular-nums">{{ count }} / {{ analysis.data.sessions.completed_sessions }} ({{ analysis.data.sessions.completed_sessions ? Math.round(count / analysis.data.sessions.completed_sessions * 100) : 0 }}%)</td>
							</tr>
						</tbody></table>
						<p class="note mt-2">This reports whether a field was filled and does not display free-text clinical notes.</p>
					</div>
				</section>
			</template>
		</div>
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { defineComponent, h, onMounted, ref } from "vue"

const analysis = createResource({ url: "krcti_mhpss.api.oversight.programme_analysis" })
const selectedGroups = ref(["clients", "baseline", "sessions"])
const exportOptions = [{ key: "clients", label: "Clients" }, { key: "baseline", label: "Baseline" }, { key: "sessions", label: "Sessions" }]
const label = (value) => String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
const cohortLabels = Object.fromEntries(Array.from({ length: 9 }, (_, index) => [String(index + 1), `Cohort ${index + 1}`]))
const yearLabels = Object.fromEntries(Array.from({ length: 10 }, (_, index) => [String(index + 1), `Year ${index + 1}`]))
const clientLabels = { gender: "Sex", study_program: "Study programme (category)", study_programme: "Study Programme", case_status: "Case status", disability_status: "Disability", refugee_status: "Refugee status", referral_source: "Referral source", institution_county: "Institution county", county_location: "Client county" }
const baselineLabels = { wellbeing_self_rating: "Wellbeing self-rating", stress_frequency: "Recent stress frequency", main_concerns: "Main concerns", support_availability: "Support availability", coping_ability: "Coping ability", coping_behaviour: "Coping behaviour", interest_in_support: "Interested in support", preferred_support_type: "Preferred support type", willingness_for_followup: "Willing to follow up", conflict_exposure: "Conflict/disaster exposure" }
const sessionLabels = { session_type: "Session type", mode_of_contact: "Mode of contact", urgency_level: "Urgency", needs_follow_up: "Follow-up needed", followup_new_issues_present: "New issues reported", followup_new_presenting_issues: "New presenting issues", followup_evident_changes_present: "Evident changes", followup_mood_affect: "Mood and affect", followup_wellbeing_rating: "Follow-up wellbeing", followup_stress_frequency: "Follow-up stress frequency", followup_engagement_level: "Engagement", followup_risk_concerns: "Risk concerns", session_details: "Session details", notes: "Notes", presenting_issues: "Presenting issues", issue_subclassifications: "Issue subclassifications", interventions_applied: "Interventions applied", referrals_made: "Referrals made", risk_assessment: "Risk assessment", follow_up_plan: "Follow-up plan", progress_previous_goals: "Progress on previous goals", followup_goals_discussed: "Goals discussed", followup_challenges: "Challenges", followup_new_issues: "New issues detail", followup_evident_changes: "Evident changes detail", followup_coping_support: "Coping support", followup_support_effectiveness: "Support effectiveness", followup_additional_support: "Additional support", counsellor_observations: "Counsellor observations", next_session_focus: "Next session focus", followup_recommendations: "Recommendations", followup_takeaways: "Takeaways", followup_action: "Follow-up action" }

const DistributionTable = defineComponent({
	props: { title: String, counts: { type: Object, default: () => ({}) }, booleanValues: Boolean, valueLabels: { type: Object, default: null } },
	setup(props) {
		return () => {
			let rows = Object.entries(props.counts || {})
			if (props.valueLabels) rows = Object.entries(props.valueLabels).map(([value, name]) => [name, Number(props.counts?.[value] || 0)])
			else rows.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
			const total = rows.reduce((sum, [, count]) => sum + count, 0)
			return h("article", { class: "distribution" }, [
				h("h3", [props.title, h("span", { class: "response-count" }, `${total} responses`)]),
				rows.length ? h("table", { class: "w-full text-sm" }, [
					h("tbody", rows.map(([name, count]) => h("tr", { class: "border-t border-[#ECEDEF]", key: name }, [
						h("td", { class: "py-1.5 pr-2" }, props.booleanValues ? (name === "1" ? "Yes" : name === "0" ? "No" : name) : name),
						h("td", { class: "py-1.5 text-right tabular-nums" }, `${count} · ${total ? Math.round(count / total * 100) : 0}%`),
					])))
				]) : h("p", { class: "text-xs text-[#858891]" }, "No recorded responses")
			])
		}
	},
})

onMounted(() => analysis.fetch())

function datasetRows(group) {
	const data = analysis.data?.[group]
	if (!data) return []
	const rows = [["Metric", "Category", "Count", "Percentage", "Value", "N", "Mean", "Median", "Min", "Max"]]
	const addValue = (metric, value) => rows.push([metric, "", "", "", value ?? "", "", "", "", "", ""])
	const addNumeric = (metric, stats) => rows.push([metric, "", "", "", "", stats.n, stats.mean ?? "", stats.median ?? "", stats.min ?? "", stats.max ?? ""])
	const addDistribution = (metric, distribution) => {
		const items = Object.entries(distribution || {})
		const total = items.reduce((sum, [, count]) => sum + count, 0)
		for (const [category, count] of items) rows.push([metric, category, count, total ? `${(count / total * 100).toFixed(1)}%` : "0.0%", "", "", "", "", "", ""])
	}
	if (group === "clients") {
		addValue("Total clients", data.total)
		addNumeric("Age", data.age)
		addValue("Assigned counsellor", data.assigned)
		addValue("Unassigned", data.unassigned)
		addDistribution("Age bands", data.age_bands)
		for (const [field, distribution] of Object.entries(data.distributions || {})) addDistribution(clientLabels[field] || label(field), distribution)
	} else if (group === "baseline") {
		addValue("Latest verified consented baselines", data.verified_clients)
		addNumeric("Dependants", data.dependants)
		addDistribution("Latest baseline cycle status", data.latest_cycle_status)
		for (const [field, score] of Object.entries(data.ordinal_scores || {})) rows.push([`${label(field)} coded ordinal score (1–5)`, "", "", "", score.scale, score.n, score.mean, score.median, "", ""])
		for (const [field, distribution] of Object.entries(data.distributions || {})) addDistribution(baselineLabels[field] || label(field), distribution)
	} else {
		addValue("Completed sessions", data.completed_sessions)
		addValue("Clients served", data.clients_served)
		addNumeric("Duration minutes", data.duration_minutes)
		for (const [field, distribution] of Object.entries(data.distributions || {})) addDistribution(sessionLabels[field] || label(field), distribution)
		for (const [field, count] of Object.entries(data.form_completion || {})) rows.push(["Session form fields recorded", sessionLabels[field] || label(field), count, data.completed_sessions ? `${(count / data.completed_sessions * 100).toFixed(1)}%` : "0.0%", "", data.completed_sessions, "", "", "", ""])
	}
	return rows
}

function triggerDownload(blob, filename) {
	const url = URL.createObjectURL(blob)
	const link = document.createElement("a")
	link.href = url
	link.download = filename
	link.click()
	setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function downloadCsv() {
	const rows = []
	for (const group of selectedGroups.value) rows.push([group.toUpperCase()], ...datasetRows(group), [])
	const csv = rows.map((row) => row.map((cell) => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(",")).join("\r\n")
	triggerDownload(new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" }), `programme-analysis-${analysis.data?.scope?.toLowerCase() || "report"}.csv`)
}

function xmlEscape(value) {
	return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&apos;")
}

function columnName(number) {
	let name = ""
	while (number) { number -= 1; name = String.fromCharCode(65 + number % 26) + name; number = Math.floor(number / 26) }
	return name
}

function worksheetXml(rows) {
	const sheetRows = rows.map((row, r) => `<row r="${r + 1}">${row.map((value, c) => {
		const ref = `${columnName(c + 1)}${r + 1}`
		return typeof value === "number" ? `<c r="${ref}"><v>${value}</v></c>` : `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${xmlEscape(value)}</t></is></c>`
	}).join("")}</row>`).join("")
	return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${sheetRows}</sheetData></worksheet>`
}

function makeZip(files) {
	const encoder = new TextEncoder()
	const crcTable = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0 })
	const crc32 = (bytes) => { let c = 0xffffffff; for (const byte of bytes) c = crcTable[(c ^ byte) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0 }
	const chunks = [], central = []
	let offset = 0
	const u16 = (view, at, value) => view.setUint16(at, value, true)
	const u32 = (view, at, value) => view.setUint32(at, value, true)
	for (const [path, content] of Object.entries(files)) {
		const name = encoder.encode(path), body = encoder.encode(content), crc = crc32(body)
		const local = new Uint8Array(30 + name.length + body.length), lv = new DataView(local.buffer)
		u32(lv, 0, 0x04034b50); u16(lv, 4, 20); u16(lv, 6, 0); u16(lv, 8, 0); u16(lv, 10, 0); u16(lv, 12, 0); u32(lv, 14, crc); u32(lv, 18, body.length); u32(lv, 22, body.length); u16(lv, 26, name.length); u16(lv, 28, 0)
		local.set(name, 30); local.set(body, 30 + name.length); chunks.push(local)
		const entry = new Uint8Array(46 + name.length), ev = new DataView(entry.buffer)
		u32(ev, 0, 0x02014b50); u16(ev, 4, 20); u16(ev, 6, 20); u16(ev, 8, 0); u16(ev, 10, 0); u16(ev, 12, 0); u16(ev, 14, 0); u32(ev, 16, crc); u32(ev, 20, body.length); u32(ev, 24, body.length); u16(ev, 28, name.length); u16(ev, 30, 0); u16(ev, 32, 0); u16(ev, 34, 0); u16(ev, 36, 0); u32(ev, 38, 0); u32(ev, 42, offset)
		entry.set(name, 46); central.push(entry); offset += local.length
	}
	const centralSize = central.reduce((sum, part) => sum + part.length, 0)
	const end = new Uint8Array(22), dv = new DataView(end.buffer)
	u32(dv, 0, 0x06054b50); u16(dv, 4, 0); u16(dv, 6, 0); u16(dv, 8, central.length); u16(dv, 10, central.length); u32(dv, 12, centralSize); u32(dv, 16, offset); u16(dv, 20, 0)
	return new Blob([...chunks, ...central, end], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" })
}

function downloadExcel() {
	const names = { clients: "Clients", baseline: "Baseline", sessions: "Sessions" }
	const groups = selectedGroups.value
	const files = {
		"[Content_Types].xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>${groups.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join("")}</Types>`,
		"_rels/.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
		"xl/workbook.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${groups.map((group, i) => `<sheet name="${names[group]}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join("")}</sheets></workbook>`,
		"xl/_rels/workbook.xml.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${groups.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join("")}</Relationships>`,
	}
	groups.forEach((group, index) => { files[`xl/worksheets/sheet${index + 1}.xml`] = worksheetXml(datasetRows(group)) })
	triggerDownload(makeZip(files), `programme-analysis-${analysis.data?.scope?.toLowerCase() || "report"}.xlsx`)
}
</script>

<style scoped>
.export-panel { border: 1px solid #e4e6ea; border-radius: 10px; background: white; padding: 14px 16px; }
.export-panel input { accent-color: #c8102e; }
.download-button { border: 1px solid #d9dbe0; border-radius: 7px; background: white; padding: 7px 12px; color: #33353a; font-size: 13px; font-weight: 600; }
.download-button:hover:not(:disabled) { border-color: #c8102e; color: #a10e24; }
.download-button.primary { border-color: #c8102e; background: #c8102e; color: white; }
.download-button:disabled { cursor: not-allowed; opacity: .5; }
.panel { border: 1px solid #e4e6ea; border-radius: 12px; background: white; padding: 20px; }
.panel h2 { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; font-size: 18px; font-weight: 650; }
.count { border-radius: 999px; background: #f4f5f7; padding: 4px 9px; color: #62656d; font-size: 12px; font-weight: 600; }
.stats { display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0; }
.stats > div { min-width: 120px; border: 1px solid #ececef; border-radius: 8px; padding: 10px 12px; }
.stats b, .stats span { display: block; }
.stats b { font-size: 18px; font-variant-numeric: tabular-nums; }
.stats span { margin-top: 3px; color: #737780; font-size: 11px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-top: 14px; }
.distribution { min-width: 0; border: 1px solid #ececef; border-radius: 8px; padding: 12px; }
.distribution h3 { margin-bottom: 6px; font-size: 13px; font-weight: 650; }
.response-count { float: right; color: #858891; font-size: 10px; font-weight: 500; }
.note { color: #737780; font-size: 12px; }
</style>
