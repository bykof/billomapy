===========
Quick Start
===========

Just initialize the Billomapy class and have fun

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