import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

const isVercelBuild = process.env.VERCEL === "1"
const frappeAssetsDir = "../krcti_mhpss/public/frontend"

export default defineConfig({
	plugins: [
		frappeui({
			// Route dev API requests to this bench site explicitly. The proxy plugin's
			// default router uses the browser host, which can select the wrong site.
			frappeProxy: false,
			jinjaBootData: !isVercelBuild,
			lucideIcons: {
    componentGlobs: ['src/**/*.vue'],
  },
			buildConfig: isVercelBuild ? false : {
				outDir: frappeAssetsDir,
				indexHtmlPath: "../krcti_mhpss/www/frontend.html",
				emptyOutDir: true,
				sourcemap: false,
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: isVercelBuild ? "dist" : frappeAssetsDir,
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
	optimizeDeps: {
		include: ["feather-icons", "highlight.js/lib/core", "interactjs", "socket.io-client"],
		exclude: ["frappe-ui"],
	},
	server: {
		port: 8080,
		strictPort: true,
		allowedHosts: true,
		proxy: {
			"^/(desk|app|login|api|assets|files|private)": {
				target: "http://127.0.0.1:8000",
				changeOrigin: true,
				ws: true,
				headers: { "X-Frappe-Site-Name": "krcti.local" },
			},
		},
	},
})
