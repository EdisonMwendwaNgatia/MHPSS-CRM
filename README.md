### Krcti Mhpss

MHPSS Case Management System

The Vue frontend is built into `krcti_mhpss/public/frontend` whenever Frappe builds
this app. The generated `www/frontend.html` serves the SPA at `/frontend`, while
Frappe's route rule sends nested frontend routes back to the same application page.
Use `bench build --app krcti_mhpss` to rebuild the backend assets and frontend together.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app krcti_mhpss
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/krcti_mhpss
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
