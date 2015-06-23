billomapy
===================

A full featured Python library for http://www.billomat.com/
----------

If you have problems or don't understand something you can email me:

mbykovski@seibert-media.net


API Doc
-------
All inputs and output from and to the api have to be like in the api docs from billomat (http://www.billomat.com/en/api)
So please have a look in the API docs if you have a question. Otherwise email me.


Install:
-------

    pip install billomapy

Initialize:
----------

    from billomapy import Billomapy
    
    """
	:param billomat_id: Mostly the name of your company for example https://YOUR_COMPANY.billomat.net/api/
	:param api_key: The api key that you requested from billomat
	:param app_id: The app_id that you requested by billomat
	:param app_secret: The app_secret that you requested by billomat
	"""
    billomapy = Billomapy(
		billomat_id, api_key, app_id, app_secret
	)

Use it:
-------
	clients = billomapy.get_all_clients()['client']
	
	"""
	Billomat response with a dictionary like this
	{
		'@page': current_page (in my api it is every time the last page),
		'@total': total_items,
		'@per_page': items_per_page,
		'client': clients_list,
	}
	"""
	
	client = billomapy.get_client(billomat_id_of_client)['client']
	
	# Creates references on http://www.billomat.com/en/api/clients
	new_client = billomapy.create_client(
		{
			'client': {
				'name': 'test'
				'first_name': 'Peter',
				'last_name': 'Griffin',
			}	
		}
	)
	
	# Update references on http://www.billomat.com/en/api/clients
	updated_client = billomapy.update_client(new_client['id'], {'client': {'first_name': 'Meg'}})
	
	deleted_response_object = billomapy.delete_client(updated_clied['id'])

----------


Functions:
----------

**Clients**

	> get_clients_per_page(per_page=1000, page=1, params=None)
	> get_all_clients(params=None)
	> get_client(client_id)
	> create_client(client_dict)
	> update_client(client_id, client_dict)
	> delete_client(client_id)

**Client Properties**

	> get_client_properties_per_page(per_page=1000, page=1, params=None)
	> get_all_client_properties(params=None)
	> get_client_property(client_id)
	> create_client_property(client_dict)
	
**Client Tags**

	> get_client_tags_per_page(per_page=1000, page=1, params=None)
	> get_all_client_tags(params=None)
	> get_client_tag(client_id)
	> create_client_tag(client_dict)
	> delete_client_tag(client_id)

**Client Contacts**

	> get_contacts_of_client_per_page(client_id, per_page=1000, page=1, params=None)
    > get_all_contacts_of_client(client_id)´
    > get_contact_of_client(contact_id)
    > create_contact_of_client(contact_dict)
    > update_contact_of_client(contact_dict)
    > delete_contact_of_client(client_id)
    
**Suppliers**

	> get_suppliers_per_page(per_page=1000, page=1, params=None)
	> get_all_suppliers(params=None)
	> get_supplier(supplier_id)
	> create_supplier(supplier_dict)
	> update_supplier(supplier_id, supplier_dict)
	> delete_supplier(supplier_id)
	
**Supplier Properties**

	> get_supplier_properties_per_page(per_page=1000, page=1, params=None)
	> get_all_supplier_properties(params=None)
	> get_supplier_property(supplier_property_id)
	> set_supplier_property(supplier_property_dict)

**Supplier Tags**

	> get_tags_of_supplier_per_page(supplier_id, per_page=1000, page=1, params=None)
	> get_all_tags_of_supplier(supplier_id)
	> get_supplier_tag(supplier_tag_id)
	> create_supplier_tag(supplier_tag_dict)
	> delete_supplier_tag(supplier_tag_id)

**Articles**
	
	> get_articles_per_page(per_page=1000, page=1, params=None)
	> get_all_articles(params=None)
	> get_article(article_id)
	> create_article(article_dict)
	> update_article(article_id, article_dict)
	> delete_article(article_id)

**Article Properties**

	> get_article_properties_per_page(per_page=1000, page=1, params=None)
	> get_all_article_properties(params=None)
	> get_article_property(article_property_id)
	> set_article_property(article_property_dict)

**Article Tags**

	> get_tags_of_article_per_page(article_id, per_page=1000, page=1, params=None)
	> get_all_tags_of_article(article_id)
	> get_article_tag(article_tag_id)
	> create_article_tag(article_tag_dict)
	> delete_article_tag(article_tag_id)

**Unit**
	
	> get_units_per_page(per_page=1000, page=1, params=None)
	> get_all_units(params=None)
	> get_unit(unit_id)
	> create_unit(unit_dict)
	> update_unit(unit_id, unit_dict)
	> delete_unit(unit_id)

**Invoice**
	
	> get_invoices_per_page(per_page=1000, page=1, params=None)
	> get_all_invoices(params=None)
	> get_invoice(invoice_id)
	> create_invoice(invoice_dict)
	> update_invoice(invoice_id, invoice_dict)
	> delete_invoice(invoice_id)
	
**Invoice Item**
	
	> get_items_of_invoice_per_page(invoice_id, per_page=1000, page=1, params=None)
	> get_all_items_of_invoice(invoice_id)
	> get_invoice_item(invoice_item_id)
	> create_invoice_item(invoice_item_id)
	> update_invoice_item(invoice_item_id, invoice_item_dict)
	> delete_invoice_item(invoice_item_id)
	
**Invoice Comment**
	
	> get_comments_of_invoice_per_page(invoice_id, per_page=1000, page=1, params=None)
	> get_all_comments_of_invoice(invoice_id)
	> get_invoice_comment(invoice_comment_id)
	> create_invoice_comment(invoice_comment_dict)
	> update_invoice_comment(invoice_comment_id, invoice_comment_dict)
	> delete_invoice_comment(invoice_comment_id)
	
**Invoice Payment**
	
	> get_invoice_payments_per_page(per_page=1000, page=1, params=None)
	> get_all_invoice_payments()
	> get_invoice_payment(invoice_payment_id)
	> create_invoice_payment(invoice_payment_dict)
	> delete_invoice_payment(invoice_payment_id)

**Invoice Tags**
	
	> get_tags_of_invoice_per_page(invoice_id, per_page=1000, page=1, params=None)
	> get_all_tags_of_invoice(invoice_id)
	> get_invoice_tag(invoice_tag_id)
	> create_invoice_tag(invoice_tagt_dict)
	> delete_invoice_tag(invoice_tag_id)

**Recurrings**
	
	> get_recurrings_per_page(self, per_page=1000, page=1, params=None)
    	> get_all_recurrings(params=None)
    	> get_recurring(recurring_id)
    	> create_recurring(recurring_dict)
    	> update_recurring(recurring_id, recurring_dict)
	> delete_recurring(recurring_id)
	
**Recurring Items**

	> get_items_of_recurring_per_page(recurring_id, per_page=1000, page=1, params=None)
	> get_all_items_of_recurring(recurring_id)
	> get_recurring_item(recurring_item_id)
     	> create_recurring_item(recurring_item_dict)
	> update_recurring_item(recurring_item_id, recurring_item_dict)
	> delete_recurring_item(recurring_item_id)

**Recurring Tags**

	> get_tags_of_recurring_per_page(recurring_id, per_page=1000, page=1, params=None)
	> get_all_tags_of_recurring(recurring_id)
	> get_recurring_tag(recurring_tag_id)
	> create_recurring_tag(recurring_tag_dict)
	> delete_recurring_tag(recurring_tag_id)

**Recurring Email Receivers**

	> get_email_receivers_of_recurring_per_page(recurring_id, per_page=1000, page=1, params=None)
	> get_all_email_receivers_of_recurring(recurring_id)
	> get_recurring_email_receiver(recurring_email_receiver_id)
	> create_recurring_email_receiver(recurring_email_receiver_dict)
	> delete_recurring_email_receiver(recurring_email_receiver_id)

**Incomings**

	> get_incomings_per_page(per_page=1000, page=1, params=None)
	> get_all_incomings(params=None)
    	> get_incoming(incoming_id)
    	> create_incoming(incoming_dict)
    	> update_incoming(incoming_id, incoming_dict)
    	> delete_incoming(incoming_id)
    	
**Incoming Comments**

	> get_comments_of_incoming_per_page(incoming_id, per_page=1000, page=1, params=None)
    	> get_all_comments_of_incoming(incoming_id)
    	> get_incoming_comment(incoming_comment_id)
    	> create_incoming_comment(incoming_comment_dict)
    	> delete_incoming_comment(incoming_comment_id)
   
**Incoming Payments**

	> get_payments_of_incoming_per_page(incoming_id, per_page=1000, page=1, params=None:
    	> get_all_payments_of_incoming(incoming_id)
    	> get_incoming_payment(incoming_payment_id)
    	> create_incoming_payment(incoming_payment_dict)
    	> delete_incoming_payment(incoming_payment_id)

**Incoming Properties**
	
	> get_incoming_properties_per_page(per_page=1000, page=1, params=None)
    	> get_all_incoming_properties(params=None)
	> get_incoming_property(incoming_property_id)
	> set_incoming_property(incoming_dict)

**Incoming Tags**

	> get_tags_of_incoming_per_page(incoming_id, per_page=1000, page=1, params=None)
	> get_all_tags_of_incoming(incoming_id)
	> get_incoming_tag(incoming_tag_id)
    	> create_incoming_tag(incoming_tag_dict)
    	> delete_incoming_tag(incoming_tag_id)
   
**Inbox Documents**
	
	> get_inbox_documents_per_page(per_page=1000, page=1, params=None)
    	> get_all_inbox_documents()
	> get_inbox_document(inbox_document_id)
    	> create_inbox_document(inbox_document_dict)
    	> delete_inbox_document(inbox_document_id)

**Offers**
	
	> get_offers_per_page(per_page=1000, page=1, params=None)
	> get_all_offers(params=None)
    	> get_offer(offer_id)
    	> create_offer(offer_dict)
    	> update_offer(offer_id, offer_dict)
    	> delete_offer(offer_id)
    
**Offer Items**

	> get_items_of_offer_per_page(offer_id, per_page=1000, page=1, params=None)
    	> get_all_items_of_offer(offer_id)
   	> get_offer_item(offer_item_id)
	> create_offer_item(offer_item_dict)
	> update_offer_item(offer_item_id, offer_item_dict)
    	> delete_offer_item(offer_item_id)

**Offer Comments**

	> get_comments_of_offer_per_page(offer_id, per_page=1000, page=1, params=None)
    	> get_all_comments_of_offer(offer_id)
    	> get_offer_comment(offer_comment_id)
    	> create_offer_comment(offer_comment_dict)
    	> update_offer_comment(offer_comment_id, offer_comment_dict)
    	> delete_offer_comment(offer_comment_id)
    	
**Offer Tags**

	> get_tags_of_offer_per_page(offer_id, per_page=1000, page=1, params=None)
    	> get_all_tags_of_offer(offer_id)
    	> get_offer_tag(offer_tag_id)
    	> create_offer_tag(offer_tag_dict)
    	> delete_offer_tag(offer_tag_id)

**Credit Notes**

	> get_credit_notes_per_page(per_page=1000, page=1, params=None)
    	> get_all_credit_notes(params=None)
    	> get_credit_note(credit_note_id)
    	> create_credit_note(credit_note_dict)
    	> update_credit_note(credit_note_id, credit_note_dict)
    	> delete_credit_note(credit_note_id)
    	
**Credit Note Items**

	> get_items_of_credit_note_per_page(credit_note_id, per_page=1000, page=1, params=None)
    	> get_all_items_of_credit_note(credit_note_id)
    	> get_credit_note_item(credit_note_item_id)
    	> create_credit_note_item(credit_note_item_dict)
    	> update_credit_note_item(credit_note_item_id, credit_note_item_dict)
    	> delete_credit_note_item(credit_note_item_id)
    	

**Credit Note Comments**

	> get_comments_of_credit_note_per_page(credit_note_id, per_page=1000, page=1, params=None)
    	> get_all_comments_of_credit_note(credit_note_id)
    	> get_credit_note_comment(credit_note_comment_id)
    	> create_credit_note_comment(credit_note_comment_dict)
    	> update_credit_note_comment(credit_note_comment_id, credit_note_comment_dict)
    	> delete_credit_note_comment(credit_note_comment_id)

**Credit Note Payment**
		
	> get_payments_of_credit_note_per_page(credit_note_id, per_page=1000, page=1, params=None)
    	> get_all_payments_of_credit_note(credit_note_id)
    	> get_credit_note_payment(credit_note_payment_id)
    	> create_credit_note_payment(credit_note_payment_dict)
    	> delete_credit_note_payment(credit_note_payment_id)

**Credit Note Tags**
	
	> get_tags_of_credit_note_per_page(credit_note_id, per_page=1000, page=1, params=None)
    	> get_all_tags_of_credit_note(credit_note_id)
    	> get_credit_note_tag(credit_note_tag_id)
    	> create_credit_note_tag(credit_note_tag_dict)
    	> delete_credit_note_tag(credit_note_tag_id)
