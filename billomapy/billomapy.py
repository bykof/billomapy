import math
import json

import requests

from resources import *


class Billomapy(object):
    """
    Billomapy is a full featured python api for Billomat (http://billomat.com)

    Some important things for developer:
    Billomat API Docs: http://www.billomat.com/api

    :param billomat_id: Mostly the name of your company for example https://YOUR_COMPANY.billomat.net/api/
    :param api_key: The api key that you requested from billomat
    :param app_id: The app_id that you requested by billomat
    :param app_secret: The app_secret that you requested by billomat
    """

    def __init__(self, billomat_id, api_key, app_id, app_secret):
        self.billomat_id = billomat_id
        self.api_key = api_key
        self.app_id = app_id
        self.app_secret = app_secret

        self.api_url = "https://{}.billomat.net/api/".format(billomat_id)
        self.session = requests.session()
        self.session.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-BillomatApiKey': self.api_key,
                'X-AppId': self.app_id,
                'X-AppSecret': self.app_secret,
            }
        )

    def _create_get_request(self, resource, billomat_id='', command=None, params=None):
        """
        Creates a get request and return the response data
        """
        if not params:
            params = {}

        if not command:
            command = ''
        else:
            command = '/' + command

        assert (isinstance(resource, basestring))
        if billomat_id:
            assert (isinstance(billomat_id, int) or isinstance(billomat_id, basestring))

            if isinstance(billomat_id, int):
                billomat_id = str(billomat_id)
        response = self.session.get(
            url=self.api_url + resource + ('/' + billomat_id if billomat_id else '') + command,
            params=params,
        )

        return self._handle_response(response)

    def _create_post_request(self, resource, send_data, billomat_id='', command=None):
        """
        Creates a post request and return the response data
        """
        assert (isinstance(resource, basestring))

        if billomat_id:
            if isinstance(billomat_id, int):
                billomat_id = str(billomat_id)

        if not command:
            command = ''
        else:
            command = '/' + command

        response = self.session.post(
            url=self.api_url + resource + ('/' + billomat_id if billomat_id else '') + command,
            data=json.dumps(send_data),
        )

        return self._handle_response(response)

    def _create_put_request(self, resource, billomat_id, command=None, send_data=None):
        """
        Creates a put request and return the response data
        """
        assert (isinstance(resource, basestring))

        if isinstance(billomat_id, int):
            billomat_id = str(billomat_id)

        if not command:
            command = ''
        else:
            command = '/' + command

        response = self.session.put(
            url=self.api_url + resource + '/' + billomat_id + command,
            data=json.dumps(send_data),
        )

        return self._handle_response(response)

    def _create_delete_request(self, resource, billomat_id):
        """
        Creates a post request and return the response data
        """
        assert (isinstance(resource, basestring))

        if isinstance(billomat_id, int):
            billomat_id = str(billomat_id)

        response = self.session.delete(
            url=self.api_url + resource + '/' + billomat_id,
        )

        return self._handle_response(response)

    def _handle_response(self, response):
        """
        Handle all responses
        :param response:
        :type response:
        :return:
        :rtype:
        """
        if response.status_code == requests.codes.ok or response.status_code == requests.codes.created:
            try:
                return response.json()
            except ValueError:
                return response
        else:
            return self._handle_failed_response(response)

    def _handle_failed_response(self, response):
        """
        Handle the failed response and check for rate limit exceeded
        If rate limit exceeded it runs the rate_limit_exceeded function which you should overwrite

        :param response: requests.Response
        :type response: requests.Reponse
        :return: None
        :rtype: None
        """
        if response.status_code == requests.codes.too_many_requests:
            return self.rate_limit_exceeded(response)
        else:
            response.raise_for_status()

    @staticmethod
    def _iterate_through_pages(get_function, resource, **kwargs):
        """
        Iterate through all pages and return the collected data
        :rtype: list
        """

        request_data = True
        data = []
        page = 1

        while request_data:
            temp_response = get_function(page=page, **kwargs)
            if temp_response[resource]['@total'] != '0':
                data.append(temp_response)

            page += 1
            if page > int(
                math.ceil(
                    float(temp_response[resource]['@total']) / float(temp_response[resource]['@per_page'])
                )
            ):
                request_data = False
        return data

    def _get_resource_per_page(self, resource, per_page=1000, page=1, params=None):
        """
        Gets specific data per resource page and per page
        """
        assert (isinstance(resource, basestring))

        common_params = {'per_page': per_page, 'page': page}
        if not params:
            params = common_params
        else:
            params.update(common_params)
        return self._create_get_request(resource=resource, params=params)

    @staticmethod
    def resolve_response_data(head_key, data_key, data):
        """
        Resolves the responses you get from billomat
        If you have done a get_one_element request then you will get a dictionary
        If you have done a get_all_elements request then you will get a list with all elements in it

        :param head_key: the head key e.g: CLIENTS
        :param data_key: the data key e.g: CLIENT
        :param data: the responses you got
        :return: dict or list
        """
        new_data = []
        if isinstance(data, list):
            for data_row in data:
                if head_key in data_row and data_key in data_row[head_key]:
                    if isinstance(data_row[head_key][data_key], list):
                        new_data += data_row[head_key][data_key]
                    else:
                        new_data.append(data_row[head_key][data_key])
                elif data_key in data_row:
                    return data_row[data_key]

        else:
            if head_key in data and data_key in data[head_key]:
                new_data += data[head_key][data_key]
            elif data_key in data:
                    return data[data_key]
        return new_data

    def rate_limit_exceeded(self, response):
        """
        Overwrite this function to handle the rate limit exceeded error
        Example: do a delay for next request

        :param response: request.Response
        :rtype response: request.Response
        :return: None
        """
        response.raise_for_status()
        pass

    """
    --------
    Billomat Clients
    --------
    http://www.billomat.com/en/api/clients
    """

    def get_clients_per_page(self, per_page=1000, page=1, params=None):
        """
        Get clients per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=CLIENTS, per_page=per_page, page=page, params=params)

    def get_all_clients(self, params=None):
        """
        Get all clients
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_clients_per_page,
            resource=CLIENTS,
            **{'params': params}
        )

    def get_client(self, client_id):
        """
        Get a specific client

        :param client_id: The specific client id
        :return: dict
        """
        return self._create_get_request(resource=CLIENTS, billomat_id=client_id)

    def create_client(self, client_dict):
        """
        Creates a client

        :param client_dict: dict
        :return: dict
        """
        return self._create_post_request(CLIENTS, client_dict)

    def update_client(self, client_id, client_dict):
        """
        Updates a client

        :param client_id: the client id
        :param client_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CLIENTS,
            billomat_id=client_id,
            send_data=client_dict
        )

    def delete_client(self, client_id):
        """
        Deletes a client

        :param client_id: the client id
        :return: Response
        """
        return self._create_delete_request(CLIENTS, client_id)

    """
    --------
    Billomat Client Properties
    --------
    http://www.billomat.com/en/api/clients/properties
    """

    def get_client_properties_per_page(self, per_page=1000, page=1, params=None):
        """
        Get client properties per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(
            resource=CLIENT_PROPERTIES,
            per_page=per_page,
            page=page,
            params=params
        )

    def get_all_client_properties(self, params=None):
        """
        Get all contacts of client
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_client_properties_per_page,
            resource=CLIENT_PROPERTIES,
            **{'params': params}
        )

    def get_client_property(self, client_property_id):
        """
        Get a specific client property

        :param client_property_id: The specific client property id
        :return: dict
        """
        return self._create_get_request(resource=CLIENT_PROPERTIES, billomat_id=client_property_id)

    def create_client_property(self, client_property_dict):
        """
        Created a client property

        :param client_property_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CLIENT_PROPERTIES, send_data=client_property_dict)

    """
    --------
    Billomat Client Tags
    --------
    http://www.billomat.com/en/api/clients/tags
    """

    def get_client_tags_per_page(self, per_page=1000, page=1, params=None):
        """
        Get client tags per page

        If you search tags, you can only search by client_id

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(
            resource=CLIENT_TAGS,
            per_page=per_page,
            page=page,
            params=params
        )

    def get_all_client_tags(self, params=None):
        """
        Get all client tags
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_client_tags_per_page,
            resource=CLIENT_TAGS,
            **{'params': params}
        )

    def get_client_tag(self, client_tag_id):
        """
        Get a specific client tag

        :param client_tag_id: The specific client tag id
        :return: dict
        """
        return self._create_get_request(resource=CLIENT_TAGS, billomat_id=client_tag_id)

    def create_client_tag(self, client_tag_dict):
        """
        Creates a client tag

        :param client_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CLIENT_TAGS, send_data=client_tag_dict)

    def delete_client_tag(self, client_tag_id):
        """
        Deletes a client tag

        :param client_tag_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=CLIENT_TAGS, billomat_id=client_tag_id)

    """
    --------
    Billomat Contacts
    --------
    http://www.billomat.com/en/api/clients/contacts
    """

    def get_contacts_of_client_per_page(self, client_id, per_page=1000, page=1):
        """
        Get contacts of client per page

        :param client_id: the client id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CONTACTS,
            per_page=per_page,
            page=page,
            params={'client_id': client_id},
        )

    def get_all_contacts_of_client(self, client_id):
        """
        Get all contacts of client
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param client_id: The id of the client
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_contacts_of_client_per_page,
            resource=CONTACTS,
            **{'client_id': client_id}
        )

    def get_contact_of_client(self, contact_id):
        """
        Get a specific contact

        :param contact_id: The specific contact id
        :return: dict
        """
        return self._create_get_request(CONTACTS, contact_id)

    def create_contact_of_client(self, contact_dict):
        """
        Creates a contact

        :param contact_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CONTACTS, send_data=contact_dict)

    def update_contact_of_client(self, contact_id, contact_dict):
        """
        Updates a contact

        :param contact_id: the id of the contact
        :param contact_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=CONTACTS, billomat_id=contact_id, send_data=contact_dict)

    def delete_contact_of_client(self, contact_id):
        """
        Deletes a contact

        :param contact_id: dict
        :return: dict
        """
        return self._create_delete_request(resource=CONTACTS, billomat_id=contact_id)

    """
    --------
    Billomat Supplier
    --------
    http://www.billomat.com/en/api/suppliers
    """

    def get_suppliers_per_page(self, per_page=1000, page=1, params=None):
        """
        Get suppliers per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=SUPPLIERS, per_page=per_page, page=page, params=params)

    def get_all_suppliers(self, params=None):
        """
        Get all suppliers
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            get_function=self.get_suppliers_per_page,
            resource=SUPPLIERS,
            **{'params': params}
        )

    def get_supplier(self, supplier_id):
        """
        Get a specific supplier

        :param supplier_id: The specific supplier id
        :return: dict
        """
        return self._create_get_request(resource=SUPPLIERS, billomat_id=supplier_id)

    def create_supplier(self, supplier_dict):
        """
        Creates a supplier

        :param supplier_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=SUPPLIERS, send_data=supplier_dict)

    def update_supplier(self, supplier_id, supplier_dict):
        """
        Updates a supplier

        :param supplier_id: the supplier id
        :param supplier_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=SUPPLIERS, billomat_id=supplier_id, send_data=supplier_dict)

    def delete_supplier(self, supplier_id):
        """
        Creates a contact

        :param supplier_id: the supplier id
        :return: Response
        """
        return self._create_delete_request(resource=SUPPLIERS, billomat_id=supplier_id)

    """
    --------
    Billomat Supplier Properties
    --------
    http://www.billomat.com/en/api/suppliers/properties
    """

    def get_supplier_properties_per_page(self, per_page=1000, page=1, params=None):
        """
        Get supplier properties per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=SUPPLIER_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_supplier_properties(self, params=None):
        """
        Get all supplier properties
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            get_function=self.get_supplier_properties_per_page,
            resource=SUPPLIER_PROPERTIES,
            **{'params': params}
        )

    def get_supplier_property(self, supplier_property_id):
        """
        Get a specific supplier property

        :param supplier_property_id: The specific supplier property id
        :return: dict
        """
        return self._create_get_request(resource=SUPPLIER_PROPERTIES, billomat_id=supplier_property_id)

    def create_supplier_property(self, supplier_dict):
        """
        Creates a supplier property

        :param supplier_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=SUPPLIER_PROPERTIES, send_data=supplier_dict)

    """
    --------
    Billomat Supplier Tags
    --------
    http://www.billomat.com/en/api/suppliers/tags
    """
    def get_tags_of_supplier_per_page(self, supplier_id, per_page=1000, page=1):
        """
        Get tags of suppliers per page

        :param supplier_id: the supplier id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=SUPPLIER_TAGS,
            per_page=per_page,
            page=page,
            params={'supplier_id': supplier_id},
        )

    def get_all_tags_of_supplier(self, supplier_id):
        """
        Get all supplier properties
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param supplier_id: the supplier id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_supplier_per_page,
            resource=SUPPLIER_TAGS,
            **{'supplier_id': supplier_id}
        )

    def get_supplier_tag(self, supplier_tag_id):
        """
        Get a specific supplier tag

        :param supplier_tag_id: The specific supplier tag id
        :return: dict
        """
        return self._create_get_request(resource=SUPPLIER_TAGS, billomat_id=supplier_tag_id)

    def create_supplier_tag(self, supplier_tag_dict):
        """
        Creates a supplier tag

        :param supplier_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=SUPPLIER_TAGS, send_data=supplier_tag_dict)

    def delete_supplier_tag(self, supplier_tag_id):
        """
        Deletes a supplier tag

        :param supplier_tag_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=SUPPLIER_TAGS, billomat_id=supplier_tag_id)

    """
    --------
    Billomat Articles
    --------
    http://www.billomat.com/en/api/articles
    """
    def get_articles_per_page(self, per_page=1000, page=1, params=None):
        """
        Get articles per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=ARTICLES, per_page=per_page, page=page, params=params)

    def get_all_articles(self, params=None):
        """
        Get all articles
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_articles_per_page, resource=ARTICLES, **{'params': params})

    def get_article(self, article_id):
        """
        Get a specific article

        :param article_id: The specific article id
        :return: dict
        """
        return self._create_get_request(resource=ARTICLES, billomat_id=article_id)

    def create_article(self, article_dict):
        """
        Creates an article

        :param article_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=ARTICLES, send_data=article_dict)

    def update_article(self, article_id, article_dict):
        """
        Updates an article

        :param article_id: the article id
        :param article_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=ARTICLES, billomat_id=article_id, send_data=article_dict)

    def delete_article(self, article_id):
        """
        Deletes an article

        :param article_id: the article id
        :return: Response
        """
        return self._create_delete_request(resource=ARTICLES, billomat_id=article_id)

    """
    --------
    Billomat Article Properties
    --------
    http://www.billomat.com/en/api/articles/properties
    """

    def get_article_properties_per_page(self, per_page=1000, page=1, params=None):
        """
        Get article properties per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=ARTICLE_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_article_properties(self, params=None):
        """
        Get all article properties
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            get_function=self.get_article_properties_per_page,
            resource=ARTICLE_PROPERTIES,
            **{'params': params}
        )

    def get_article_property(self, article_property_id):
        """
        Get a specific article property

        :param article_property_id: The specific article property id
        :return: dict
        """
        return self._create_get_request(resource=ARTICLE_PROPERTIES, billomat_id=article_property_id)

    def create_article_property(self, article_property_dict):
        """
        Creates an article property

        :param article_property_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=ARTICLE_PROPERTIES, send_data=article_property_dict)

    """
    --------
    Billomat Article Tags
    --------
    http://www.billomat.com/en/api/articles/tags
    """
    def get_tags_of_article_per_page(self, article_id, per_page=1000, page=1):
        """
        Get articles tags per page

        :param article_id: the article id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=ARTICLE_TAGS,
            per_page=per_page,
            page=page,
            params={'article_id': article_id},
        )

    def get_all_tags_of_article(self, article_id):
        """
        Get all tags of article
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param article_id: the article id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_article_per_page,
            resource=ARTICLE_TAGS,
            **{'article_id': article_id}
        )

    def get_article_tag(self, article_tag_id):
        """
        Get a specific article tag

        :param article_tag_id: The specific article tag id
        :return: dict
        """
        return self._create_get_request(resource=ARTICLE_TAGS, billomat_id=article_tag_id)

    def create_article_tag(self, article_tag_dict):
        """
        Creates an article tag

        :param article_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=ARTICLE_TAGS, send_data=article_tag_dict)

    def delete_article_tag(self, article_tag_id):
        """
        Deletes an article tag

        :param article_tag_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=ARTICLE_TAGS, billomat_id=article_tag_id)

    """
    --------
    Billomat Unit
    --------
    http://www.billomat.com/en/api/units
    """

    def get_units_per_page(self, per_page=1000, page=1, params=None):
        """
        Get units per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=UNITS, per_page=per_page, page=page, params=params)

    def get_all_units(self, params=None):
        """
        Get all units
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_units_per_page, resource=UNITS, **{'params': params})

    def get_unit(self, unit_id):
        """
        Get a specific unit

        :param unit_id: The specific unit id
        :return: dict
        """
        return self._create_get_request(resource=UNITS, billomat_id=unit_id)

    def create_unit(self, unit_dict):
        """
        Creates an unit

        :param unit_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=UNITS, send_data=unit_dict)

    def update_unit(self, unit_id, unit_dict):
        """
        Updates an unit

        :param unit_id: the unit id
        :param unit_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=UNITS, billomat_id=unit_id, send_data=unit_dict)

    def delete_unit(self, unit_id):
        """
        Deletes an unit

        :param unit_id: the unit id
        :return: Response
        """
        return self._create_delete_request(resource=UNITS, billomat_id=unit_id)

    """
    --------
    Billomat Invoice
    --------
    http://www.billomat.com/en/api/invoices
    """

    def get_invoices_per_page(self, per_page=1000, page=1, params=None):
        """
        Get invoices per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=INVOICES, per_page=per_page, page=page, params=params)

    def get_all_invoices(self, params=None):
        """
        Get all invoices
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_invoices_per_page, resource=INVOICES, **{'params': params})

    def get_invoice(self, invoice_id):
        """
        Get a specific invoice

        :param invoice_id: The specific invoice id
        :return: dict
        """
        return self._create_get_request(resource=INVOICES, billomat_id=invoice_id)

    def create_invoice(self, invoice_dict):
        """
        Creates an invoice

        :param invoice_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INVOICES, send_data=invoice_dict)

    def update_invoice(self, invoice_id, invoice_dict):
        """
        Updates an invoice

        :param invoice_id: the invoice id
        :param invoice_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=INVOICES, billomat_id=invoice_id, send_data=invoice_dict)

    def delete_invoice(self, invoice_id):
        """
        Deletes an invoice

        :param invoice_id: the invoice id
        :return: Response
        """
        return self._create_delete_request(resource=INVOICES, billomat_id=invoice_id)

    def complete_invoice(self, invoice_id, complete_dict):
        """
        Completes an invoice

        :param complete_dict: the complete dict with the template id
        :param invoice_id: the invoice id
        :return: Response
        """
        return self._create_put_request(
            resource=INVOICES,
            billomat_id=invoice_id,
            command=COMPLETE,
            send_data=complete_dict
        )

    def invoice_pdf(self, invoice_id):
        """
        Opens a pdf of an invoice

        :param invoice_id: the invoice id
        :return: dict
        """
        return self._create_get_request(resource=INVOICES, billomat_id=invoice_id, command=PDF)

    def upload_invoice_signature(self, invoice_id, signature_dict):
        """
        Uploads a signature for the invoice

        :param signature_dict: the signature
        :type signature_dict: dict
        :param invoice_id: the invoice id
        :return Response
        """
        return self._create_put_request(
            resource=INVOICES,
            billomat_id=invoice_id,
            send_data=signature_dict,
            command=UPLOAD_SIGNATURE
        )

    def send_invoice_email(self, invoice_id, email_dict):
        """
        Sends an invoice by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param invoice_id: the invoice id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=INVOICES,
            billomat_id=invoice_id,
            send_data=email_dict,
            command=EMAIL,
        )

    def cancel_invoice(self, invoice_id):
        """
        Cancelles an invoice

        :param invoice_id: the invoice id
        :return Response
        """
        return self._create_put_request(
            resource=INVOICES,
            billomat_id=invoice_id,
            command=CANCEL,
        )

    def uncancel_invoice(self, invoice_id):
        """
        Uncancelles an invoice

        :param invoice_id: the invoice id
        """
        return self._create_put_request(
            resource=INVOICES,
            billomat_id=invoice_id,
            command=UNCANCEL,
        )

    """
    --------
    Billomat Invoice Item
    --------
    http://www.billomat.com/en/api/invoices/items
    """

    def get_items_of_invoice_per_page(self, invoice_id, per_page=1000, page=1):
        """
        Get invoice items of invoice per page

        :param invoice_id: the invoice id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INVOICE_ITEMS,
            per_page=per_page,
            page=page,
            params={'invoice_id': invoice_id},
        )

    def get_all_items_of_invoice(self, invoice_id):
        """
        Get all items of invoice
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param invoice_id: the invoice id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_invoice_per_page,
            resource=INVOICE_ITEMS,
            **{'invoice_id': invoice_id}
        )

    def get_invoice_item(self, invoice_item_id):
        """
        Get a specific invoice item

        :param invoice_item_id: The specific invoice_item id
        :return: dict
        """
        return self._create_get_request(INVOICE_ITEMS, invoice_item_id)

    def create_invoice_item(self, invoice_item_dict):
        """
        Creates an invoice item

        :param invoice_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INVOICE_ITEMS, send_data=invoice_item_dict)

    def update_invoice_item(self, invoice_item_id, invoice_item_dict):
        """
        Updates an invoice item

        :param invoice_item_id: the invoice item id
        :param invoice_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=INVOICE_ITEMS,
            billomat_id=invoice_item_id,
            send_data=invoice_item_dict
        )

    def delete_invoice_item(self, invoice_item_id):
        """
        Deletes an invoice item

        :param invoice_item_id: the invoice item id
        :return: Response
        """
        return self._create_delete_request(resource=INVOICE_ITEMS, billomat_id=invoice_item_id)

    """
    --------
    Billomat Invoice Comment
    --------
    http://www.billomat.com/en/api/invoices/comments
    """

    def get_comments_of_invoice_per_page(self, invoice_id, per_page=1000, page=1):
        """
        Get comments of invoice per page

        :param invoice_id: the invoice id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INVOICE_COMMENTS,
            per_page=per_page,
            page=page,
            params={'invoice_id': invoice_id},
        )

    def get_all_comments_of_invoice(self, invoice_id):
        """
        Get all invoice comments of invoice
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param invoice_id: the invoice id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_invoice_per_page,
            resource=INVOICE_COMMENTS,
            **{'invoice_id': invoice_id}
        )

    def get_invoice_comment(self, invoice_comment_id):
        """
        Get a specific invoice comment

        :param invoice_comment_id: The specific invoice comment id
        :return: dict
        """
        return self._create_get_request(INVOICE_COMMENTS, invoice_comment_id)

    def create_invoice_comment(self, invoice_comment_dict):
        """
        Creates an invoice comment

        :param invoice_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INVOICE_COMMENTS, send_data=invoice_comment_dict)

    def update_invoice_comment(self, invoice_comment_id, invoice_comment_dict):
        """
        Updates an invoice comment

        :param invoice_comment_id: the invoice comment id
        :param invoice_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=INVOICE_COMMENTS,
            billomat_id=invoice_comment_id,
            send_data=invoice_comment_dict
        )

    def delete_invoice_comment(self, invoice_comment_id):
        """
        Deletes an invoice comment

        :param invoice_comment_id: the invoice comment id
        :return: Response
        """
        return self._create_delete_request(resource=INVOICE_COMMENTS, billomat_id=invoice_comment_id)

    """
    --------
    Billomat Invoice Payment
    --------
    http://www.billomat.com/en/api/invoices/payments
    """

    def get_invoice_payments_per_page(self, per_page=1000, page=1, params=None):
        """
        Get invoice payments per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        if not params:
            params = {}

        return self._get_resource_per_page(
            resource=INVOICE_PAYMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_invoice_payments(self, params=None):
        """
        Get all invoice payments
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            get_function=self.get_invoice_payments_per_page,
            resource=INVOICE_PAYMENTS,
            **{'params': params}
        )

    def get_invoice_payment(self, invoice_payment_id):
        """
        Get a specific invoice payments

        :param invoice_payment_id: The specific invoice payment id
        :return: dict
        """
        return self._create_get_request(INVOICE_PAYMENTS, invoice_payment_id)

    def create_invoice_payment(self, invoice_payment_dict):
        """
        Creates an invoice payment

        :param invoice_payment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INVOICE_PAYMENTS, send_data=invoice_payment_dict)

    def delete_invoice_payment(self, invoice_payment_id):
        """
        Deletes an invoice payment

        :param invoice_payment_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=INVOICE_PAYMENTS, billomat_id=invoice_payment_id)

    """
    --------
    Billomat Invoice Tags
    --------
    http://www.billomat.com/en/api/invoices/tags
    """
    def get_tags_of_invoice_per_page(self, invoice_id, per_page=1000, page=1):
        """
        Get tags of invoice per page

        :param invoice_id: the invoice id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INVOICE_TAGS,
            per_page=per_page,
            page=page,
            params={'invoice_id': invoice_id},
        )

    def get_all_tags_of_invoice(self, invoice_id):
        """
        Get all tags of invoice
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param invoice_id: the invoice id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_invoice_per_page,
            resource=INVOICE_TAGS,
            **{'invoice_id': invoice_id}
        )

    def get_invoice_tag(self, invoice_tag_id):
        """
        Get a specific invoice tag

        :param invoice_tag_id: The specific invoice tag id
        :return: dict
        """
        return self._create_get_request(resource=INVOICE_TAGS, billomat_id=invoice_tag_id)

    def create_invoice_tag(self, invoice_tag_dict):
        """
        Creates an invoice tag

        :param invoice_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INVOICE_TAGS, send_data=invoice_tag_dict)

    def delete_invoice_tag(self, invoice_tag_id):
        """
        Deletes an invoice tag

        :param invoice_tag_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=INVOICE_TAGS, billomat_id=invoice_tag_id)

    """
    --------
    Billomat Recurring
    --------
    http://www.billomat.com/en/api/recurrings
    """

    def get_recurrings_per_page(self, per_page=1000, page=1, params=None):
        """
        Get recurrings per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=RECURRINGS, per_page=per_page, page=page, params=params)

    def get_all_recurrings(self, params=None):
        """
        Get all recurrings
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_recurrings_per_page, resource=RECURRINGS, **{'params': params})

    def get_recurring(self, recurring_id):
        """
        Get a specific recurring

        :param recurring_id: The specific recurring id
        :return: dict
        """
        return self._create_get_request(resource=RECURRINGS, billomat_id=recurring_id)

    def create_recurring(self, recurring_dict):
        """
        Creates a recurring

        :param recurring_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=RECURRINGS, send_data=recurring_dict)

    def update_recurring(self, recurring_id, recurring_dict):
        """
        Updates a recurring

        :param recurring_id: the recurring id
        :param recurring_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=RECURRINGS, billomat_id=recurring_id, send_data=recurring_dict)

    def delete_recurring(self, recurring_id):
        """
        Deletes a recurring

        :param recurring_id: the recurring id
        :return: dict
        """
        return self._create_delete_request(resource=RECURRINGS, billomat_id=recurring_id)

    """
    --------
    Billomat Recurring Item
    --------
    http://www.billomat.com/en/api/recurrings/items
    """

    def get_items_of_recurring_per_page(self, recurring_id, per_page=1000, page=1):
        """
        Get items of recurring per page

        :param recurring_id: the recurring id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=RECURRING_ITEMS,
            per_page=per_page,
            page=page,
            params={'recurring_id': recurring_id},
        )

    def get_all_items_of_recurring(self, recurring_id):
        """
        Get all items of recurring
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param recurring_id: the recurring id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_recurring_per_page,
            resource=RECURRING_ITEMS,
            **{'recurring_id': recurring_id}
        )

    def get_recurring_item(self, recurring_item_id):
        """
        Get a specific recurring item

        :param recurring_item_id: The specific recurring item id
        :return: dict
        """
        return self._create_get_request(RECURRING_ITEMS, recurring_item_id)

    def create_recurring_item(self, recurring_item_dict):
        """
        Creates a recurring item

        :param recurring_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=RECURRING_ITEMS, send_data=recurring_item_dict)

    def update_recurring_item(self, recurring_item_id, recurring_item_dict):
        """
        Updates a recurring item

        :param recurring_item_id: the recurring item id
        :param recurring_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=RECURRING_ITEMS,
            billomat_id=recurring_item_id,
            send_data=recurring_item_dict
        )

    def delete_recurring_item(self, recurring_item_id):
        """
        Deletes a recurring item

        :param recurring_item_id: the recurring item id
        :return: dict
        """
        return self._create_delete_request(resource=RECURRING_ITEMS, billomat_id=recurring_item_id)

    """
    --------
    Billomat Recurring Tags
    --------
    http://www.billomat.com/en/api/recurrings/tags
    """
    def get_tags_of_recurring_per_page(self, recurring_id, per_page=1000, page=1):
        """
        Get tags of recurring per page

        :param recurring_id: the recurring id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=RECURRING_TAGS,
            per_page=per_page,
            page=page,
            params={'recurring_id': recurring_id},
        )

    def get_all_tags_of_recurring(self, recurring_id):
        """
        Get all tags of recurring
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param recurring_id: the recurring id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_recurring_per_page,
            resource=RECURRING_TAGS,
            **{'recurring_id': recurring_id}
        )

    def get_recurring_tag(self, recurring_tag_id):
        """
        Get a specific recurring tag

        :param recurring_tag_id: The specific recurring tag id
        :return: dict
        """
        return self._create_get_request(resource=RECURRING_TAGS, billomat_id=recurring_tag_id)

    def create_recurring_tag(self, recurring_tag_dict):
        """
        Creates a recurring tag

        :param recurring_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=RECURRING_TAGS, send_data=recurring_tag_dict)

    def delete_recurring_tag(self, recurring_tag_id):
        """
        Deletes a recurring

        :param recurring_tag_id: the recurring tag id
        :return: dict
        """
        return self._create_delete_request(resource=RECURRING_TAGS, billomat_id=recurring_tag_id)

    """
    --------
    Billomat Recurring Email Receiver
    --------
    http://www.billomat.com/en/api/recurrings/receivers
    """
    def get_email_receivers_of_recurring_per_page(self, recurring_id, per_page=1000, page=1):
        """
        Get email receivers of recurring per page

        :param recurring_id: the recurring id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=RECURRING_EMAIL_RECEIVERS,
            per_page=per_page,
            page=page,
            params={'recurring_id': recurring_id},
        )

    def get_all_email_receivers_of_recurring(self, recurring_id):
        """
        Get all email receivers of recurring
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param recurring_id: the recurring id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_email_receivers_of_recurring_per_page,
            resource=RECURRING_EMAIL_RECEIVERS,
            **{'recurring_id': recurring_id}
        )

    def get_recurring_email_receiver(self, recurring_email_receiver_id):
        """
        Get a specific recurring email receiver

        :param recurring_email_receiver_id: The specific recurring email receiver id
        :return: dict
        """
        return self._create_get_request(resource=RECURRING_EMAIL_RECEIVERS, billomat_id=recurring_email_receiver_id)

    def create_recurring_email_receiver(self, recurring_email_receiver_dict):
        """
        Creates a recurring emai receiver

        :param recurring_email_receiver_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=RECURRING_EMAIL_RECEIVERS, send_data=recurring_email_receiver_dict)

    def delete_recurring_email_receiver(self, recurring_email_receiver_id):
        """
        Creates a recurring email receiver

        :param recurring_email_receiver_id: the recurring email receiver id
        :return: dict
        """
        return self._create_delete_request(resource=RECURRING_EMAIL_RECEIVERS, billomat_id=recurring_email_receiver_id)

    """
    --------
    Billomat Incoming
    --------
    http://www.billomat.com/en/api/incomings
    """

    def get_incomings_per_page(self, per_page=1000, page=1, params=None):
        """
        Get incomings per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=INCOMINGS, per_page=per_page, page=page, params=params)

    def get_all_incomings(self, params=None):
        """
        Get all incomings
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_incomings_per_page, resource=INCOMINGS, **{'params': params})

    def get_incoming(self, incoming_id):
        """
        Get a specific incoming

        :param incoming_id: The specific incoming id
        :return: dict
        """
        return self._create_get_request(resource=INCOMINGS, billomat_id=incoming_id)

    def create_incoming(self, incoming_dict):
        """
        Creates an incoming

        :param incoming_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INCOMINGS, send_data=incoming_dict)

    def update_incoming(self, incoming_id, incoming_dict):
        """
        Updates an incoming

        :param incoming_id: the incoming id
        :param incoming_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=INCOMINGS, billomat_id=incoming_id, send_data=incoming_dict)

    def delete_incoming(self, incoming_id):
        """
        Deletes an incoming

        :param incoming_id: the incoming id
        :return: dict
        """
        return self._create_delete_request(resource=INCOMINGS, billomat_id=incoming_id)

    """
    --------
    Billomat Incoming Comment
    --------
    http://www.billomat.com/en/api/incomings/comments
    """

    def get_comments_of_incoming_per_page(self, incoming_id, per_page=1000, page=1):
        """
        Get comments of incoming per page

        :param incoming_id: the incoming id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INCOMING_COMMENTS,
            per_page=per_page,
            page=page,
            params={'incoming_id': incoming_id},
        )

    def get_all_comments_of_incoming(self, incoming_id):
        """
        Get all comments of incoming
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param incoming_id: the incoming id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_incoming_per_page,
            resource=INCOMING_COMMENTS,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_comment(self, incoming_comment_id):
        """
        Get a incoming comment

        :param incoming_comment_id: The specific incoming comment id
        :return: dict
        """
        return self._create_get_request(INCOMING_COMMENTS, incoming_comment_id)

    def create_incoming_comment(self, incoming_comment_dict):
        """
        Creates an incoming comment

        :param incoming_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INCOMING_COMMENTS, send_data=incoming_comment_dict)

    def delete_incoming_comment(self, incoming_comment_id):
        """
        Deletes an incoming comment

        :param incoming_comment_id: the incoming comment id
        :return: Response
        """
        return self._create_delete_request(resource=INCOMING_COMMENTS, billomat_id=incoming_comment_id)

    """
    --------
    Billomat Incoming Payment
    --------
    http://www.billomat.com/en/api/incomings/payments
    """

    def get_payments_of_incoming_per_page(self, incoming_id, per_page=1000, page=1):
        """
        Get payments of incoming per page

        :param incoming_id: the incoming id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INCOMING_PAYMENTS,
            per_page=per_page,
            page=page,
            params={'incoming_id': incoming_id},
        )

    def get_all_payments_of_incoming(self, incoming_id):
        """
        Get all payments of incoming
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param incoming_id: the incoming id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_payments_of_incoming_per_page,
            resource=INCOMING_PAYMENTS,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_payment(self, incoming_payment_id):
        """
        Get a specific incoming payment

        :param incoming_payment_id: The specific incoming payment id
        :return: dict
        """
        return self._create_get_request(INCOMING_PAYMENTS, incoming_payment_id)

    def create_incoming_payment(self, incoming_payment_dict):
        """
        Creates an incoming payment

        :param incoming_payment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INCOMING_PAYMENTS, send_data=incoming_payment_dict)

    def delete_incoming_payment(self, incoming_payment_id):
        """
        Deletes an incoming payment

        :param incoming_payment_id: the incoment payment id
        :return: Response
        """
        return self._create_delete_request(resource=INCOMING_PAYMENTS, billomat_id=incoming_payment_id)

    """
    --------
    Billomat Incoming Properties
    --------
    http://www.billomat.com/en/api/incoming/properties
    """

    def get_incoming_properties_per_page(self, per_page=1000, page=1, params=None):
        """
        Get incoming properties per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=INCOMING_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_incoming_properties(self, params=None):
        """
        Get all incoming properties
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_incoming_properties_per_page,
            resource=INCOMING_PROPERTIES,
            **{'params': params}
        )

    def get_incoming_property(self, incoming_property_id):
        """
        Get a specific incoming property

        :param incoming_property_id: The specific incoming property id
        :return: dict
        """
        return self._create_get_request(resource=INCOMING_PROPERTIES, billomat_id=incoming_property_id)

    def create_incoming_property(self, incoming_property_dict):
        """
        Creates an incoming property

        :param incoming_property_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INCOMING_PROPERTIES, send_data=incoming_property_dict)

    """
    --------
    Billomat Incoming Tags
    --------
    http://www.billomat.com/en/api/incomings/tags
    """
    def get_tags_of_incoming_per_page(self, incoming_id, per_page=1000, page=1):
        """
        Get tags of incoming per page

        :param incoming_id: the incoming id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INCOMING_TAGS,
            per_page=per_page,
            page=page,
            params={'incoming_id': incoming_id},
        )

    def get_all_tags_of_incoming(self, incoming_id):
        """
        Get all tags of incoming
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param incoming_id: the incoming id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_incoming_per_page,
            resource=INCOMING_TAGS,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_tag(self, incoming_tag_id):
        """
        Get a specific incoming tag

        :param incoming_tag_id: The specific incoming tag id
        :return: dict
        """
        return self._create_get_request(resource=INCOMING_TAGS, billomat_id=incoming_tag_id)

    def create_incoming_tag(self, incoming_tag_dict):
        """
        Creates an incoming tag

        :param incoming_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INCOMING_TAGS, send_data=incoming_tag_dict)

    def delete_incoming_tag(self, incoming_tag_id):
        """
        Deletes an incoming tag

        :param incoming_tag_id: the incoming tag id
        :return: dict
        """
        return self._create_delete_request(resource=INCOMING_TAGS, billomat_id=incoming_tag_id)

    """
    --------
    Billomat Inbox Documents
    --------
    http://www.billomat.com/en/api/incomings/inbox
    """
    def get_inbox_documents_per_page(self, per_page=1000, page=1):
        """
        Get inbox documents per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=INBOX_DOCUMENTS,
            per_page=per_page,
            page=page,
        )

    def get_all_inbox_documents(self):
        """
        Get all inbox documents
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_inbox_documents_per_page,
            resource=INBOX_DOCUMENTS,
        )

    def get_inbox_document(self, inbox_document_id):
        """
        Get a specific inbox document

        :param inbox_document_id: The specific inbox document id
        :return: dict
        """
        return self._create_get_request(resource=INBOX_DOCUMENTS, billomat_id=inbox_document_id)

    def create_inbox_document(self, inbox_document_dict):
        """
        Creates an inbox document

        :param inbox_document_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=INBOX_DOCUMENTS, send_data=inbox_document_dict)

    def delete_inbox_document(self, inbox_document_id):
        """
        Deletes an inbox document

        :param inbox_document_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=INBOX_DOCUMENTS, billomat_id=inbox_document_id)

    """
    --------
    Billomat Offer
    --------
    http://www.billomat.com/en/api/estimates
    """

    def get_offers_per_page(self, per_page=1000, page=1, params=None):
        """
        Get offers per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=OFFERS, per_page=per_page, page=page, params=params)

    def get_all_offers(self, params=None):
        """
        Get all offers
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_offers_per_page, resource=OFFERS, **{'params': params})

    def get_offer(self, offer_id):
        """
        Get a specific offer

        :param offer_id: The specific offer id
        :return: dict
        """
        return self._create_get_request(resource=OFFERS, billomat_id=offer_id)

    def create_offer(self, offer_dict):
        """
        Creates an offer

        :param offer_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=OFFERS, send_data=offer_dict)

    def update_offer(self, offer_id, offer_dict):
        """
        Updates an offer

        :param offer_id: the offer id
        :param offer_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=OFFERS, billomat_id=offer_id, send_data=offer_dict)

    def delete_offer(self, offer_id):
        """
        Deletes an offer

        :param offer_id: the offer id
        :return: dict
        """
        return self._create_delete_request(resource=OFFERS, billomat_id=offer_id)

    def complete_offer(self, offer_id, complete_dict):
        """
        Completes an offer

        :param complete_dict: the complete dict with the template id
        :param offer_id: the offer id
        :return: Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=COMPLETE,
            send_data=complete_dict
        )

    def offer_pdf(self, offer_id):
        """
        Opens a pdf of an offer

        :param offer_id: the offer id
        :return: dict
        """
        return self._create_get_request(resource=OFFERS, billomat_id=offer_id, command=PDF)

    def send_offer_email(self, offer_id, email_dict):
        """
        Sends an offer by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param offer_id: the invoice id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=OFFERS,
            billomat_id=offer_id,
            send_data=email_dict,
            command=EMAIL,
        )

    def cancel_offer(self, offer_id):
        """
        Cancelles an offer

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=CANCEL,
        )

    def uncancel_offer(self, offer_id):
        """
        Uncancelles an invoice

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=UNCANCEL,
        )

    def mark_offer_as_win(self, offer_id):
        """
        Mark offer as win

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=WIN,
        )

    def mark_offer_as_lose(self, offer_id):
        """
        Mark offer as lose

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=LOSE,
        )

    def mark_offer_as_clear(self, offer_id):
        """
        Mark offer as clear

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=CLEAR,
        )

    def mark_offer_as_unclear(self, offer_id):
        """
        Mark offer as unclear

        :param offer_id: the offer id
        :return Response
        """
        return self._create_put_request(
            resource=OFFERS,
            billomat_id=offer_id,
            command=UNCLEAR,
        )

    """
    --------
    Billomat Offer Item
    --------
    http://www.billomat.com/en/api/estimates/items
    """

    def get_items_of_offer_per_page(self, offer_id, per_page=1000, page=1):
        """
        Get items of offer per page

        :param offer_id: the offer id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=OFFER_ITEMS,
            per_page=per_page,
            page=page,
            params={'offer_id': offer_id},
        )

    def get_all_items_of_offer(self, offer_id):
        """
        Get all items of offer
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param offer_id: the offer id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_offer_per_page,
            resource=OFFER_ITEMS,
            **{'offer_id': offer_id}
        )

    def get_offer_item(self, offer_item_id):
        """
        Get a specific offer item

        :param offer_item_id: The specific offer item id
        :return: dict
        """
        return self._create_get_request(OFFER_ITEMS, offer_item_id)

    def create_offer_item(self, offer_item_dict):
        """
        Creates an offer item

        :param offer_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=OFFER_ITEMS, send_data=offer_item_dict)

    def update_offer_item(self, offer_item_id, offer_item_dict):
        """
        Updates an offer item

        :param offer_item_id: offer item id
        :param offer_item_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=OFFER_ITEMS, billomat_id=offer_item_id, send_data=offer_item_dict)

    def delete_offer_item(self, offer_item_id):
        """
        Deletes an offer item

        :param offer_item_id: the offer item id
        :return: Response
        """
        return self._create_delete_request(resource=OFFER_ITEMS, billomat_id=offer_item_id)

    """
    --------
    Billomat Offer Comments
    --------
    http://www.billomat.com/en/api/estimates/comments
    """

    def get_comments_of_offer_per_page(self, offer_id, per_page=1000, page=1):
        """
        Get comments of offer per page

        :param offer_id: the offer id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=OFFER_COMMENTS,
            per_page=per_page,
            page=page,
            params={'offer_id': offer_id},
        )

    def get_all_comments_of_offer(self, offer_id):
        """
        Get all comments of offer
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param offer_id: the offer id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_offer_per_page,
            resource=OFFER_COMMENTS,
            **{'offer_id': offer_id}
        )

    def get_offer_comment(self, offer_comment_id):
        """
        Get a specific offer comment

        :param offer_comment_id: The specific offer comment id
        :return: dict
        """
        return self._create_get_request(OFFER_COMMENTS, offer_comment_id)

    def create_offer_comment(self, offer_comment_dict):
        """
        Creates an offer comment

        :param offer_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=OFFER_COMMENTS, send_data=offer_comment_dict)

    def update_offer_comment(self, offer_comment_id, offer_comment_dict):
        """
        Updates an offer comment

        :param offer_comment_id: the offer comment id
        :param offer_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=OFFER_COMMENTS,
            billomat_id=offer_comment_id,
            send_data=offer_comment_dict
        )

    def delete_offer_comment(self, offer_comment_id):
        """
        Deletes an offer comment

        :param offer_comment_id: the offer comment id
        :return: Response
        """
        return self._create_delete_request(resource=OFFER_COMMENTS, billomat_id=offer_comment_id)

    """
    --------
    Billomat Offer Tags
    --------
    http://www.billomat.com/en/api/estimates/tags
    """
    def get_tags_of_offer_per_page(self, offer_id, per_page=1000, page=1):
        """
        Get tags of offer per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param offer_id: the offer id
        :return: list
        """
        return self._get_resource_per_page(
            resource=OFFER_TAGS,
            per_page=per_page,
            page=page,
            params={'offer_id': offer_id},
        )

    def get_all_tags_of_offer(self, offer_id):
        """
        Get all tags of offer
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param offer_id: the offer id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_offer_per_page,
            resource=OFFER_TAGS,
            **{'offer_id': offer_id}
        )

    def get_offer_tag(self, offer_tag_id):
        """
        Get a specific offer tag

        :param offer_tag_id: The specific offer tag id
        :return: dict
        """
        return self._create_get_request(resource=OFFER_TAGS, billomat_id=offer_tag_id)

    def create_offer_tag(self, offer_tag_dict):
        """
        Creates an offer tag

        :param offer_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=OFFER_TAGS, send_data=offer_tag_dict)

    def delete_offer_tag(self, offer_tag_id):
        """
        Deletes an offer

        :param offer_tag_id: the offer tag id
        :return: Response
        """
        return self._create_delete_request(resource=OFFER_TAGS, billomat_id=offer_tag_id)

    """
    --------
    Billomat Credit Note
    --------
    http://www.billomat.com/en/api/credit-notes
    """

    def get_credit_notes_per_page(self, per_page=1000, page=1, params=None):
        """
        Get credit notes per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=CREDIT_NOTES, per_page=per_page, page=page, params=params)

    def get_all_credit_notes(self, params=None):
        """
        Get all credit notes
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_credit_notes_per_page, resource=CREDIT_NOTES, **{'params': params})

    def get_credit_note(self, credit_note_id):
        """
        Get a specific credit note

        :param credit_note_id: The specific credit note id
        :return: dict
        """
        return self._create_get_request(resource=CREDIT_NOTES, billomat_id=credit_note_id)

    def create_credit_note(self, credit_note_dict):
        """
        Creates a credit note

        :param credit_note_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CREDIT_NOTES, send_data=credit_note_dict)

    def update_credit_note(self, credit_note_id, credit_note_dict):
        """
        Updates a credit note

        :param credit_note_id: the credit note id
        :param credit_note_dict: dict
        :return: dict
        """
        return self._create_put_request(resource=CREDIT_NOTES, billomat_id=credit_note_id, send_data=credit_note_dict)

    def delete_credit_note(self, credit_note_id):
        """
        Deletes a credit note

        :param credit_note_id: the credit note id
        :return: Response
        """
        return self._create_delete_request(resource=CREDIT_NOTES, billomat_id=credit_note_id)

    def complete_credit_note(self, credit_note_it, complete_dict):
        """
        Completes an credit note

        :param complete_dict: the complete dict with the template id
        :param credit_note_it: the credit note id
        :return: Response
        """
        return self._create_put_request(
            resource=CREDIT_NOTES,
            billomat_id=credit_note_it,
            command=COMPLETE,
            send_data=complete_dict
        )

    def credit_note_pdf(self, credit_note_it):
        """
        Opens a pdf of a credit note

        :param credit_note_it: the credit note id
        :return: dict
        """
        return self._create_get_request(resource=CREDIT_NOTES, billomat_id=credit_note_it, command=PDF)

    def upload_credit_note_signature(self, credit_note_it, signature_dict):
        """
        Uploads a signature for the credit note

        :param signature_dict: the signature
        :type signature_dict: dict
        :param credit_note_it: the credit note id
        :return Response
        """
        return self._create_put_request(
            resource=CREDIT_NOTES,
            billomat_id=credit_note_it,
            send_data=signature_dict,
            command=UPLOAD_SIGNATURE
        )

    def send_credit_note_email(self, credit_note_it, email_dict):
        """
        Sends an credit note by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param credit_note_it: the credit note id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=CREDIT_NOTES,
            billomat_id=credit_note_it,
            send_data=email_dict,
            command=EMAIL,
        )

    """
    --------
    Billomat Credit Note Item
    --------
    http://www.billomat.com/en/api/credit-notes/items
    """

    def get_items_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1):
        """
        Get items of credit note per page

        :param credit_note_id: the credit note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CREDIT_NOTE_ITEMS,
            per_page=per_page,
            page=page,
            params={'credit_note_id': credit_note_id},
        )

    def get_all_items_of_credit_note(self, credit_note_id):
        """
        Get all items of credit note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param credit_note_id: the credit note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_credit_note_per_page,
            resource=CREDIT_NOTE_ITEMS,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_item(self, credit_note_item_id):
        """
        Get a specific credit note item

        :param credit_note_item_id: The specific credit note item id
        :return: dict
        """
        return self._create_get_request(CREDIT_NOTE_ITEMS, credit_note_item_id)

    def create_credit_note_item(self, credit_note_item_dict):
        """
        Creates a credit note item

        :param credit_note_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CREDIT_NOTE_ITEMS, send_data=credit_note_item_dict)

    def update_credit_note_item(self, credit_note_item_id, credit_note_item_dict):
        """
        Updates a credit note item

        :param credit_note_item_id: the credit note item id
        :param credit_note_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CREDIT_NOTE_ITEMS,
            billomat_id=credit_note_item_id,
            send_data=credit_note_item_dict
        )

    def delete_credit_note_item(self, credit_note_item_id):
        return self._create_delete_request(resource=CREDIT_NOTE_ITEMS, billomat_id=credit_note_item_id)

    """
    --------
    Billomat Credit Note Comments
    --------
    http://www.billomat.com/en/api/credit-notes/comments
    """

    def get_comments_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1):
        """
        Get comments of credit note per page

        :param credit_note_id: the credit note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CREDIT_NOTE_COMMENTS,
            per_page=per_page,
            page=page,
            params={'credit_note_id': credit_note_id},
        )

    def get_all_comments_of_credit_note(self, credit_note_id):
        """
        Get all comments of credit note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param credit_note_id: the credit note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_credit_note_per_page,
            resource=CREDIT_NOTE_COMMENTS,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_comment(self, credit_note_comment_id):
        """
        Get a specific credit note comment

        :param credit_note_comment_id: The specific credit note comment id
        :return: dict
        """
        return self._create_get_request(CREDIT_NOTE_COMMENTS, credit_note_comment_id)

    def create_credit_note_comment(self, credit_note_comment_dict):
        """
        Creates a credit note comment

        :param credit_note_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CREDIT_NOTE_COMMENTS, send_data=credit_note_comment_dict)

    def update_credit_note_comment(self, credit_note_comment_id, credit_note_comment_dict):
        """
        Updates a credit note comment

        :param credit_note_comment_id: the credit note comment id
        :param credit_note_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CREDIT_NOTE_COMMENTS,
            billomat_id=credit_note_comment_id,
            send_data=credit_note_comment_dict
        )

    def delete_credit_note_comment(self, credit_note_comment_id):
        """
        Deletes a credit note comment

        :param credit_note_comment_id: the credit note comment id
        :return: Response
        """
        return self._create_delete_request(resource=CREDIT_NOTE_COMMENTS, billomat_id=credit_note_comment_id)

    """
    --------
    Billomat Credit Note Payment
    --------
    http://www.billomat.com/en/api/credit-notes/payments
    """

    def get_payments_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1):
        """
        Get payments of credit note per page

        :param credit_note_id: the credit note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CREDIT_NOTE_PAYMENTS,
            per_page=per_page,
            page=page,
            params={'credit_note_id': credit_note_id},
        )

    def get_all_payments_of_credit_note(self, credit_note_id):
        """
        Get all payments of credit note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param credit_note_id: the credit note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_payments_of_credit_note_per_page,
            resource=CREDIT_NOTE_PAYMENTS,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_payment(self, credit_note_payment_id):
        """
        Get a specific credit note payment

        :param credit_note_payment_id: The specific credit note payment id
        :return: dict
        """
        return self._create_get_request(CREDIT_NOTE_PAYMENTS, credit_note_payment_id)

    def create_credit_note_payment(self, credit_note_payment_dict):
        """
        Creates a credit note payment

        :param credit_note_payment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CREDIT_NOTE_PAYMENTS, send_data=credit_note_payment_dict)

    def delete_credit_note_payment(self, credit_note_payment_id):
        """
        Deletes a credit note payment

        :param credit_note_payment_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=CREDIT_NOTE_PAYMENTS, billomat_id=credit_note_payment_id)

    """
    --------
    Billomat Credit Note Tags
    --------
    http://www.billomat.com/en/api/credit-notes/tags
    """
    def get_tags_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1):
        """
        Get tags of credit note per page

        :param credit_note_id: the credit note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CREDIT_NOTE_TAGS,
            per_page=per_page,
            page=page,
            params={'credit_note_id': credit_note_id},
        )

    def get_all_tags_of_credit_note(self, credit_note_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_credit_note_per_page,
            resource=CREDIT_NOTE_TAGS,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_tag(self, credit_note_tag_id):
        """
        Get a specific credit note tag

        :param credit_note_tag_id: The specific credit note tag id
        :return: dict
        """
        return self._create_get_request(resource=CREDIT_NOTE_TAGS, billomat_id=credit_note_tag_id)

    def create_credit_note_tag(self, credit_note_tag_dict):
        """
        Creates a credit note tag

        :param credit_note_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CREDIT_NOTE_TAGS, send_data=credit_note_tag_dict)

    def delete_credit_note_tag(self, credit_note_tag_id):
        """
        Deletes a credit note tag

        :param credit_note_tag_id: the credit note tag id
        :return: Response
        """
        return self._create_delete_request(resource=CREDIT_NOTE_TAGS, billomat_id=credit_note_tag_id)

    """
    --------
    Billomat Confirmation
    --------
    http://www.billomat.com/en/api/credit-notes
    """

    def get_confirmations_per_page(self, per_page=1000, page=1, params=None):
        """
        Get confirmations per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=CONFIRMATIONS, per_page=per_page, page=page, params=params)

    def get_all_confirmations(self, params=None):
        """
        Get all confirmations
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_confirmations_per_page,
            resource=CONFIRMATIONS,
            **{'params': params}
        )

    def get_confirmation(self, confirmation_id):
        """
        Get a specific confirmation

        :param confirmation_id: The specific confirmation id
        :return: dict
        """
        return self._create_get_request(resource=CONFIRMATIONS, billomat_id=confirmation_id)

    def create_confirmation(self, confirmation_dict):
        """
        Creates a confirmation

        :param confirmation_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CONFIRMATIONS, send_data=confirmation_dict)

    def update_confirmation(self, confirmation_id, confirmation_dict):
        """
        Updates a confirmation

        :param confirmation_id: the confirmation id
        :param confirmation_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            send_data=confirmation_dict
        )

    def delete_confirmation(self, confirmation_id):
        """
        Deletes a confirmation

        :param confirmation_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=CONFIRMATIONS, billomat_id=confirmation_id)

    def complete_confirmation(self, confirmation_id, complete_dict):
        """
        Completes an confirmation

        :param complete_dict: the complete dict with the template id
        :param confirmation_id: the confirmation id
        :return: Response
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            command=COMPLETE,
            send_data=complete_dict
        )

    def confirmation_pdf(self, confirmation_id):
        """
        Opens a pdf of a confirmation

        :param confirmation_id: the confirmation id
        :return: dict
        """
        return self._create_get_request(resource=CONFIRMATIONS, billomat_id=confirmation_id, command=PDF)

    def send_confirmation_email(self, confirmation_id, email_dict):
        """
        Sends an confirmation by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param confirmation_id: the confirmation id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            send_data=email_dict,
            command=EMAIL,
        )

    def cancel_confirmation(self, confirmation_id):
        """
        Cancelles an confirmation

        :param confirmation_id: the confirmation id
        :return Response
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            command=CANCEL,
        )

    def uncancel_confirmation(self, confirmation_id):
        """
        Uncancelles an confirmation

        :param confirmation_id: the confirmation id
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            command=UNCANCEL,
        )

    def mark_confirmation_as_clear(self, confirmation_id):
        """
        Mark confirmation as clear

        :param confirmation_id: the confirmation id
        :return Response
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            command=CLEAR,
        )

    def mark_confirmation_as_unclear(self, confirmation_id):
        """
        Mark confirmation as unclear

        :param confirmation_id: the confirmation id
        :return Response
        """
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            command=UNCLEAR,
        )

    """
    --------
    Billomat Confirmation Item
    --------
    http://www.billomat.com/en/api/confirmations/items
    """

    def get_items_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1):
        """
        Get items of confirmation per page

        :param confirmation_id: the confirmation id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CONFIRMATION_ITEMS,
            per_page=per_page,
            page=page,
            params={'confirmation_id': confirmation_id},
        )

    def get_all_items_of_confirmation(self, confirmation_id):
        """
        Get all items of confirmation
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param confirmation_id: the confirmation id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_confirmation_per_page,
            resource=CONFIRMATION_ITEMS,
            **{'confirmation_id': confirmation_id}
        )

    def get_confirmation_item(self, confirmation_item_id):
        """
        Get a specific confirmation item

        :param confirmation_item_id: The specific confirmation item id
        :return: dict
        """
        return self._create_get_request(CONFIRMATION_ITEMS, confirmation_item_id)

    def create_confirmation_item(self, confirmation_item_dict):
        """
        Creates a confirmation item

        :param confirmation_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CONFIRMATION_ITEMS, send_data=confirmation_item_dict)

    def update_confirmation_item(self, confirmation_item_id, confirmation_item_dict):
        """
        Updates a confirmation item

        :param confirmation_item_id: the confirmation item id
        :param confirmation_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CONFIRMATION_ITEMS,
            billomat_id=confirmation_item_id,
            send_data=confirmation_item_dict
        )

    def delete_confirmation_item(self, confirmation_item_id):
        """
        Deletes a confirmation item

        :param confirmation_item_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=CONFIRMATION_ITEMS, billomat_id=confirmation_item_id)

    """
    --------
    Billomat Confirmation Comments
    --------
    http://www.billomat.com/en/api/confirmation/comments
    """

    def get_comments_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1):
        """
        Get comments of confirmation per page

        :param confirmation_id: the confirmation id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CONFIRMATION_COMMENTS,
            per_page=per_page,
            page=page,
            params={'confirmation_id': confirmation_id},
        )

    def get_all_comments_of_confirmation(self, confirmation_id):
        """
        Get all comments of confirmation
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param confirmation_id: the confirmation id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_confirmation_per_page,
            resource=CONFIRMATION_COMMENTS,
            **{'confirmation_id': confirmation_id}
        )

    def get_confirmation_comment(self, confirmation_comment_id):
        """
        Get a specific confirmation comment

        :param confirmation_comment_id: The specific confirmation comment id
        :return: dict
        """
        return self._create_get_request(CONFIRMATION_COMMENTS, confirmation_comment_id)

    def create_confirmation_comment(self, confirmation_comment_dict):
        """
        Creates a confirmation comment

        :param confirmation_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CONFIRMATION_COMMENTS, send_data=confirmation_comment_dict)

    def update_confirmation_comment(self, confirmation_comment_id, confirmation_comment_dict):
        """
        Updates a confirmation comment

        :param confirmation_comment_id: the confirmation comment id
        :param confirmation_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=CONFIRMATION_COMMENTS,
            billomat_id=confirmation_comment_id,
            send_data=confirmation_comment_dict
        )

    def delete_confirmation_comment(self, confirmation_comment_id):
        """
        Deletes a confirmation comment

        :param confirmation_comment_id: dict
        :return: dict
        """
        return self._create_delete_request(resource=CONFIRMATION_COMMENTS, billomat_id=confirmation_comment_id)

    """
    --------
    Billomat Confirmation Tags
    --------
    http://www.billomat.com/en/api/confirmations/tags
    """
    def get_tags_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1):
        """
        Get tags of confirmation per page

        :param confirmation_id: the confirmation id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=CONFIRMATION_TAGS,
            per_page=per_page,
            page=page,
            params={'confirmation_id': confirmation_id},
        )

    def get_all_tags_of_confirmation(self, confirmation_id):
        """
        Get all tags of confirmation
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param confirmation_id: the confirmation id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_confirmation_per_page,
            resource=CONFIRMATION_TAGS,
            **{'confirmation_id': confirmation_id}
        )

    def get_confirmation_tag(self, confirmation_tag_id):
        """
        Get a specific confirmation tag

        :param confirmation_tag_id: The specific confirmation tag id
        :return: dict
        """
        return self._create_get_request(resource=CONFIRMATION_TAGS, billomat_id=confirmation_tag_id)

    def create_confirmation_tag(self, confirmation_tag_dict):
        """
        Creates a confirmation tag

        :param confirmation_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=CONFIRMATION_TAGS, send_data=confirmation_tag_dict)

    def delete_confirmation_tag(self, confirmation_tag_id):
        """
        Deletes a confirmation tag

        :param confirmation_tag_id: the confirmation tag id
        :return: Response
        """
        return self._create_delete_request(resource=CONFIRMATION_TAGS, billomat_id=confirmation_tag_id)

    """
    --------
    Billomat Reminder
    --------
    http://www.billomat.com/en/api/reminders
    """

    def get_reminders_per_page(self, per_page=1000, page=1, params=None):
        """
        Get reminders per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=REMINDERS, per_page=per_page, page=page, params=params)

    def get_all_reminders(self, params=None):
        """
        Get all reminders
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_reminders_per_page, resource=REMINDERS, **{'params': params})

    def get_reminder(self, reminder_id):
        """
        Get a specific reminder

        :param reminder_id: The specific reminder id
        :return: dict
        """
        return self._create_get_request(resource=REMINDERS, billomat_id=reminder_id)

    def create_reminder(self, reminder_dict):
        """
        Creates a reminder

        :param reminder_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=REMINDERS, send_data=reminder_dict)

    def update_reminder(self, reminder_id, reminder_dict):
        """
        Updates a reminder

        :param reminder_id: the reminder id
        :param reminder_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=REMINDERS,
            billomat_id=reminder_id,
            send_data=reminder_dict
        )

    def delete_reminder(self, reminder_id):
        """
        Deletes a reminder

        :param reminder_id: the reminder id
        :return: dict
        """
        return self._create_delete_request(resource=REMINDERS, billomat_id=reminder_id)

    def complete_reminder(self, reminder_id, complete_dict):
        """
        Completes a reminder

        :param complete_dict: the complete dict with the template id
        :param reminder_id: the reminder id
        :return: Response
        """
        return self._create_put_request(
            resource=REMINDERS,
            billomat_id=reminder_id,
            command=COMPLETE,
            send_data=complete_dict
        )

    def reminder_pdf(self, reminder_id):
        """
        Opens a pdf of a reminder

        :param reminder_id: the reminder id
        :return: dict
        """
        return self._create_get_request(resource=REMINDERS, billomat_id=reminder_id, command=PDF)

    def send_reminder_email(self, reminder_id, email_dict):
        """
        Sends an reminder by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param reminder_id: the reminder id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=REMINDERS,
            billomat_id=reminder_id,
            send_data=email_dict,
            command=EMAIL,
        )

    """
    --------
    Billomat Reminder Item
    --------
    http://www.billomat.com/en/api/reminders/items
    """

    def get_items_of_reminder_per_page(self, reminder_id, per_page=1000, page=1):
        """
        Get items of reminder per page

        :param reminder_id: the reminder id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=REMINDER_ITEMS,
            per_page=per_page,
            page=page,
            params={'reminder_id': reminder_id},
        )

    def get_all_items_of_reminder(self, reminder_id):
        """
        Get all items of reminder
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param reminder_id: the reminder id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_reminder_per_page,
            resource=REMINDER_ITEMS,
            **{'reminder_id': reminder_id}
        )

    def get_reminder_item(self, reminder_item_id):
        """
        Get a specific reminder item

        :param reminder_item_id: The specific reminder item id
        :return: dict
        """
        return self._create_get_request(REMINDER_ITEMS, reminder_item_id)

    def create_reminder_item(self, reminder_item_dict):
        """
        Creates a reminder item

        :param reminder_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=REMINDER_ITEMS, send_data=reminder_item_dict)

    def update_reminder_item(self, reminder_item_id, reminder_item_dict):
        """
        Updates a reminder item

        :param reminder_item_id: the reminder item id
        :param reminder_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=REMINDER_ITEMS,
            billomat_id=reminder_item_id,
            send_data=reminder_item_dict
        )

    def delete_reminder_item(self, reminder_item_id):
        """
        Deletes a reminder item

        :param reminder_item_id: the reminder item id
        :return: Response
        """
        return self._create_delete_request(resource=REMINDER_ITEMS, billomat_id=reminder_item_id)

    """
    --------
    Billomat Reminder Tags
    --------
    http://www.billomat.com/en/api/reminders/tags
    """
    def get_tags_of_reminder_per_page(self, reminder_id, per_page=1000, page=1):
        """
        Get tags of reminder per page

        :param reminder_id: the reminder id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=REMINDER_TAGS,
            per_page=per_page,
            page=page,
            params={'reminder_id': reminder_id},
        )

    def get_all_tags_of_reminder(self, reminder_id):
        """
        Get all tags of reminder
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param reminder_id: the reminder id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_reminder_per_page,
            resource=REMINDER_TAGS,
            **{'reminder_id': reminder_id}
        )

    def get_reminder_tag(self, reminder_tag_id):
        """
        Get a specific reminder tag

        :param reminder_tag_id: The specific reminder tag id
        :return: dict
        """
        return self._create_get_request(resource=REMINDER_TAGS, billomat_id=reminder_tag_id)

    def create_reminder_tag(self, reminder_tag_dict):
        """
        Creates a reminder tag

        :param reminder_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=REMINDER_TAGS, send_data=reminder_tag_dict)

    def delete_reminder_tag(self, reminder_tag_id):
        """
        Deletes a reminder tag

        :param reminder_tag_id: reminder tag id
        :return: Response
        """
        return self._create_delete_request(resource=REMINDER_TAGS, billomat_id=reminder_tag_id)

    """
    --------
    Billomat Delivery Notes
    --------
    http://www.billomat.com/en/api/delivery-notes
    """

    def get_delivery_notes_per_page(self, per_page=1000, page=1, params=None):
        """
        Get delivery notes per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=DELIVERY_NOTES, per_page=per_page, page=page, params=params)

    def get_all_delivery_notes(self, params=None):
        """
        Get all delivery notes
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_delivery_notes_per_page,
            resource=DELIVERY_NOTES,
            **{'params': params}
        )

    def get_delivery_note(self, delivery_note_id):
        """
        Get a specific delivery note

        :param delivery_note_id: The specific delivery note id
        :return: dict
        """
        return self._create_get_request(resource=DELIVERY_NOTES, billomat_id=delivery_note_id)

    def create_delivery_note(self, delivery_note_dict):
        """
        Creates a delivery note

        :param delivery_note_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=DELIVERY_NOTES, send_data=delivery_note_dict)

    def update_delivery_note(self, delivery_note_id, delivery_note_dict):
        """
        Updates a delivery note

        :param delivery_note_id: the delivery note id
        :param delivery_note_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=DELIVERY_NOTES,
            billomat_id=delivery_note_id,
            send_data=delivery_note_dict
        )

    def delete_delivery_note(self, delivery_note_id):
        """
        Deletes a delivery note

        :param delivery_note_id: the delivery note id
        :return: Response
        """
        return self._create_delete_request(resource=DELIVERY_NOTES, billomat_id=delivery_note_id)

    def complete_delivery_note(self, delivery_note_id, complete_dict):
        """
        Completes an delivery note

        :param complete_dict: the complete dict with the template id
        :param delivery_note_id: the delivery note id
        :return: Response
        """
        return self._create_put_request(
            resource=DELIVERY_NOTES,
            billomat_id=delivery_note_id,
            command=COMPLETE,
            send_data=complete_dict
        )

    def delivery_note_pdf(self, delivery_note_id):
        """
        Opens a pdf of a delivery note

        :param delivery_note_id: the delivery note id
        :return: dict
        """
        return self._create_get_request(resource=DELIVERY_NOTES, billomat_id=delivery_note_id, command=PDF)

    def send_delivery_note_email(self, delivery_note_id, email_dict):
        """
        Sends an delivery note by email
        If you want to send your email to more than one persons do:
        'recipients': {'to': ['bykof@me.com', 'mbykovski@seibert-media.net']}}

        :param delivery_note_id: the delivery note id
        :param email_dict: the email dict
        :return dict
        """
        return self._create_post_request(
            resource=DELIVERY_NOTES,
            billomat_id=delivery_note_id,
            send_data=email_dict,
            command=EMAIL,
        )

    """
    --------
    Billomat Delivery Note Item
    --------
    http://www.billomat.com/en/api/delivery-notes/items
    """

    def get_items_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1):
        """
        Get items of delivery note per page

        :param delivery_note_id: the delivery note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_ITEMS,
            per_page=per_page,
            page=page,
            params={'delivery_note_id': delivery_note_id},
        )

    def get_all_items_of_delivery_note(self, delivery_note_id):
        """
        Get all items of delivery note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param delivery_note_id: the delivery note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_items_of_delivery_note_per_page,
            resource=DELIVERY_NOTE_ITEMS,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_delivery_note_item(self, delivery_note_item_id):
        """
        Get a specific delivery note item

        :param delivery_note_item_id: The specific delivery note item id
        :return: dict
        """
        return self._create_get_request(REMINDER_ITEMS, delivery_note_item_id)

    def create_delivery_note_item(self, delivery_note_item_dict):
        """
        Creates a delivery note item

        :param delivery_note_item_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=DELIVERY_NOTE_ITEMS, send_data=delivery_note_item_dict)

    def update_delivery_note_item(self, delivery_note_item_id, delivery_note_item_dict):
        """
        Updates a delivery note item

        :param delivery_note_item_id: delivery note item id
        :param delivery_note_item_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=DELIVERY_NOTE_ITEMS,
            billomat_id=delivery_note_item_id,
            send_data=delivery_note_item_dict
        )

    def delete_delivery_note_item(self, delivery_note_item_id):
        """
        Deletes a delivery note item

        :param delivery_note_item_id: the delivery note item id
        :return: Response
        """
        return self._create_delete_request(resource=DELIVERY_NOTE_ITEMS, billomat_id=delivery_note_item_id)

    """
    --------
    Billomat Delivery Note Comments
    --------
    http://www.billomat.com/en/api/delivery-notes/comments
    """

    def get_comments_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1):
        """
        Get comments of delivery note per page

        :param delivery_note_id: the delivery note
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_COMMENTS,
            per_page=per_page,
            page=page,
            params={'delivery_note_id': delivery_note_id},
        )

    def get_all_comments_of_delivery_note(self, delivery_note_id):
        """
        Get all comments of delivery note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param delivery_note_id: the delivery note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_delivery_note_per_page,
            resource=DELIVERY_NOTE_COMMENTS,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_delivery_note_comment(self, delivery_note_comment_id):
        """
        Get a specific delivery note comment

        :param delivery_note_comment_id: The specific delivery note comment id
        :return: dict
        """
        return self._create_get_request(DELIVERY_NOTE_COMMENTS, delivery_note_comment_id)

    def create_delivery_note_comment(self, delivery_note_comment_dict):
        """
        Creates a delivery note comment

        :param delivery_note_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=DELIVERY_NOTE_COMMENTS, send_data=delivery_note_comment_dict)

    def update_delivery_note_comment(self, delivery_note_comment_id, delivery_note_comment_dict):
        """
        Updates a delivery note comment

        :param delivery_note_comment_id: the delivery note comment id
        :param delivery_note_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=DELIVERY_NOTE_COMMENTS,
            billomat_id=delivery_note_comment_id,
            send_data=delivery_note_comment_dict
        )

    def delete_delivery_note_comment(self, delivery_note_comment_id):
        """
        Deletes a delivery note comment

        :param delivery_note_comment_id: dict
        :return: Response
        """
        return self._create_delete_request(resource=DELIVERY_NOTE_COMMENTS, billomat_id=delivery_note_comment_id)

    """
    --------
    Billomat Delivery Note Tags
    --------
    http://www.billomat.com/en/api/delivery-notes/tags
    """
    def get_tags_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1):
        """
        Get tags of delivery note per page

        :param delivery_note_id: the delivery note id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_TAGS,
            per_page=per_page,
            page=page,
            params={'delivery_note_id': delivery_note_id},
        )

    def get_all_tags_of_delivery_note(self, delivery_note_id):
        """
        Get all tags of delivery note
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param delivery_note_id: the delivery note id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_delivery_note_per_page,
            resource=DELIVERY_NOTE_TAGS,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_delivery_note_tag(self, delivery_note_tag_id):
        """
        Get a specific delivery note tag

        :param delivery_note_tag_id: The specific delivery note tag id
        :return: dict
        """
        return self._create_get_request(resource=DELIVERY_NOTE_TAGS, billomat_id=delivery_note_tag_id)

    def create_delivery_note_tag(self, delivery_note_tag_dict):
        """
        Creates a delivery note tag

        :param delivery_note_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=DELIVERY_NOTE_TAGS, send_data=delivery_note_tag_dict)

    def delete_delivery_note_tag(self, delivery_note_tag_id):
        """
        Deletes a delivery note tag

        :param delivery_note_tag_id: the delivery note tag
        :return: Response
        """
        return self._create_delete_request(resource=DELIVERY_NOTE_TAGS, billomat_id=delivery_note_tag_id)

    """
    --------
    Billomat Letters
    --------
    http://www.billomat.com/en/api/letters
    """

    def get_letters_per_page(self, per_page=1000, page=1, params=None):
        """
        Get letters per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=LETTERS, per_page=per_page, page=page, params=params)

    def get_all_letters(self, params=None):
        """
        Get all letters
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_letters_per_page, resource=LETTERS, **{'params': params})

    def get_letter(self, letter_id):
        """
        Get a specific letter

        :param letter_id: The specific letter id
        :return: dict
        """
        return self._create_get_request(resource=LETTERS, billomat_id=letter_id)

    def create_letter(self, letter_dict):
        """
        Creates a letter

        :param letter_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=LETTERS, send_data=letter_dict)

    def update_letter(self, letter_id, letter_dict):
        """
        Updates a letter

        :param letter_id: the letter id
        :param letter_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=LETTERS,
            billomat_id=letter_id,
            send_data=letter_dict
        )

    def delete_letter(self, letter_id):
        """
        Deletes a letter

        :param letter_id: the letter id
        :return: Response
        """
        return self._create_delete_request(resource=LETTERS, billomat_id=letter_id)

    """
    --------
    Billomat Letter Comments
    --------
    http://www.billomat.com/en/api/letters/comments
    """

    def get_comments_of_letter_per_page(self, letter_id, per_page=1000, page=1):
        """
        Get comments of letter per page

        :param letter_id: the letter id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=LETTER_COMMENTS,
            per_page=per_page,
            page=page,
            params={'letter_id': letter_id},
        )

    def get_all_comments_of_letter(self, letter_id):
        """
        Get all comments of letter
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param letter_id: the letter id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_comments_of_letter_per_page,
            resource=LETTER_COMMENTS,
            **{'letter_id': letter_id}
        )

    def get_letter_comment(self, letter_comment_id):
        """
        Get a specific letter comment

        :param letter_comment_id: The specific letter comment id
        :return: dict
        """
        return self._create_get_request(LETTER_COMMENTS, letter_comment_id)

    def create_letter_comment(self, letter_comment_dict):
        """
        Creates a letter comment

        :param letter_comment_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=LETTER_COMMENTS, send_data=letter_comment_dict)

    def update_letter_comment(self, letter_comment_id, letter_comment_dict):
        """
        Updates a letter comment

        :param letter_comment_id: the letter command id
        :param letter_comment_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=LETTER_COMMENTS,
            billomat_id=letter_comment_id,
            send_data=letter_comment_dict
        )

    def delete_letter_comment(self, letter_comment_id):
        """
        Deletes a letter comment

        :param letter_comment_id: the letter comment id
        :return: Response
        """
        return self._create_delete_request(resource=LETTER_COMMENTS, billomat_id=letter_comment_id)

    """
    --------
    Billomat Letter Tags
    --------
    http://www.billomat.com/en/api/letters/tags
    """
    def get_tags_of_letter_per_page(self, letter_id, per_page=1000, page=1):
        """
        Get tags of letter per page

        :param letter_id: the letter id
        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :return: list
        """
        return self._get_resource_per_page(
            resource=LETTER_TAGS,
            per_page=per_page,
            page=page,
            params={'letter_id': letter_id},
        )

    def get_all_tags_of_letter(self, letter_id):
        """
        Get all tags of letter
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param letter_id: the letter id
        :return: list
        """
        return self._iterate_through_pages(
            get_function=self.get_tags_of_letter_per_page,
            resource=LETTER_TAGS,
            **{'letter_id': letter_id}
        )

    def get_letter_tag(self, letter_tag_id):
        """
        Get a specific letter tag

        :param letter_tag_id: The specific letter tag id
        :return: dict
        """
        return self._create_get_request(resource=LETTER_TAGS, billomat_id=letter_tag_id)

    def create_letter_tag(self, letter_tag_dict):
        """
        Creates a letter tag

        :param letter_tag_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=LETTER_TAGS, send_data=letter_tag_dict)

    def delete_letter_tag(self, letter_tag_id):
        """
        Deletes a letter tag

        :param letter_tag_id: the letter tag id
        :return: Response
        """
        return self._create_delete_request(resource=LETTER_TAGS, billomat_id=letter_tag_id)

    """
    --------
    Billomat Template
    --------
    http://www.billomat.com/en/api/templates
    """

    def get_templates_per_page(self, per_page=1000, page=1, params=None):
        """
        Get templates per page

        :param per_page: How many objects per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: list
        """
        return self._get_resource_per_page(resource=TEMPLATES, per_page=per_page, page=page, params=params)

    def get_all_templates(self, params=None):
        """
        Get all templates
        This will iterate over all pages until it gets all elements.
        So if the rate limit exceeded it will throw an Exception and you will get nothing

        :param params: search params
        :return: list
        """
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_templates_per_page, resource=TEMPLATES, **{'params': params})

    def get_template(self, template_id):
        """
        Get a specific template

        :param template_id: The specific template id
        :return: dict
        """
        return self._create_get_request(resource=TEMPLATES, billomat_id=template_id)

    def create_template(self, template_dict):
        """
        Creates a template

        :param template_dict: dict
        :return: dict
        """
        return self._create_post_request(resource=TEMPLATES, send_data=template_dict)

    def update_template(self, template_id, template_dict):
        """
        Updates a template

        :param template_id: the template id
        :param template_dict: dict
        :return: dict
        """
        return self._create_put_request(
            resource=TEMPLATES,
            billomat_id=template_id,
            send_data=template_dict
        )

    def delete_template(self, template_id):
        """
        Deletes a template

        :param template_id: the template id
        :return: Response
        """
        return self._create_delete_request(resource=TEMPLATES, billomat_id=template_id)
