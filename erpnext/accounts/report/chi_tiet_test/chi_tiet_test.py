# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def validate_filters(filters):
	
	if filters.get('maso'):
		filters.account = frappe.parse_json(filters.get('maso'))

def get_columns(filters):
	columns = [
		{
			"label": _("Ma So"),
			"fieldtype": "Data",
			"fieldname": "maso",
			"options": "BangCanDoiKeToan",
			"width": 100
		}
		
	]

	return columns


def get_data(filters):

	data = []
	a =filters.get('maso')
	row={}
	if(a=='100'):
		row = {"maso": 'hello'}

	data.append(row)
	return data
