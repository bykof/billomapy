#########
billomapy
#########

+++++++++++
Description
+++++++++++

Welcome to billomapy a full featured Python library for http://www.billomat.com/

If you have problems or don’t understand something you can email me:
mbykovski@seibert-media.net

**All inputs and outputs of and to the api have to be like in the api docs from billomat (http://www.billomat.com/en/api) So please have a look in the API docs if you have a question. Otherwise email me.**

+++++++++++
Quick Start
+++++++++++

Just initialize the Billomapy Class and have fun

.. code-block:: python

    from billomapy import Billomapy

    billomapy = Billomapy(
        'BILLOMAT_ID', 'API_KEY', 'APP_ID', 'APP_SECRET'
    )

    # Here you get all responses of billomat because there can be metadata in it you want to use
    all_client_responses = billomapy.get_all_clients()

    clients = billomapy.resolve_response_data(
        CLIENTS,
        CLIENT,
        all_client_responses,
    )

    for client in clients:
        print client.get('id'), client.get('name')
