"""Build the Vue SPA as part of the Frappe asset build."""

from pathlib import Path
import shutil
import subprocess


def after_build():
	"""Compile the Vue frontend into this app's public assets."""
	frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
	yarn = shutil.which("yarn")
	if not yarn:
		raise RuntimeError("Yarn is required to build the KRCTI MHPSS frontend.")

	subprocess.run([yarn, "install", "--frozen-lockfile"], cwd=frontend_dir, check=True)
	subprocess.run([yarn, "build"], cwd=frontend_dir, check=True)
