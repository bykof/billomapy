===========
Quick Start
===========

Just initialize the Billomapy class and have fun

.. code-block:: python
    :linenos:

    from billomapy import Billomapy

    billomapy = Billomapy(
        'BILLOMAT_ID', 'API_KEY', 'APP_ID', 'APP_SECRET'
    )

    # Here you get all responses of billomat because there can be metadata in it you want to use
    all_client_responses = billomapy.get_all_clients()

    """
    all_client_responses will look like this:
        [
            'clients': {
                '@page': 1,
                    '@total': total_items,
                '@per_page': 1000,
                'client': [
                    {
                        'name': 'Tim',
                        'last_name': 'Tester',
                    }
                    ...
                ],
            },
            'clients': {
                '@page': 2,
                '@total': 2000,
                '@per_page': 1000,
                'client': [
                    {
                        'name': 'Peter',
                        'last_name': 'Griffin,
                    }
                    ...
                ],
            }
        ]
    """

    # If you want to have just a list of all clients you can use resolve_response_data
    # Import resources
    from billomapy.resources import CLIENT, CLIENTS

    clients = billomapy.resolve_response_data(
        head_key=CLIENTS,
        data_key=CLIENT,
        data=clients,
    )

    """
    Now the variable clients is a list of all client dicts
    clients:
        [
            {
                'name': 'Tim',
                'last_name': 'Tester',
                ...
            },
            {
                'name': 'Peter',
                'last_name': 'Griffin,
                ...
            },
            ...
        ]
    """

    for client in clients:
        print client.get('id'), client.get('name')


    # Retrieving one client
    client = billomapy.get_client(1000)

    """
    This will return just a dictionary with the client information
    client:
        {
            'name': 'Tim',
            'last_name': 'Tester',
            ...
        }
    """

    # Creating a client
    new_client = billomapy.create_client(
        {
            'client': {
                'name': 'test'
                'first_name': 'Peter',
                'last_name': 'Griffin',
            }
        }
    )

    # Updating a client
    updated_client = billomapy.update_client(
        new_client.get('id'),
        {
            'client': {
                'first_name': 'Meg'
			}
		}
	)

    # Deleting a client
    deleted_response_object = billomapy.delete_client(new_client.get('id'))

