===========
Quick Start
===========

Initialize WITHOUT RATE LIMIT HANDLING!
=======================================

Just initialize the Billomapy class and have fun

.. code-block:: python
    :linenos:

    from billomapy import Billomapy

    billomapy = Billomapy(
        'BILLOMAT_ID', 'API_KEY', 'APP_ID', 'APP_SECRET'
    )


Initialize WITH RATE LIMIT HANDLING!
====================================

If you want to handle the rate limit in your application you will have to inherit the billomapy class in a custom class and overwrite the rate_limit_exceeded function.
Here is an example which will sleep until rate limit will reset and then send the request again.

.. code-block:: python
    :linenos:

    from billomapy import Billomapy
    import time

    class CustomBillomapy(object):
        def rate_limit_exceeded(response):
            rate_limit_reset = response.headers.get('X-Rate-Limit-Reset')
            if rate_limit_reset:
                seconds = (
                    datetime.datetime.fromtimestamp(float(rate_limit_reset)) -
                    datetime.datetime.now()
                ).seconds + 3
                if seconds > 0:
                    time.sleep(seconds)
                response = self.session.send(response.request)
                return self._handle_response(response)
            else:
                response.raise_for_status()

    billomapy = CustomBillomapy(
        'BILLOMAT_ID', 'API_KEY', 'APP_ID', 'APP_SECRET'
    )


Retrieve data
=============

If you want to retrieve data the pattern is: get_all_* where * speaks for the endpoint.

.. code-block:: python
    :linenos:

    """
	Here you get all responses of billomat
	because there can be metadata in it you want to use.
	So i just parse the response of billomat in python code. If you want to work easier with this data read further
	"""

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

    # If you want to have just a list of all clients you can use the function resolve_response_data
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


Retrieve single data
====================

If you want to retrieve single data the pattern is: get_* where * speaks for the endpoint.

.. code-block:: python
    :linenos:

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


Create data
===========

If you want to create data the pattern is: create_* where * speaks for the endpoint.

.. code-block:: python
    :linenos:

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


Update data
===========

If you want to update data the pattern is: update_* where * speaks for the endpoint.

.. code-block:: python
    :linenos:

    # Updating a client
    updated_client = billomapy.update_client(
        new_client.get('id'),
        {
            'client': {
                'first_name': 'Meg'
			}
		}
	)


Delete data
===========

If you want to delete data the pattern is: delete_* where * speaks for the endpoint.

.. code-block:: python
    :linenos:

    # Deleting a client
    deleted_response_object = billomapy.delete_client(new_client.get('id'))
