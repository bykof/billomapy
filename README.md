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