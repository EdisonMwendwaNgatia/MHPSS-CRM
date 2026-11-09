app_name = "krcti_mhpss"
app_title = "Krcti Mhpss"
app_publisher = "KRCS Digital Transformation Team"
app_description = "MHPSS Case Management System"
app_email = "esibitaremmanuel316@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "krcti_mhpss",
# 		"logo": "/assets/krcti_mhpss/logo.png",
# 		"title": "Krcti Mhpss",
# 		"route": "/krcti_mhpss",
# 		"has_permission": "krcti_mhpss.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `krcti_mhpss/dock/krcti_mhpss/krcti_mhpss.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/krcti_mhpss/css/krcti_mhpss.css"
# app_include_js = "/assets/krcti_mhpss/js/krcti_mhpss.js"

# include js, css files in header of web template
# web_include_css = "/assets/krcti_mhpss/css/krcti_mhpss.css"
# web_include_js = "/assets/krcti_mhpss/js/krcti_mhpss.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "krcti_mhpss/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "krcti_mhpss/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "krcti_mhpss.utils.jinja_methods",
# 	"filters": "krcti_mhpss.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "krcti_mhpss.install.before_install"
# after_install = "krcti_mhpss.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "krcti_mhpss.uninstall.before_uninstall"
# after_uninstall = "krcti_mhpss.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "krcti_mhpss.utils.before_app_install"
# after_app_install = "krcti_mhpss.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "krcti_mhpss.utils.before_app_uninstall"
# after_app_uninstall = "krcti_mhpss.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

after_build = "krcti_mhpss.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "krcti_mhpss.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "krcti_mhpss.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["krcti_mhpss.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"krcti_mhpss.tasks.all"
# 	],
# 	"daily": [
# 		"krcti_mhpss.tasks.daily"
# 	],
# 	"hourly": [
# 		"krcti_mhpss.tasks.hourly"
# 	],
# 	"weekly": [
# 		"krcti_mhpss.tasks.weekly"
# 	],
# 	"monthly": [
# 		"krcti_mhpss.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "krcti_mhpss.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "krcti_mhpss.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "krcti_mhpss.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "krcti_mhpss.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["krcti_mhpss.utils.before_request"]
# after_request = ["krcti_mhpss.utils.after_request"]

# Job Events
# ----------
# before_job = ["krcti_mhpss.utils.before_job"]
# after_job = ["krcti_mhpss.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"krcti_mhpss.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# ---- KRCTI MHPSS ----
after_install = "krcti_mhpss.install.after_install"

permission_query_conditions = {
    "Client": "krcti_mhpss.permissions.client_conditions",
    "Baseline Survey": "krcti_mhpss.permissions.baseline_conditions",
    "Appointment": "krcti_mhpss.permissions.appointment_conditions",
}

has_permission = {
    "Client": "krcti_mhpss.permissions.client_has_permission",
    "Baseline Survey": "krcti_mhpss.permissions.baseline_has_permission",
    "Appointment": "krcti_mhpss.permissions.appointment_has_permission",
}

doc_events = {
    "User": {
        "after_insert": "krcti_mhpss.permissions.log_user_created",
        "validate": [
            "krcti_mhpss.permissions.validate_user_roles",
            "krcti_mhpss.permissions.validate_user_password",
        ],
        "on_update": "krcti_mhpss.permissions.log_user_updated",
    },
    "Client": {
        "after_insert": "krcti_mhpss.permissions.log_client_registration",
        "on_update": "krcti_mhpss.permissions.log_client_update",
    },
    "Appointment": {
        "after_insert": "krcti_mhpss.permissions.log_appointment_activity",
        "on_update": "krcti_mhpss.permissions.log_appointment_activity",
    }
}

on_login = "krcti_mhpss.permissions.log_user_login"
on_logout = "krcti_mhpss.permissions.log_user_logout"

# Recreate any missing role whenever the site is updated
after_migrate = ["krcti_mhpss.install.after_migrate"]

scheduler_events = {
    "cron": {
        "*/15 * * * *": ["krcti_mhpss.api.counsellor.notify_overdue_followups"],
    },
}

# The Frappe UI app at /frontend
website_route_rules = [{"from_route": "/frontend/<path:app_path>", "to_route": "frontend"}]
