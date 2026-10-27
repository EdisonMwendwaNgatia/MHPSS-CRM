import "./data/busy"
import { Badge, Button, ErrorMessage, FormControl, FrappeUI, TextInput, frappeRequest, setConfig } from "frappe-ui"
import { createApp } from "vue"
import App from "./App.vue"
import PageLoader from "./components/PageLoader.vue"
import Spinner from "./components/Spinner.vue"
import "./index.css"
import router from "./router"

const globalComponents = { Badge, Button, ErrorMessage, FormControl, TextInput, PageLoader, Spinner }

const app = createApp(App)
setConfig("resourceFetcher", frappeRequest)
app.use(FrappeUI)
app.use(router)
for (const [name, component] of Object.entries(globalComponents)) app.component(name, component)
app.mount("#app")