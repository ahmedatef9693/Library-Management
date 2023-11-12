# Copyright (c) 2023, ahmed atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LibraryTransaction(Document):
	def before_submit(self):
		if self.type == "Issue":
			self.validate_membership()
			self.validate_max_limit()
			article = frappe.get_doc("Article",self.article)
			article.status = "Issued"
			article.save()
		elif self.type == "Return":
			self.validate_return()
			article = frappe.get_doc("Article",self.article)
			article.sttaus = "Available"
			article.save()


	def validate_membership(self):
		valid = frappe.db.exists(
			"Library Membership",
			{
				'library_member' : self.library_member,
				'docstatus' : 1,
				'from_date' : ("<",self.date_of_transaction),
				'to_date' : (">",self.date_of_transaction)
			}
		)
		if not valid:
			frappe.throw("you dont have a valid membership")

	def validate_return(self):
		article = frappe.get_doc("Article",self.article)
		if article.status == "Available":
			frappe.throw("Article Cannot Be Returned Without Being Issued First")

	def validate_max_limit(self):
		max_articles = frappe.db.get_single_value("Library Settings","max_articles")
		count = frappe.db.count("Library Transaction",
						  {
							'library_member' : self.library_member,
							'type':"Issue",
							'docstatus' : 1,  
						  })
		if count >= max_articles:
			frappe.throw(f"maximum articles reached for member {self.library_member}")
