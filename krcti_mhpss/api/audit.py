import frappe
from frappe import _
from frappe.utils import cint

from krcti_mhpss.api.oversight import _names
from krcti_mhpss.utils import DPO_ROLE, require_roles


@frappe.whitelist()
def audit_logs(start=0, page_length=100, search=None):
	"""Full immutable audit data is restricted to the KRCS Data Protection Officer."""
	require_roles(DPO_ROLE)
	start = max(0, cint(start))
	page_length = max(1, min(cint(page_length) or 100, 200))
	search = " ".join(str(search or "").split())[:80]
	filters = {}
	if search:
		like = f"%{search}%"
		or_filters = [["actor", "like", like], ["action", "like", like], ["affected_record", "like", like], ["details", "like", like]]
		rows = frappe.get_all("KRCTI Audit Log", filters=filters, or_filters=or_filters,
			fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"],
			order_by="creation desc", start=start, page_length=page_length)
		total = len(frappe.get_all("KRCTI Audit Log", filters=filters, or_filters=or_filters, pluck="name", limit=0))
	else:
		rows = frappe.get_all("KRCTI Audit Log", filters=filters,
			fields=["name", "actor", "action", "affected_record", "module", "outcome", "details", "creation"],
			order_by="creation desc", start=start, page_length=page_length)
		total = frappe.db.count("KRCTI Audit Log")
	actor_names = _names({row.actor for row in rows if row.actor})
	for row in rows:
		row["actor_name"] = actor_names.get(row.actor, row.actor)
	return {"logs": rows, "total": total, "start": start, "page_length": page_length}
