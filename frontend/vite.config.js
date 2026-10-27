import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: true,
			buildConfig: {
				outDir: "../krcti_mhpss/public/frontend",
				indexHtmlPath: "../krcti_mhpss/www/frontend.html",
				emptyOutDir: true,
				sourcemap: false,
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../krcti_mhpss/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: false,
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	optimizeDeps: { include: ["feather-icons", "showdown", "highlight.js/lib/core", "interactjs"] },
	server: { allowedHosts: true },
})