<template>
	<main class="min-h-[calc(100vh-68px)] bg-[#F4F5F7] px-4 py-6 text-[#25272B] sm:px-6 lg:px-8 lg:py-8">
		<div class="mx-auto max-w-[1440px]">
			<!-- Header -->
			<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
				<div>
					<p class="text-sm font-medium text-[#737780]">{{ analysis.data?.scope || 'Programme' }} aggregate reporting</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#25272B] sm:text-[28px]">Analysis</h1>
					<p class="mt-1 text-sm text-[#737780]">Counts and distributions for client profiles, verified baselines and completed sessions.</p>
				</div>
				<div v-if="analysis.data" class="no-print flex flex-wrap gap-2">
					<button v-if="defaultCount" type="button" class="btn btn-secondary" @click="resetDefaults"><RotateCcw :size="16" /> Reset chart defaults <span class="count-pill">{{ defaultCount }}</span></button>
					<button type="button" class="btn btn-secondary" @click="exportOpen = true"><Download :size="16" /> Export data</button>
				</div>
			</div>

			<ErrorMessage class="mt-4" :message="analysis.error" />
			<div v-if="analysis.loading && !analysis.data" class="mt-5 rounded-xl border border-[#E4E6EA] bg-white px-5 py-12"><PageLoader /></div>

			<template v-if="analysis.data">
				<p class="mt-4 inline-flex items-start gap-2.5 rounded-lg border border-[#C9D8F5] bg-[#E0EAFD] px-3.5 py-2.5 text-[13px] leading-5 text-[#1B4DB1]">
					<Info :size="16" class="mt-0.5 shrink-0" />
					<span>Client and session figures use all available records. Baseline responses use each client’s latest verified, consented baseline. Missing answers are excluded from that field’s response denominator.</span>
				</p>

				<!-- Tabs + chart search -->
				<div class="no-print sticky top-[68px] z-20 -mx-4 mt-5 border-b border-[#E4E6EA] bg-[#F4F5F7]/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6 md:top-[72px] lg:-mx-8 lg:px-8">
					<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
						<div class="inline-flex w-full rounded-lg bg-white p-1 shadow-[0_1px_2px_rgba(20,25,35,0.04)] ring-1 ring-[#E4E6EA] sm:w-auto" role="tablist" aria-label="Analysis sections">
							<button v-for="s in sections" :key="s.key" type="button" role="tab" :aria-selected="tab === s.key" class="seg" :class="tab === s.key ? 'seg-on' : ''" @click="tab = s.key">
								<component :is="s.icon" :size="15" /> <span class="hidden sm:inline">{{ s.title }}</span><span class="sm:hidden">{{ s.short }}</span>
							</button>
						</div>
						<label v-if="tab !== 'overview'" class="flex h-10 w-full items-center gap-2.5 rounded-lg border border-[#D9DBE0] bg-white px-3 transition focus-within:border-[#C8102E] focus-within:ring-2 focus-within:ring-[#C8102E]/10 sm:w-72">
							<Search :size="16" class="shrink-0 text-[#858891]" />
							<input v-model="q" type="search" placeholder="Find a chart…" class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[#33353A] outline-none placeholder:text-[#A0A2A8] focus:ring-0" />
							<button v-if="q" type="button" class="text-xs font-medium text-[#858891] hover:text-[#33353A]" @click="q = ''">Clear</button>
						</label>
					</div>
				</div>

				<template v-for="s in sections" :key="s.key">
					<section v-show="tab === s.key" class="print-show mt-5" :aria-label="s.title">
						<div class="mb-4 flex flex-wrap items-center justify-between gap-2">
							<div>
								<h2 class="text-lg font-semibold text-[#25272B]">{{ s.title }}</h2>
								<p class="mt-0.5 text-xs text-[#858891]">{{ s.subtitle }}</p>
							</div>
							<div class="flex flex-wrap items-center gap-2">
								<span v-if="s.key !== 'overview'" class="no-print hidden items-center gap-1.5 text-xs text-[#858891] md:inline-flex"><Pin :size="12" /> Double-click a chart type to make it that card’s default</span>
								<span class="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-[#62656D] ring-1 ring-[#E4E6EA]">{{ s.badge }}</span>
							</div>
						</div>

						<!-- ============ OVERVIEW EXTRAS ============ -->
						<template v-if="s.key === 'overview'">
							<!-- Progress rings -->
							<div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
								<div v-for="r in rings" :key="r.label" class="stat-card rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
									<div class="flex items-center gap-4">
										<div class="relative h-[84px] w-[84px] shrink-0">
											<svg viewBox="0 0 42 42" class="h-full w-full -rotate-90" role="img" :aria-label="`${r.label}: ${r.pct}%`">
												<circle cx="21" cy="21" r="15.9155" fill="none" stroke="#F4F5F7" stroke-width="4.5" />
												<circle cx="21" cy="21" r="15.9155" fill="none" :stroke="r.color" stroke-width="4.5" stroke-linecap="round" :stroke-dasharray="`${r.pct} ${100 - r.pct}`" class="ring-seg" />
											</svg>
											<span class="absolute inset-0 flex items-center justify-center text-lg font-semibold tabular-nums text-[#25272B]">{{ r.pct }}<span class="text-[11px] font-medium text-[#858891]">%</span></span>
										</div>
										<div class="min-w-0">
											<p class="text-xs font-semibold text-[#555860]">{{ r.label }}</p>
											<p class="mt-1 text-xs leading-5 text-[#858891]">{{ r.sub }}</p>
										</div>
									</div>
								</div>
							</div>

							<div class="mt-4 grid gap-4 lg:grid-cols-3">
								<!-- Funnel -->
								<article class="viz-card lg:col-span-2">
									<header class="card-head">
										<div>
											<h3 class="text-sm font-semibold text-[#25272B]">Programme pipeline</h3>
											<p class="mt-0.5 text-xs text-[#858891]">From registration to delivered sessions</p>
										</div>
										<span class="chip"><Filter :size="12" /> Funnel</span>
									</header>
									<div class="space-y-2.5 p-5">
										<div v-for="(f, i) in funnel" :key="f.label">
											<div v-if="i" class="mb-2 flex items-center justify-center gap-1.5 text-[11px] font-semibold text-[#858891]"><ArrowDown :size="12" /> {{ f.conv }}% of previous step</div>
											<div class="funnel-bar mx-auto flex h-12 items-center justify-between gap-3 rounded-lg px-4 text-white" :style="{ '--w': `${f.width}%`, background: f.color }">
												<span class="truncate text-sm font-semibold">{{ f.label }}</span>
												<span class="text-lg font-semibold tabular-nums">{{ f.value }}</span>
											</div>
										</div>
									</div>
								</article>

								<!-- Insights -->
								<article class="viz-card">
									<header class="card-head">
										<div>
											<h3 class="text-sm font-semibold text-[#25272B]">Key insights</h3>
											<p class="mt-0.5 text-xs text-[#858891]">Generated from the figures</p>
										</div>
										<span class="chip"><Lightbulb :size="12" /> Highlights</span>
									</header>
									<ul class="divide-y divide-[#F0F1F3]">
										<li v-for="(i, n) in insights" :key="n" class="flex items-start gap-3 px-5 py-3.5">
											<span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full" :class="i.tone"><component :is="i.icon" :size="14" /></span>
											<p class="text-[13px] leading-5 text-[#44474E]">{{ i.text }}</p>
										</li>
									</ul>
								</article>
							</div>

							<!-- At a glance: stacked bars -->
							<article v-if="glance.length" class="viz-card mt-4">
								<header class="card-head">
									<div>
										<h3 class="text-sm font-semibold text-[#25272B]">At a glance</h3>
										<p class="mt-0.5 text-xs text-[#858891]">How the main splits are shared</p>
									</div>
									<span class="chip"><Layers :size="12" /> 100% stacked</span>
								</header>
								<div class="grid gap-x-10 gap-y-6 p-5 md:grid-cols-2">
									<div v-for="g in glance" :key="g.key">
										<div class="flex items-baseline justify-between gap-3">
											<span class="text-sm font-semibold text-[#33353A]">{{ g.title }}</span>
											<span class="text-xs text-[#858891]">{{ g.total }} responses</span>
										</div>
										<div class="mt-2 flex h-4 gap-0.5 overflow-hidden rounded-full bg-[#F4F5F7]">
											<span v-for="seg in g.grouped" :key="seg.name" class="stack-seg h-full" :style="{ width: `${seg.share}%`, background: seg.color }" :title="`${seg.name}: ${seg.count} (${seg.pct}%)`"></span>
										</div>
										<ul class="mt-2.5 flex flex-wrap gap-x-4 gap-y-1.5">
											<li v-for="seg in g.grouped" :key="seg.name" class="flex items-center gap-1.5 text-xs text-[#555860]"><span class="h-2 w-2 rounded-full" :style="{ background: seg.color }"></span>{{ seg.name }} <b class="font-semibold tabular-nums text-[#25272B]">{{ seg.pct }}%</b></li>
										</ul>
									</div>
								</div>
							</article>
						</template>

						<!-- KPI tiles -->
						<div v-if="s.stats?.length" class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6" :class="s.key === 'overview' ? 'mt-4' : ''">
							<div v-for="k in s.stats" :key="k.label" class="stat-card rounded-xl border border-[#E4E6EA] bg-white p-4 shadow-[0_1px_2px_rgba(20,25,35,0.03)]">
								<span class="flex h-8 w-8 items-center justify-center rounded-full" :class="k.tone"><component :is="k.icon" :size="15" /></span>
								<span class="mt-3 block text-2xl font-semibold leading-none tabular-nums text-[#25272B]">{{ k.value }}</span>
								<span class="mt-1.5 block text-xs text-[#858891]">{{ k.label }}</span>
							</div>
						</div>

						<!-- Charts -->
						<div v-if="visibleCards(s).length" class="mt-4 grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
							<article v-for="c in visibleCards(s)" :key="c.key" class="viz-card min-w-0" :class="c.wide ? 'md:col-span-2 xl:col-span-3' : ''">
								<header class="card-head">
									<div class="min-w-0">
										<h3 class="truncate text-sm font-semibold text-[#25272B]">{{ c.title }}</h3>
										<p class="mt-0.5 truncate text-xs text-[#858891]">{{ c.subtitle || (c.total !== undefined ? `${c.total} responses` : '') }}</p>
									</div>
									<!-- View switcher: click to switch, double-click to pin as default -->
									<div v-if="(c.kind === 'dist' && !c.empty) || c.kind === 'completion'" class="no-print inline-flex shrink-0 select-none rounded-lg bg-[#F4F5F7] p-0.5" role="group" :aria-label="`Chart type for ${c.title}`">
										<button
											v-for="o in viewsFor(c)" :key="o.v" type="button" class="view-btn"
											:class="viewOf(c) === o.v ? 'view-btn-on' : ''"
											:title="isDefault(c, o.v) ? `${o.label} (default). Double-click to clear` : `${o.label}. Double-click to set as default`"
											:aria-label="`${o.label}${isDefault(c, o.v) ? ' (default)' : ''}`"
											:aria-pressed="viewOf(c) === o.v"
											@click="setView(c, o.v)" @dblclick.prevent="toggleDefault(c, o)"
										>
											<component :is="o.icon" :size="14" />
											<span v-if="isDefault(c, o.v)" class="pin-dot" aria-hidden="true"></span>
										</button>
									</div>
									<span v-else class="chip">{{ c.chip }}</span>
								</header>

								<div class="p-5">
									<p v-if="c.empty" class="py-8 text-center text-xs text-[#858891]">No recorded responses</p>

									<!-- ===== Distribution views ===== -->
									<template v-else-if="c.kind === 'dist'">
										<!-- Bars -->
										<div v-if="viewOf(c) === 'bars'" :key="`${c.key}-bars`" class="view-swap">
											<ul class="space-y-3.5">
												<li v-for="r in shownRows(c)" :key="r.name" class="bar-row">
													<div class="flex items-baseline justify-between gap-3 text-sm">
														<span class="flex min-w-0 items-center gap-2"><span class="h-2 w-2 shrink-0 rounded-full" :style="{ background: r.color }"></span><span class="truncate font-medium text-[#33353A]" :title="r.name">{{ r.name }}</span></span>
														<span class="shrink-0 tabular-nums"><b class="font-semibold text-[#25272B]">{{ r.count }}</b><span class="ml-1.5 text-xs text-[#858891]">{{ r.pct }}%</span></span>
													</div>
													<div class="mt-1.5 h-2 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="bar-fill h-full rounded-full" :style="{ '--w': `${r.rel}%`, background: r.color }"></div></div>
												</li>
											</ul>
											<button v-if="c.rows.length > 8" type="button" class="no-print mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-[#A10E24] hover:underline" @click="expanded[c.key] = !expanded[c.key]">
												<ChevronDown :size="14" :class="expanded[c.key] ? 'rotate-180' : ''" /> {{ expanded[c.key] ? 'Show fewer' : `Show all ${c.rows.length}` }}
											</button>
										</div>

										<!-- Columns -->
										<div v-else-if="viewOf(c) === 'columns'" :key="`${c.key}-columns`" class="view-swap">
											<div class="col-grid flex h-48 items-end gap-2 border-b border-[#ECEDEF] px-1">
												<div v-for="r in c.rows.slice(0, 14)" :key="r.name" class="group flex h-full min-w-0 flex-1 flex-col items-center justify-end" :title="`${r.name}: ${r.count} (${r.pct}%)`">
													<span class="mb-1 text-[11px] font-semibold tabular-nums text-[#555860]">{{ r.count }}</span>
													<span class="col-bar w-full max-w-[44px] rounded-t-md bg-[#C8102E] transition group-hover:bg-[#A10E24]" :style="{ '--h': `${Math.max(r.rel, 3)}%` }"></span>
												</div>
											</div>
											<div class="mt-2 flex gap-2 px-1">
												<span v-for="r in c.rows.slice(0, 14)" :key="r.name" class="min-w-0 flex-1 truncate text-center text-[11px] text-[#858891]" :title="r.name">{{ r.name }}</span>
											</div>
											<p v-if="c.rows.length > 14" class="mt-2 text-center text-[11px] text-[#A0A2A8]">Showing the first 14 of {{ c.rows.length }} categories</p>
										</div>

										<!-- Donut -->
										<div v-else-if="viewOf(c) === 'donut'" :key="`${c.key}-donut`" class="view-swap flex flex-col items-center gap-5 sm:flex-row">
											<div class="relative h-40 w-40 shrink-0">
												<svg viewBox="0 0 42 42" class="h-full w-full -rotate-90" role="img" :aria-label="c.title">
													<circle cx="21" cy="21" r="15.9155" fill="none" stroke="#F4F5F7" stroke-width="5" />
													<circle v-for="seg in segments(c)" :key="seg.name" cx="21" cy="21" r="15.9155" fill="none" :stroke="seg.color" stroke-width="5" :stroke-dasharray="`${seg.len} ${100 - seg.len}`" :stroke-dashoffset="-seg.start" class="donut-seg" :style="{ opacity: dim(c, seg.name) }"><title>{{ seg.name }}: {{ seg.count }} ({{ seg.pct }}%)</title></circle>
												</svg>
												<span class="absolute inset-0 flex flex-col items-center justify-center">
													<span class="text-2xl font-semibold tabular-nums text-[#25272B]">{{ hot[c.key] ? hotRow(c)?.pct + '%' : c.total }}</span>
													<span class="max-w-[90px] truncate text-[11px] text-[#858891]">{{ hot[c.key] || 'total' }}</span>
												</span>
											</div>
											<ul class="min-w-0 flex-1 space-y-2 self-stretch">
												<li v-for="r in c.grouped" :key="r.name" class="legend-row flex items-center justify-between gap-3 rounded-md px-2 py-1 text-sm" @mouseenter="hot[c.key] = r.name" @mouseleave="hot[c.key] = ''">
													<span class="flex min-w-0 items-center gap-2"><span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ background: r.color }"></span><span class="truncate text-[#33353A]">{{ r.name }}</span></span>
													<span class="shrink-0 tabular-nums"><b class="font-semibold text-[#25272B]">{{ r.count }}</b><span class="ml-1.5 text-xs text-[#858891]">{{ r.pct }}%</span></span>
												</li>
											</ul>
										</div>
									</template>

									<!-- ===== Central tendency plot ===== -->
									<div v-else-if="c.kind === 'plot'" class="space-y-7">
										<div v-for="p in c.items" :key="p.name">
											<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
												<span class="text-sm font-semibold text-[#33353A]">{{ p.name }} <span class="text-xs font-normal text-[#858891]">n = {{ p.n }}</span></span>
												<span class="flex items-center gap-4 text-xs text-[#555860]">
													<span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-[#C8102E]"></span>Mean <b class="tabular-nums text-[#25272B]">{{ p.mean }}</b></span>
													<span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rotate-45 bg-[#1B4DB1]"></span>Median <b class="tabular-nums text-[#25272B]">{{ p.median }}</b></span>
													<span v-if="p.min !== null" class="text-[#858891]">Range {{ p.min }}–{{ p.max }}</span>
												</span>
											</div>
											<div class="relative mt-4 h-6">
												<div class="absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-[#F4F5F7]"></div>
												<div v-if="p.min !== null" class="plot-range absolute top-1/2 h-3 -translate-y-1/2 rounded-full bg-[#F7C9D1]" :style="{ left: `${p.minPos}%`, width: `${Math.max(p.maxPos - p.minPos, 1)}%` }"></div>
												<span class="plot-dot absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rotate-45 border-2 border-white bg-[#1B4DB1] shadow" :style="{ left: `${p.medianPos}%` }" :title="`Median ${p.median}`"></span>
												<span class="plot-dot absolute top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-[#C8102E] shadow" :style="{ left: `${p.meanPos}%` }" :title="`Mean ${p.mean}`"></span>
											</div>
											<div class="relative mt-1 h-4 text-[10px] tabular-nums text-[#A0A2A8]">
												<span v-for="t in p.ticks" :key="t.pos" class="absolute -translate-x-1/2" :style="{ left: `${t.pos}%` }">{{ t.label }}</span>
											</div>
										</div>
									</div>

									<!-- ===== Radar + gauges ===== -->
									<div v-else-if="c.kind === 'radar'" class="grid items-center gap-6 lg:grid-cols-[340px_1fr]">
										<svg v-if="c.radar" viewBox="0 0 320 230" class="mx-auto w-full max-w-[340px]" role="img" aria-label="Radar chart of coded means">
											<polygon v-for="(ring, i) in c.radar.rings" :key="i" :points="ring" fill="none" stroke="#E4E6EA" stroke-width="1" />
											<line v-for="a in c.radar.axes" :key="a.text" :x1="c.radar.cx" :y1="c.radar.cy" :x2="a.x2" :y2="a.y2" stroke="#ECEDEF" stroke-width="1" />
											<polygon :points="c.radar.poly" fill="rgba(200,16,46,0.16)" stroke="#C8102E" stroke-width="2" stroke-linejoin="round" class="radar-poly" />
											<circle v-for="a in c.radar.axes" :key="`d-${a.text}`" :cx="a.dx" :cy="a.dy" r="3.5" fill="#C8102E" stroke="#fff" stroke-width="1.5" />
											<text v-for="a in c.radar.axes" :key="`t-${a.text}`" :x="a.lx" :y="a.ly" :text-anchor="a.anchor" dominant-baseline="middle" font-size="9" fill="#737780">{{ a.short }}</text>
										</svg>
										<div class="grid gap-5 sm:grid-cols-2" :class="c.radar ? '' : 'lg:col-span-2 lg:grid-cols-3'">
											<div v-for="g in c.rows" :key="g.name">
												<div class="flex items-baseline justify-between gap-3">
													<span class="text-sm font-medium text-[#33353A]">{{ g.name }}</span>
													<span class="text-sm tabular-nums"><b class="text-lg font-semibold text-[#25272B]">{{ g.mean }}</b><span class="text-xs text-[#858891]"> / 5</span></span>
												</div>
												<div class="relative mt-2 h-2.5 overflow-hidden rounded-full bg-[#F4F5F7]">
													<div class="bar-fill h-full rounded-full bg-gradient-to-r from-[#E58A99] to-[#C8102E]" :style="{ '--w': `${g.rel}%` }"></div>
												</div>
												<div class="mt-1 flex justify-between px-0.5 text-[10px] text-[#A0A2A8]"><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span></div>
												<p class="mt-0.5 text-xs text-[#858891]">n = {{ g.n }}</p>
											</div>
										</div>
									</div>

									<!-- ===== Form completion ===== -->
									<template v-else-if="c.kind === 'completion'">
										<ul v-if="viewOf(c) === 'bars'" :key="`${c.key}-bars`" class="view-swap grid gap-x-8 gap-y-4 md:grid-cols-2">
											<li v-for="r in c.rows" :key="r.name">
												<div class="flex items-baseline justify-between gap-3 text-sm">
													<span class="truncate font-medium text-[#33353A]" :title="r.name">{{ r.name }}</span>
													<span class="shrink-0 tabular-nums text-xs text-[#858891]"><b class="text-sm font-semibold text-[#25272B]">{{ r.pct }}%</b> · {{ r.count }} / {{ r.of }}</span>
												</div>
												<div class="mt-1.5 h-2 overflow-hidden rounded-full bg-[#F4F5F7]"><div class="bar-fill h-full rounded-full" :style="{ '--w': `${r.pct}%`, background: heat(r.pct).solid }"></div></div>
											</li>
										</ul>
										<div v-else :key="`${c.key}-heat`" class="view-swap grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
											<div v-for="r in c.rows" :key="r.name" class="heat-tile rounded-lg p-3" :style="{ background: heat(r.pct).soft }" :title="`${r.name}: ${r.count} / ${r.of}`">
												<p class="truncate text-xs font-medium text-[#33353A]">{{ r.name }}</p>
												<p class="mt-1 text-lg font-semibold tabular-nums" :style="{ color: heat(r.pct).ink }">{{ r.pct }}%</p>
											</div>
										</div>
										<div class="mt-5 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-[11px] text-[#858891]">
											<span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-[#146C3A]"></span>80% or more</span>
											<span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-[#D99A2B]"></span>50–79%</span>
											<span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-[#C8102E]"></span>Below 50%</span>
										</div>
									</template>
								</div>

								<p v-if="c.kind === 'dist' && c.top" class="flex items-center gap-2 border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3 text-xs text-[#737780]">
									<TrendingUp :size="13" class="shrink-0 text-[#A10E24]" /> Most common: <b class="truncate font-semibold text-[#33353A]">{{ c.top.name }}</b> · {{ c.top.pct }}%
								</p>
								<p v-else-if="c.footnote" class="border-t border-[#ECEDEF] bg-[#FCFCFD] px-5 py-3 text-xs text-[#737780]">{{ c.footnote }}</p>
							</article>
						</div>
						<div v-else-if="s.key !== 'overview'" class="viz-card px-5 py-14 text-center">
							<span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F4F5F7] text-[#858891]"><Search :size="22" /></span>
							<p class="mt-3 text-sm font-semibold text-[#33353A]">No charts match “{{ q }}”</p>
							<button type="button" class="mt-2 text-xs font-semibold text-[#A10E24] hover:underline" @click="q = ''">Clear search</button>
						</div>
					</section>
				</template>
			</template>
		</div>

		<!-- Default-set confirmation -->
		<Transition name="toast">
			<div v-if="toast" class="no-print fixed bottom-6 left-1/2 z-50 flex max-w-[calc(100vw-2rem)] -translate-x-1/2 items-center gap-2.5 rounded-xl bg-[#25272B] px-4 py-3 text-sm text-white shadow-[0_12px_32px_-8px_rgba(20,25,35,0.45)]" role="status" aria-live="polite">
				<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full" :class="toast.cleared ? 'bg-white/15' : 'bg-[#C8102E]'"><component :is="toast.cleared ? RotateCcw : Pin" :size="12" /></span>
				<span class="min-w-0">{{ toast.text }}</span>
			</div>
		</Transition>
		<ProgrammeDataExport v-if="exportOpen" @close="exportOpen = false" />
	</main>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue"
import { Activity, AlignLeft, ArrowDown, BarChart3, CalendarRange, ChevronDown, ClipboardCheck, Download, Filter, HeartPulse, Info, Layers, LayoutDashboard, LayoutGrid, Lightbulb, PieChart, Pin, RotateCcw, Search, ShieldCheck, Timer, TrendingUp, UserCheck, UserX, Users, UsersRound } from "lucide-vue-next"
import ProgrammeDataExport from "../components/ProgrammeDataExport.vue"

const analysis = createResource({ url: "krcti_mhpss.api.oversight.programme_analysis" })
const tab = ref("overview")
const q = ref("")
const exportOpen = ref(false)

const label = (value) => String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
const clientLabels = { gender: "Sex", study_program: "Study programme (category)", study_programme: "Study Programme", case_status: "Case status", disability_status: "Disability", refugee_status: "Refugee status", referral_source: "Referral source", institution_county: "Institution county", county_location: "Client county" }
const baselineLabels = { wellbeing_self_rating: "Wellbeing self-rating", stress_frequency: "Recent stress frequency", main_concerns: "Main concerns", support_availability: "Support availability", coping_ability: "Coping ability", coping_behaviour: "Coping behaviour", interest_in_support: "Interested in support", preferred_support_type: "Preferred support type", willingness_for_followup: "Willing to follow up", conflict_exposure: "Conflict/disaster exposure" }
const sessionLabels = { session_type: "Session type", mode_of_contact: "Mode of contact", urgency_level: "Urgency", needs_follow_up: "Follow-up needed", followup_new_issues_present: "New issues reported", followup_new_presenting_issues: "New presenting issues", followup_evident_changes_present: "Evident changes", followup_mood_affect: "Mood and affect", followup_wellbeing_rating: "Follow-up wellbeing", followup_stress_frequency: "Follow-up stress frequency", followup_engagement_level: "Engagement", followup_risk_concerns: "Risk concerns", session_details: "Session details", notes: "Notes", presenting_issues: "Presenting issues", issue_subclassifications: "Issue subclassifications", interventions_applied: "Interventions applied", referrals_made: "Referrals made", risk_assessment: "Risk assessment", follow_up_plan: "Follow-up plan", progress_previous_goals: "Progress on previous goals", followup_goals_discussed: "Goals discussed", followup_challenges: "Challenges", followup_new_issues: "New issues detail", followup_evident_changes: "Evident changes detail", followup_coping_support: "Coping support", followup_support_effectiveness: "Support effectiveness", followup_additional_support: "Additional support", counsellor_observations: "Counsellor observations", next_session_focus: "Next session focus", followup_recommendations: "Recommendations", followup_takeaways: "Takeaways", followup_action: "Follow-up action" }

// ---- Chart switcher ----
// Click switches the view for this visit. Double-click pins it as that card's default (saved in this browser).
const distViews = [
	{ v: "bars", label: "Bars", icon: AlignLeft },
	{ v: "columns", label: "Columns", icon: BarChart3 },
	{ v: "donut", label: "Donut", icon: PieChart },
]
const completionViews = [
	{ v: "bars", label: "Bars", icon: AlignLeft },
	{ v: "heat", label: "Heatmap", icon: LayoutGrid },
]
const viewsFor = (c) => (c.kind === "completion" ? completionViews : distViews)

const STORE_KEY = "krcti-analysis-chart-defaults"
function loadDefaults() {
	try {
		const parsed = JSON.parse(localStorage.getItem(STORE_KEY) || "{}")
		return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {}
	} catch {
		return {}
	}
}
function saveDefaults() {
	try { localStorage.setItem(STORE_KEY, JSON.stringify(defaults)) } catch { /* storage unavailable */ }
}

const views = reactive({})
const defaults = reactive(loadDefaults())
const expanded = reactive({})
const hot = reactive({})
const defaultCount = computed(() => Object.keys(defaults).length)

// A saved default only applies while it is still a valid view for that card; otherwise fall back to the automatic choice.
const viewOf = (c) => {
	const chosen = views[c.key] || defaults[c.key]
	return chosen && viewsFor(c).some((o) => o.v === chosen) ? chosen : c.auto
}
const isDefault = (c, v) => defaults[c.key] === v
const setView = (c, v) => { views[c.key] = v }

const toast = ref(null)
let toastTimer = null
function notify(text, cleared = false) {
	toast.value = { text, cleared }
	clearTimeout(toastTimer)
	toastTimer = setTimeout(() => { toast.value = null }, 2600)
}
function toggleDefault(c, option) {
	views[c.key] = option.v
	if (defaults[c.key] === option.v) {
		delete defaults[c.key]
		notify(`Default cleared for “${c.title}”`, true)
	} else {
		defaults[c.key] = option.v
		notify(`${option.label} is now the default for “${c.title}”`)
	}
	saveDefaults()
}
function resetDefaults() {
	for (const key of Object.keys(defaults)) delete defaults[key]
	for (const key of Object.keys(views)) delete views[key]
	saveDefaults()
	notify("All chart defaults reset", true)
}
onBeforeUnmount(() => clearTimeout(toastTimer))

const shownRows = (c) => (expanded[c.key] ? c.rows : c.rows.slice(0, 8))
const hotRow = (c) => c.grouped.find((r) => r.name === hot[c.key])
const dim = (c, name) => (hot[c.key] && hot[c.key] !== name ? 0.25 : 1)

// ---- Helpers ----
const PALETTE = ["#C8102E", "#1B4DB1", "#146C3A", "#D99A2B", "#0E8A8A", "#7A3FB5", "#62656D"]
const OTHER = "#B9BBC1"
const YES_NO_DISTRIBUTIONS = new Set([
	"disability_status", "refugee_status", "interest_in_support", "willingness_for_followup",
	"needs_follow_up", "followup_new_issues_present", "followup_new_presenting_issues", "followup_evident_changes_present",
])
const pretty = (name, field) => YES_NO_DISTRIBUTIONS.has(field) && name === "1" ? "Yes" : YES_NO_DISTRIBUTIONS.has(field) && name === "0" ? "No" : name
const pct = (n, d) => (d ? Math.min(100, Math.round((n / d) * 100)) : 0)
const val = (v) => (v === null || v === undefined ? "—" : v)
const has = (v) => v !== null && v !== undefined

function distribution(key, title, counts, extra = {}) {
	const entries = Object.entries(counts || {}).filter(([, n]) => n > 0)
	const total = entries.reduce((sum, [, n]) => sum + n, 0)
	if (!total) return { kind: "dist", key, title, empty: true, ...extra }
	const numeric = entries.length > 2 && entries.every(([name]) => name.trim() !== "" && !Number.isNaN(Number(name)))
	if (numeric) entries.sort((a, b) => Number(a[0]) - Number(b[0]))
	else if (!extra.ordered) entries.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
	const max = Math.max(...entries.map(([, n]) => n))
	const rows = entries.map(([name, count], i) => ({ name: pretty(name, key.replace(/^(client|baseline|session)-/, "")), count, share: (count / total) * 100, pct: Math.round((count / total) * 100), rel: Math.round((count / max) * 100), color: i < 7 ? PALETTE[i] : OTHER }))

	const byCount = [...rows].sort((a, b) => b.count - a.count)
	const grouped = byCount.slice(0, 6).map((r, i) => ({ ...r, color: PALETTE[i] }))
	if (byCount.length > 6) {
		const rest = byCount.slice(6)
		const count = rest.reduce((s, r) => s + r.count, 0)
		grouped.push({ name: `Other (${rest.length})`, count, share: (count / total) * 100, pct: Math.round((count / total) * 100), rel: 0, color: OTHER })
	}

	const auto = extra.view || (rows.length > 1 && rows.length <= 5 ? "donut" : "bars")
	return { kind: "dist", key, title, rows, grouped, total, top: byCount[0], auto, ...extra }
}
function segments(card) {
	let start = 0
	return card.grouped.map((r) => {
		const len = Math.max(r.share - 0.6, 0.3)
		const seg = { ...r, start, len }
		start += r.share
		return seg
	})
}

// Mean / median track
function niceCeil(v) {
	const step = v <= 10 ? 1 : v <= 50 ? 5 : 10
	return Math.max(step, Math.ceil(v / step) * step)
}
function plot(name, o) {
	if (!o || !has(o.mean)) return null
	const top = Math.max(o.max ?? 0, o.mean, o.median ?? 0)
	const scale = niceCeil(top * 1.1)
	const pos = (v) => Math.min(100, Math.max(0, (v / scale) * 100))
	return {
		name, n: o.n ?? 0, mean: o.mean, median: val(o.median), min: has(o.min) ? o.min : null, max: has(o.max) ? o.max : null,
		meanPos: pos(o.mean), medianPos: pos(o.median ?? o.mean), minPos: pos(o.min ?? 0), maxPos: pos(o.max ?? 0),
		ticks: [0, 0.25, 0.5, 0.75, 1].map((f) => ({ pos: f * 100, label: Math.round(scale * f * 10) / 10 })),
	}
}

// Radar
function radar(rows) {
	const n = rows.length
	if (n < 3) return null
	const cx = 160, cy = 112, R = 78
	const angle = (i) => ((-90 + (i * 360) / n) * Math.PI) / 180
	const pt = (i, r) => [cx + r * Math.cos(angle(i)), cy + r * Math.sin(angle(i))]
	const fmt = (p) => p.map((v) => v.toFixed(1)).join(",")
	const rings = [1, 2, 3, 4, 5].map((l) => rows.map((_, i) => fmt(pt(i, (R * l) / 5))).join(" "))
	const axes = rows.map((r, i) => {
		const [x2, y2] = pt(i, R)
		const [lx, ly] = pt(i, R + 14)
		const [dx, dy] = pt(i, R * Math.min(1, Math.max(0, r.mean / 5)))
		return { text: r.name, short: r.name.length > 18 ? `${r.name.slice(0, 17)}…` : r.name, x2, y2, lx, ly, dx, dy, anchor: lx < cx - 4 ? "end" : lx > cx + 4 ? "start" : "middle" }
	})
	const poly = rows.map((r, i) => fmt(pt(i, R * Math.min(1, Math.max(0, r.mean / 5))))).join(" ")
	return { rings, axes, poly, cx, cy }
}

const heat = (p) => (p >= 80
	? { solid: "#146C3A", soft: "rgba(20,108,58,0.14)", ink: "#146C3A" }
	: p >= 50
		? { solid: "#D99A2B", soft: "rgba(217,154,43,0.18)", ink: "#8A4B00" }
		: { solid: "#C8102E", soft: "rgba(200,16,46,0.12)", ink: "#A10E24" })

// ---- Data model ----
const model = computed(() => {
	const d = analysis.data
	if (!d) return null
	const c = d.clients || {}
	const b = d.baseline || {}
	const s = d.sessions || {}
	const age = c.age || {}
	const dep = b.dependants || {}
	const dur = s.duration_minutes || {}
	const done = s.completed_sessions || 0

	const map = {}
	const reg = (card) => { map[card.key] = card; return card }

	// Clients
	const clientCards = [
		...(plot("Client age", age) ? [{ kind: "plot", key: "age-plot", title: "Client age", subtitle: "Mean, median and range in years", chip: "Mean vs median", items: [plot("Age (years)", age)], wide: false }] : []),
		reg(distribution("age-bands", "Age bands", c.age_bands, { ordered: true, subtitle: "Clients by age group" })),
		reg(distribution("assignment", "Counsellor assignment", { Assigned: c.assigned || 0, Unassigned: c.unassigned || 0 }, { subtitle: "Assigned vs unassigned" })),
		...Object.entries(c.distributions || {}).map(([f, counts]) => reg(distribution(`client-${f}`, clientLabels[f] || label(f), counts))),
	]

	// Baseline
	const gauges = Object.entries(b.ordinal_scores || {}).map(([f, sc]) => ({ name: label(f), mean: sc.mean, n: sc.n, rel: Math.min(100, Math.max(0, Math.round(((sc.mean - 1) / 4) * 100))) }))
	const baselineCards = [
		...(gauges.length ? [{ kind: "radar", key: "ordinals", title: "Coded means", subtitle: "Ordered answers mapped from 1 (lowest) to 5 (highest)", chip: "Radar + gauges", rows: gauges, radar: radar(gauges), wide: true, footnote: "Coded means are a summary only; category distributions remain the primary result." }] : []),
		...(plot("Dependants", dep) ? [{ kind: "plot", key: "dep-plot", title: "Dependants", subtitle: "Mean and median per client", chip: "Mean vs median", items: [plot("Dependants per client", dep)] }] : []),
		reg(distribution("cycle", "Latest baseline cycle status", b.latest_cycle_status, { subtitle: "Status of each client’s latest cycle" })),
		...Object.entries(b.distributions || {}).map(([f, counts]) => reg(distribution(`baseline-${f}`, baselineLabels[f] || label(f), counts))),
	]

	// Sessions
	const completion = Object.entries(s.form_completion || {})
		.map(([f, count]) => ({ name: sessionLabels[f] || label(f), count, of: done, pct: pct(count, done) }))
		.sort((x, y) => y.pct - x.pct || x.name.localeCompare(y.name))
	const avgCompletion = completion.length ? Math.round(completion.reduce((t, r) => t + r.pct, 0) / completion.length) : 0
	const sessionCards = [
		...(plot("Session duration", dur) ? [{ kind: "plot", key: "dur-plot", title: "Session duration", subtitle: "Mean and median in minutes", chip: "Mean vs median", items: [plot("Duration (minutes)", dur)] }] : []),
		...Object.entries(s.distributions || {}).map(([f, counts]) => reg(distribution(`session-${f}`, sessionLabels[f] || label(f), counts))),
		{ kind: "completion", key: "completion", title: "Session form fields recorded", subtitle: "Share of completed sessions where each field was filled", rows: completion, auto: "bars", empty: !completion.length, wide: true, footnote: "This reports whether a field was filled and does not display free-text clinical notes." },
	]

	// Overview
	const rings = [
		{ label: "Counsellor assignment", pct: pct(c.assigned, c.total), color: "#C8102E", sub: `${c.assigned ?? 0} of ${c.total ?? 0} clients have a counsellor` },
		{ label: "Baseline coverage", pct: pct(b.verified_clients, c.total), color: "#1B4DB1", sub: `${b.verified_clients ?? 0} verified, consented baselines` },
		{ label: "Service reach", pct: pct(s.clients_served, c.total), color: "#146C3A", sub: `${s.clients_served ?? 0} clients received a session` },
		{ label: "Form completion", pct: avgCompletion, color: "#D99A2B", sub: "Average share of session fields filled" },
	]
	const steps = [
		{ label: "Registered clients", value: c.total || 0, color: "#C8102E" },
		{ label: "Counsellor assigned", value: c.assigned || 0, color: "#D94B62" },
		{ label: "Verified baseline", value: b.verified_clients || 0, color: "#E0707F" },
		{ label: "Received sessions", value: s.clients_served || 0, color: "#E58A99" },
	]
	const funnel = steps.map((st, i) => ({ ...st, width: Math.min(100, Math.max(st.value ? (st.value / (steps[0].value || 1)) * 100 : 0, 24)), conv: i ? pct(st.value, steps[i - 1].value) : 100 }))

	const lead = (key, text) => {
		const card = map[key]
		return card?.top ? { tone: "bg-[#E0EAFD] text-[#1B4DB1]", icon: TrendingUp, text: `${text}: ${card.top.name} leads at ${card.top.pct}%.` } : null
	}
	const lowest = [...completion].sort((x, y) => x.pct - y.pct)[0]
	const insights = [
		{ tone: "bg-[#FCE8EB] text-[#A10E24]", icon: UserCheck, text: `${pct(c.assigned, c.total)}% of clients have an assigned counsellor${c.unassigned ? `, with ${c.unassigned} still waiting.` : "."}` },
		has(age.median) ? { tone: "bg-[#DCF3E4] text-[#146C3A]", icon: CalendarRange, text: `Median client age is ${age.median}${has(age.min) ? `, ranging from ${age.min} to ${age.max}` : ""}.` } : null,
		lead("client-gender", "Sex"),
		lead("client-referral_source", "Referral source"),
		lead("baseline-stress_frequency", "Recent stress"),
		lead("session-mode_of_contact", "Mode of contact"),
		has(dur.mean) ? { tone: "bg-[#FDECC8] text-[#8A4B00]", icon: Timer, text: `Sessions average ${dur.mean} minutes (median ${val(dur.median)}).` } : null,
		lowest && completion.length > 1 ? { tone: "bg-[#FBE0E4] text-[#A10E24]", icon: Activity, text: `“${lowest.name}” is the least completed session field at ${lowest.pct}%.` } : null,
	].filter(Boolean).slice(0, 7)

	const glance = ["client-case_status", "client-gender", "baseline-stress_frequency", "session-mode_of_contact", "session-urgency_level", "client-disability_status"]
		.map((k) => map[k]).filter((x) => x && !x.empty).slice(0, 4)

	const overviewCards = [
		...(plot("Client age", age) ? [{ kind: "plot", key: "ov-plot", title: "Averages at a glance", subtitle: "Mean (circle) and median (diamond) across the programme", chip: "Mean vs median", wide: true, items: [plot("Client age (years)", age), plot("Dependants per client", dep), plot("Session duration (minutes)", dur)].filter(Boolean) }] : []),
	]

	const sections = [
		{ key: "overview", short: "Overview", title: "Overview", icon: LayoutDashboard, subtitle: "The whole programme on one page", badge: `${c.total ?? 0} clients · ${done} sessions`, stats: [], cards: overviewCards },
		{
			key: "clients", short: "Clients", title: "Clients", icon: Users, subtitle: "Profile, demographics and assignment", badge: `${c.total ?? 0} total`,
			stats: [
				{ label: "Mean age", value: val(age.mean), icon: CalendarRange, tone: "bg-[#FCE8EB] text-[#A10E24]" },
				{ label: "Median age", value: val(age.median), icon: CalendarRange, tone: "bg-[#FCE8EB] text-[#A10E24]" },
				{ label: `Age range (n=${age.n ?? 0})`, value: `${val(age.min)}–${val(age.max)}`, icon: Activity, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
				{ label: "Assigned counsellor", value: val(c.assigned), icon: UserCheck, tone: "bg-[#DCF3E4] text-[#146C3A]" },
				{ label: "Unassigned", value: val(c.unassigned), icon: UserX, tone: "bg-[#FDECC8] text-[#8A4B00]" },
				{ label: "Total clients", value: val(c.total), icon: Users, tone: "bg-[#F4F5F7] text-[#62656D]" },
			],
			cards: clientCards,
		},
		{
			key: "baseline", short: "Baseline", title: "Baseline", icon: HeartPulse, subtitle: "Latest verified, consented baseline per client", badge: `${b.verified_clients ?? 0} latest verified responses`,
			stats: [
				{ label: "Verified clients", value: val(b.verified_clients), icon: ShieldCheck, tone: "bg-[#DCF3E4] text-[#146C3A]" },
				{ label: "Mean dependants", value: val(dep.mean), icon: UsersRound, tone: "bg-[#FCE8EB] text-[#A10E24]" },
				{ label: `Median dependants (n=${dep.n ?? 0})`, value: val(dep.median), icon: UsersRound, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
			],
			cards: baselineCards,
		},
		{
			key: "sessions", short: "Sessions", title: "Sessions", icon: ClipboardCheck, subtitle: "Completed session records", badge: `${done} completed · ${s.clients_served ?? 0} clients`,
			stats: [
				{ label: "Completed records", value: val(s.completed_sessions), icon: ClipboardCheck, tone: "bg-[#DCF3E4] text-[#146C3A]" },
				{ label: "Clients served", value: val(s.clients_served), icon: Users, tone: "bg-[#FCE8EB] text-[#A10E24]" },
				{ label: "Mean duration (min)", value: val(dur.mean), icon: Timer, tone: "bg-[#FDECC8] text-[#8A4B00]" },
				{ label: `Median duration (n=${dur.n ?? 0})`, value: val(dur.median), icon: Timer, tone: "bg-[#E0EAFD] text-[#1B4DB1]" },
			],
			cards: sessionCards,
		},
	]
	return { sections, rings, funnel, insights, glance }
})

const sections = computed(() => model.value?.sections || [])
const rings = computed(() => model.value?.rings || [])
const funnel = computed(() => model.value?.funnel || [])
const insights = computed(() => model.value?.insights || [])
const glance = computed(() => model.value?.glance || [])

function visibleCards(s) {
	const term = q.value.trim().toLowerCase()
	if (s.key === "overview" || !term) return s.cards
	return s.cards.filter((c) => (c.title || "").toLowerCase().includes(term))
}

onMounted(() => analysis.fetch())
</script>

<style scoped>
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid transparent; border-radius: 8px; padding: 10px 16px; font-size: 14px; font-weight: 600; line-height: 20px; white-space: nowrap; transition: background 0.15s, border-color 0.15s, color 0.15s; }
.btn:focus-visible, .seg:focus-visible, .view-btn:focus-visible { outline: 2px solid rgba(200, 16, 46, 0.45); outline-offset: 2px; }
.btn-secondary { border-color: #d9dbe0; background: #fff; color: #33353a; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.04); }
.btn-secondary:hover { border-color: #c8102e; color: #a10e24; }
.count-pill { display: inline-flex; min-width: 20px; height: 20px; align-items: center; justify-content: center; border-radius: 999px; background: #fce8eb; padding: 0 6px; font-size: 11px; font-weight: 700; color: #a10e24; }

.seg { display: inline-flex; flex: 1; align-items: center; justify-content: center; gap: 8px; border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: 600; color: #62656d; white-space: nowrap; transition: background 0.15s, color 0.15s; }
.seg:hover { color: #25272b; }
.seg-on { background: #fce8eb; color: #a10e24; }

.viz-card { overflow: hidden; border: 1px solid #e4e6ea; border-radius: 12px; background: #fff; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.03); transition: border-color 0.2s, box-shadow 0.2s; }
.viz-card:hover { border-color: #d9dbe0; box-shadow: 0 4px 14px -6px rgba(20, 25, 35, 0.12); }
.stat-card { transition: border-color 0.2s, box-shadow 0.2s; }
.stat-card:hover { border-color: #d9dbe0; box-shadow: 0 4px 14px -6px rgba(20, 25, 35, 0.12); }
.card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; border-bottom: 1px solid #ecedef; padding: 16px 20px; }
.chip { display: inline-flex; flex-shrink: 0; align-items: center; gap: 6px; border-radius: 999px; background: #f4f5f7; padding: 4px 10px; font-size: 11px; font-weight: 600; color: #62656d; }

.view-btn { position: relative; display: flex; height: 28px; width: 30px; align-items: center; justify-content: center; border-radius: 6px; color: #737780; transition: background 0.15s, color 0.15s; }
.view-btn:hover { color: #25272b; }
.view-btn-on { background: #fff; color: #a10e24; box-shadow: 0 1px 2px rgba(20, 25, 35, 0.12); }
.pin-dot { position: absolute; top: 3px; right: 3px; height: 6px; width: 6px; border-radius: 999px; background: #c8102e; box-shadow: 0 0 0 1.5px #f4f5f7; }
.view-btn-on .pin-dot { box-shadow: 0 0 0 1.5px #fff; }

.legend-row { transition: background 0.15s; }
.legend-row:hover { background: #f7f7f8; }
.bar-row { transition: opacity 0.15s; }

.col-grid { background-image: linear-gradient(to top, #f0f1f3 1px, transparent 1px); background-size: 100% 25%; }
.heat-tile { transition: transform 0.15s; }
.heat-tile:hover { transform: translateY(-1px); }

/* Animations */
.view-swap { animation: fade-in 0.25s ease both; }
.bar-fill { width: var(--w); animation: grow-x 0.8s cubic-bezier(0.22, 1, 0.36, 1) both; }
.col-bar { height: var(--h); animation: grow-y 0.8s cubic-bezier(0.22, 1, 0.36, 1) both; }
.funnel-bar { width: var(--w); animation: grow-x 0.9s cubic-bezier(0.22, 1, 0.36, 1) both; }
.stack-seg { animation: fade-in 0.7s ease both; transition: filter 0.15s; }
.stack-seg:hover { filter: brightness(1.1); }
.donut-seg { transition: opacity 0.2s; animation: dash-in 0.9s cubic-bezier(0.22, 1, 0.36, 1) both; }
.ring-seg { animation: dash-in 1s cubic-bezier(0.22, 1, 0.36, 1) both; }
.radar-poly { animation: fade-in 0.8s ease both; }
.plot-dot, .plot-range { animation: fade-in 0.8s ease both; }
@keyframes grow-x { from { width: 0; } to { width: var(--w); } }
@keyframes grow-y { from { height: 0; } to { height: var(--h); } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes dash-in { from { stroke-dasharray: 0 100; } }

.toast-enter-active, .toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 8px); }

@media (prefers-reduced-motion: reduce) {
	.view-swap, .bar-fill, .col-bar, .funnel-bar, .stack-seg, .donut-seg, .ring-seg, .radar-poly, .plot-dot, .plot-range { animation: none; }
	.toast-enter-active, .toast-leave-active { transition: none; }
}

@media print {
	.no-print { display: none !important; }
	main { min-height: 0 !important; background: #fff !important; padding: 0 !important; }
	.print-show { display: block !important; break-inside: avoid-page; margin-top: 24px; }
	.viz-card { break-inside: avoid; box-shadow: none !important; }
	.view-swap, .bar-fill, .col-bar, .funnel-bar, .stack-seg, .donut-seg, .ring-seg, .radar-poly, .plot-dot, .plot-range { animation: none; }
}
</style>
