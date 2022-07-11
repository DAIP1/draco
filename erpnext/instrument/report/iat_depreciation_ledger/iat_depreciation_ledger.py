# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	depreciation_accounts = frappe.db.sql_list(""" select name from tabAccount
		where ifnull(account_type, '') = 'Depreciation' """)

	filters_data = [["company", "=", filters.get('company')],
		["posting_date", ">=", filters.get('from_date')],
		["posting_date", "<=", filters.get('to_date')],
		["against_voucher_type", "=", "IaT"],
		["account", "in", depreciation_accounts]]

	if filters.get("iat"):
		filters_data.append(["against_voucher", "=", filters.get("iat")])

	if filters.get("tools_category"):

		instrument = frappe.db.sql_list("""select name from tabIaT
			where tools_category = %s and docstatus=1""", filters.get("tools_category"))

		filters_data.append(["against_voucher", "in", instrument])

	if filters.get("finance_book"):
		filters_data.append(["finance_book", "in", ['', filters.get('finance_book')]])

	gl_entries = frappe.get_all('GL Entry',
		filters= filters_data,
		fields = ["against_voucher", "debit_in_account_currency as debit", "voucher_no", "posting_date"],
		order_by= "against_voucher, posting_date")

	if not gl_entries:
		return data

	instrument = [d.against_voucher for d in gl_entries]
	instrument_details = get_instrument_details(instrument)

	for d in gl_entries:
		iat_data = instrument_details.get(d.against_voucher)
		if iat_data:
			if not iat_data.get("accumulated_depreciation_amount"):
				iat_data.accumulated_depreciation_amount = d.debit
			else:
				iat_data.accumulated_depreciation_amount += d.debit

			row = frappe._dict(iat_data)
			row.update({
				"depreciation_amount": d.debit,
				"depreciation_date": d.posting_date,
				"amount_after_depreciation": (flt(row.gross_purchase_amount) -
					flt(row.accumulated_depreciation_amount)),
				"depreciation_entry": d.voucher_no
			})

			data.append(row)

	return data

def get_instrument_details(instrument):
	instrument_details = {}

	fields = ["name as iat", "gross_purchase_amount",
		"tools_category", "status", "depreciation_method", "purchase_date"]

	for d in frappe.get_all("IaT", fields = fields, filters = {'name': ('in', instrument)}):
		instrument_details.setdefault(d.iat, d)

	return instrument_details

def get_columns():
	return [
		{
			"label": _("IaT"),
			"fieldname": "iat",
			"fieldtype": "Link",
			"options": "IaT",
			"width": 120
		},
		{
			"label": _("Depreciation Date"),
			"fieldname": "depreciation_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Purchase Amount"),
			"fieldname": "gross_purchase_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Depreciation Amount"),
			"fieldname": "depreciation_amount",
			"fieldtype": "Currency",
			"width": 140
		},
		{
			"label": _("Accumulated Depreciation Amount"),
			"fieldname": "accumulated_depreciation_amount",
			"fieldtype": "Currency",
			"width": 210
		},
		{
			"label": _("Amount After Depreciation"),
			"fieldname": "amount_after_depreciation",
			"fieldtype": "Currency",
			"width": 180
		},
		{
			"label": _("Depreciation Entry"),
			"fieldname": "depreciation_entry",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 140
		},
		{
			"label": _("Tools Category"),
			"fieldname": "tools_category",
			"fieldtype": "Link",
			"options": "Tools Category",
			"width": 120
		},
		{
			"label": _("Current Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Depreciation Method"),
			"fieldname": "depreciation_method",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("Purchase Date"),
			"fieldname": "purchase_date",
			"fieldtype": "Date",
			"width": 120
		}
	]
