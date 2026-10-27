import frappeUIPreset from "frappe-ui/tailwind"

export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				gp: {
					DEFAULT: "#C8102E",
					light: "#E4002B",
					bg: "#FAF6F6",
					line: "#E4E9E4",
					ink: "#252925",
					muted: "#6B746C",
				},
			},
		},
	},
	plugins: [],
}