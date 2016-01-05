[![Documentation Status](https://readthedocs.org/projects/billomapy/badge/?version=latest)](http://billomapy.readthedocs.org/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/billomapy.svg)](https://badge.fury.io/py/billomapy)
billomapy
===================

A full featured Python library for http://www.billomat.com/
----------

If you have problems or don't understand something you can email me:

mbykovski@seibert-media.net


API Doc
-------

Read the Docs: http://billomapy.readthedocs.org/en/latest/?badge=latest


All inputs and output from and to the api have to be like in the api docs from billomat (http://www.billomat.com/en/api)
So please have a look in the API docs if you have a question. Otherwise email me.


Install:
-------

PyPi: https://pypi.python.org/pypi/billomapy/

    pip install billomapy

Initialize:
----------

    from billomapy import Billomapy
    
    """
	billomat_id: Mostly the name of your company for example https://YOUR_COMPANY.billomat.net/api/
	api_key: The api key that you requested from billomat
	app_id: The app_id that you requested by billomat
	app_secret: The app_secret that you requested by billomat
	"""
	
    billomapy = Billomapy(
		billomat_id, api_key, app_id, app_secret
	)

Use it:
-------
	clients = billomapy.get_all_clients()
	
	"""
	Billomat response with a dictionary like this
	[
		{
			'@page': current_page (in my api it is every time the last page),
			'@total': total_items,
			'@per_page': items_per_page,
			'clients': ,
		}
	]
	"""
	
	client = billomapy.get_client(billomat_id_of_client)
	
	# Import resource
	from billomapy.resources import CLIENT
	
	# Creting references on http://www.billomat.com/en/api/clients
	new_client = billomapy.create_client(
		{
			'client': {
				'name': 'test'
				'first_name': 'Peter',
				'last_name': 'Griffin',
			}	
		}
	)
	
	updated_client = billomapy.update_client(new_client[CLIENT]['id'], {'client': {'first_name': 'Meg'}})
	deleted_response_object = billomapy.delete_client(new_client[CLIENT]['id'])

----------