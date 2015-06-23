billomapy
===================

A full featured Python library for http://www.billomat.com/
----------

If you have problems or don't understanding something you can email me:

mbykovski@seibert-media.net


API Doc
-------



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
	
	from billomapy.resources import CLIENT
	clients = billomapy.get_all_clients()['client']
	
	"""
	Billomat response with a dictionay like this
	{
		'@page': current_page (in my api it is every time the last page),
		'@total': total_items,
		'@per_page': items_per_page,
		'client': clients_list,
	}
	"""


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