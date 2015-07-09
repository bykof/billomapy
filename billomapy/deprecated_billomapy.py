import math
import json
import logging

import requests
from tornado import ioloop, httpclient

from .resources import *

logger = logging.getLogger(__name__)


class Billomapy(object):
    """
    Billomapy helps you to get data from billomat

    Info: The response object of this api will be dict

    Some important things for developer:
    Billomat API Docs: http://www.billomat.com/api
    """

    def __init__(self, billomat_id, api_key, app_id, app_secret):
        """
        :param billomat_id: Mostly the name of your company for example https://YOUR_COMPANY.billomat.net/api/
        :param api_key: The api key that you requested from billomat
        :param app_id: The app_id that you requested by billomat
        :param app_secret: The app_secret that you requested by billomat
        """
        self.billomat_id = billomat_id
        self.api_key = api_key
        self.app_id = app_id
        self.app_secret = app_secret

        self.billomat_header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-BillomatApiKey': self.api_key,
            'X-AppId': self.app_id,
            'X-AppSecret': self.app_secret,
        }

        self.api_url = "https://{}.billomat.net/api/".format(billomat_id)
        self.session = self._create_session()
        self.tornado_http_client = httpclient.AsyncHTTPClient()
        self.tornado_loops = 0
        self.tornado_current_resource = None
        self.tornado_current_data_key = None
        self.data_pot = []

    def _create_session(self):
        """
        Creates the billomat session and returns it
        """
        session = requests.Session()
        session.headers.update(self.billomat_header)
        return session

    def _create_get_request(self, resource, billomat_id='', params=None):
        """
        Creates a get request and return the response data
        """
        if not params:
            params = {}

        assert (isinstance(resource, basestring))
        if billomat_id:
            assert (isinstance(billomat_id, int) or isinstance(billomat_id, basestring))

            if isinstance(billomat_id, int):
                billomat_id = str(billomat_id)

        response = self.session.get(
            url=self.api_url + resource + ('/' + billomat_id if billomat_id else ''),
            params=params,
        )

        if response.status_code == requests.codes.ok:
            return response.json()[resource]
        else:
            logger.error('Error: ', response.content)
            response.raise_for_status()

    def _create_post_request(self, resource, send_data):
        """
        Creates a post request and return the response data
        """
        assert (isinstance(resource, basestring))
        response = self.session.post(
            url=self.api_url + resource,
            data=json.dumps(send_data),
        )

        if response.status_code == requests.codes.created:
            return response.json()
        else:
            logger.error('Error: ', response.content)
            response.raise_for_status()

    def _create_put_request(self, resource, billomat_id, send_data):
        """
        Creates a post request and return the response data
        """
        assert (isinstance(resource, basestring))

        if isinstance(billomat_id, int):
            billomat_id = str(billomat_id)

        response = self.session.post(
            url=self.api_url + resource + '/' + billomat_id,
            data=json.dumps(send_data),
        )

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logger.error('Error: ', response.content)
            response.raise_for_status()

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

        if response.status_code == requests.codes.ok:
            return response
        else:
            logger.error('Error: ', response.content)
            response.raise_for_status()

    def _collect_pot_items(self, response):
        if not response.body:
            response.body = []

        self.tornado_loops -= 1

        if self.tornado_loops == 0:
            ioloop.IOLoop.instance().stop()

        try:
            temp_data_pot = json.loads(response.body)[self.tornado_current_resource][self.tornado_current_data_key]

            if isinstance(temp_data_pot, dict):
                temp_data_pot = [temp_data_pot]

            self.data_pot += temp_data_pot
        except TypeError:
            logger.error(
                '{} was not JSON Serializable'.format(response)
            )

    def _create_flood_get_request(self, resource, data_key, params):
        """
        Creates a flood request of many links and sends them in one time
        """
        assert (isinstance(resource, basestring))
        assert (isinstance(params, list))
        self.data_pot = []
        self.tornado_current_resource = resource
        self.tornado_current_data_key = data_key
        for url in [
            self.api_url + resource + '?' + '&'.join(['{}={}'.format(key, value) for key, value in params_row.items()])
            for params_row in params
        ]:
            self.tornado_loops += 1
            self.tornado_http_client.fetch(
                request=httpclient.HTTPRequest(
                    url=url,
                    method='GET',
                    headers=self.billomat_header,
                    request_timeout=500,
                    connect_timeout=500,
                ),
                callback=self._collect_pot_items
            )
        ioloop.IOLoop.instance().start()
        return self.data_pot

    @staticmethod
    def _iterate_through_pages(get_function, data_key, params=None, **kwargs):
        """
        Iterate through all pages and return the collected data
        """
        if not params:
            params = {}

        assert(isinstance(data_key, basestring))
        request_data = True
        data = {data_key: []}
        page = 1

        while request_data:
            temp_response = get_function(page=page, params=params, **kwargs)
            if temp_response['@total'] != '0':
                data[data_key] += temp_response[data_key]

            if page == 1:
                for key, value in temp_response.items():
                    if key is not data_key:
                        data[key] = value

            page += 1

            if page > int(math.ceil(float(data['@total']) / float(data['@per_page']))):
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

    """
    --------
    Billomat Clients
    --------
    http://www.billomat.com/en/api/clients
    """

    def get_clients_per_page(self, per_page=1000, page=1, params=None):
        """
        Get clients per page
        :param per_page: How many clients per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: dict
        """
        return self._get_resource_per_page(resource=CLIENTS, per_page=per_page, page=page, params=params)

    def get_all_clients(self, params=None):
        """
        Get all clients
        :param params: Search parameters. Default: {
        :return: dict
        """
        return self._iterate_through_pages(self.get_clients_per_page, CLIENT, params=params)

    def get_client(self, client_id):
        """
        Get a specific client by the billomat client id
        :param client_id: The specific client id
        :return: dict
        """
        return self._create_get_request(resource=CLIENTS, billomat_id=client_id)

    def create_client(self, client_dict):
        """
        Creates a client
        :param client_dict: a dictionary with e.g.
        {
            'client': {
                'name': 'Company Name',
            }
        }
        :return: response dict of billomat
        """
        return self._create_post_request(CLIENTS, client_dict)

    def update_client(self, client_id, client_dict):
        """
        Updates a client with the given keys and values in the dict
        :param client_id: the client which you want to update
        :param client_dict: the key, value pairs (see doc)
        :return: response dict of billomat
        """
        return self._create_put_request(CLIENTS, client_id, client_dict)

    def delete_client(self, client_id):
        """
        Deletes a client
        :param client_id: the client billomat id
        :return: the response object
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
        Get client properties by a given page and per page number
        :param per_page: how many elements per page
        :param page: which page
        :param params: search params
        :return: dict
        """
        return self._get_resource_per_page(
            resource='client-property-values',
            per_page=per_page,
            page=page,
            params=params
        )

    def get_all_client_properties(self, params=None):
        """
        Get all client properties
        :param params: Search params
        :return: dict
        """
        return self._iterate_through_pages(self.get_client_properties_per_page, CLIENT_PROPERTY, params=params)

    def get_client_property(self, client_property_id):
        """
        Get a client property by the billomat id of a client property
        :param client_propery_id: the billomat id
        :return: the found client property dict
        """
        return self._create_get_request(resource=CLIENT_PROPERTIES, billomat_id=client_property_id)

    def create_client_property(self, client_property_dict):
        """
        Sets a client property
        :param client_property_dict: the client property
        :return:
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
        Get clients by a page paginated by a given number
        If you search tags, you can only search by client_id
        :param per_page: how many items per page
        :param page: which page
        :param params: search params.
        :return: the client tags
        """
        return self._get_resource_per_page(
            resource='client-tags',
            per_page=per_page,
            page=page,
            params=params
        )

    def get_all_client_tags(self, params=None):
        """
        Get all clients
        If you search tags, you can only search by client_id
        :param params: search params
        :return:
        """
        return self._iterate_through_pages(self.get_client_tags_per_page, CLIENT_TAG, params=params)

    def get_client_tag(self, client_tag_id):
        """
        Get a specific client tag by the billomat id
        :param client_tag_id: billomat id of the client tag
        :return: the specific client tag
        """
        return self._create_get_request(resource=CLIENT_TAGS, billomat_id=client_tag_id)

    def create_client_tag(self, client_tag_dict):
        """
        Creates a client atg
        :param client_tag_dict:
        :return:
        """
        return self._create_post_request(resource=CLIENT_TAGS, send_data=client_tag_dict)

    def delete_client_tag(self, client_tag_id):
        """
        Delete a specific client tag by the client tag id
        :param client_tag_id: the billomat id
        :return: Response Object
        """
        return self._create_delete_request(resource=CLIENT_TAGS, billomat_id=client_tag_id)

    """
    --------
    Billomat Client Contacts
    --------
    http://www.billomat.com/en/api/clients/contacts
    """

    def get_contacts_of_client_per_page(self, client_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'client_id': client_id}

        return self._get_resource_per_page(
            resource=CONTACTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_contacts_of_client(self, client_id):
        return self._iterate_through_pages(
            get_function=self.get_contacts_of_client_per_page,
            data_key=CONTACT,
            **{'client_id': client_id}
        )

    def get_contact_of_client(self, contact_id):
        return self._create_get_request(CONTACTS, contact_id)

    def create_contact_of_client(self, contact_dict):
        return self._create_post_request(resource=CONTACTS, send_data=contact_dict)

    def update_contact_of_client(self, contact_dict):
        return self._create_put_request(resource=CONTACTS, send_data=contact_dict)

    def delete_contact_of_client(self, client_id):
        return self._create_delete_request(resource=CONTACTS, billomat_id=client_id)

    """
    --------
    Billomat Supplier
    --------
    http://www.billomat.com/en/api/suppliers
    """

    def get_suppliers_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=SUPPLIERS, per_page=per_page, page=page, params=params)

    def get_all_suppliers(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_suppliers_per_page, data_key=SUPPLIER, params=params)

    def get_supplier(self, supplier_id):
        return self._create_get_request(resource=SUPPLIERS, billomat_id=supplier_id)

    def create_supplier(self, supplier_dict):
        return self._create_post_request(resource=SUPPLIERS, send_data=supplier_dict)

    def update_supplier(self, supplier_id, supplier_dict):
        return self._create_put_request(resource=SUPPLIERS, billomat_id=supplier_id, send_data=supplier_dict)

    def delete_supplier(self, supplier_id):
        return self._create_delete_request(resource=SUPPLIERS, billomat_id=supplier_id)

    """
    --------
    Billomat Supplier Properties
    --------
    http://www.billomat.com/en/api/suppliers/properties
    """

    def get_supplier_properties_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=SUPPLIER_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_supplier_properties(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_supplier_properties_per_page,
            data_key=SUPPLIER_PROPERTY,
            params=params
        )

    def get_supplier_property(self, supplier_property_id):
        return self._create_get_request(resource=SUPPLIER_PROPERTIES, billomat_id=supplier_property_id)

    def set_supplier_property(self, supplier_dict):
        return self._create_post_request(resource=SUPPLIER_PROPERTIES, send_data=supplier_dict)

    """
    --------
    Billomat Supplier Tags
    --------
    http://www.billomat.com/en/api/suppliers/tags
    """
    def get_tags_of_supplier_per_page(self, supplier_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'supplier_id': supplier_id}

        return self._get_resource_per_page(
            resource=SUPPLIER_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_supplier(self, supplier_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_supplier_per_page,
            data_key=SUPPLIER_TAG,
            **{'supplier_id': supplier_id}
        )

    def get_supplier_tag(self, supplier_tag_id):
        return self._create_get_request(resource=SUPPLIER_TAGS, billomat_id=supplier_tag_id)

    def create_supplier_tag(self, supplier_tag_dict):
        return self._create_post_request(resource=SUPPLIER_TAGS, send_data=supplier_tag_dict)

    def delete_supplier_tag(self, supplier_tag_id):
        return self._create_delete_request(resource=SUPPLIER_TAGS, billomat_id=supplier_tag_id)

    """
    --------
    Billomat Articles
    --------
    http://www.billomat.com/en/api/articles
    """
    def get_articles_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=ARTICLES, per_page=per_page, page=page, params=params)

    def get_all_articles(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_articles_per_page, data_key=ARTICLE, params=params)

    def get_article(self, article_id):
        return self._create_get_request(resource=ARTICLES, billomat_id=article_id)

    def create_article(self, article_dict):
        return self._create_post_request(resource=ARTICLES, send_data=article_dict)

    def update_article(self, article_id, article_dict):
        return self._create_put_request(resource=ARTICLES, billomat_id=article_id, send_data=article_dict)

    def delete_article(self, article_id):
        return self._create_delete_request(resource=ARTICLES, billomat_id=article_id)

    """
    --------
    Billomat Article Properties
    --------
    http://www.billomat.com/en/api/articles/properties
    """

    def get_article_properties_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=ARTICLE_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_article_properties(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_article_properties_per_page,
            data_key=ARTICLE_PROPERTY,
            params=params
        )

    def get_article_property(self, article_property_id):
        return self._create_get_request(resource=ARTICLE_PROPERTIES, billomat_id=article_property_id)

    def set_article_property(self, article_dict):
        return self._create_post_request(resource=ARTICLE_PROPERTIES, send_data=article_dict)

    """
    --------
    Billomat Article Tags
    --------
    http://www.billomat.com/en/api/articles/tags
    """
    def get_tags_of_article_per_page(self, article_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'article_id': article_id}

        return self._get_resource_per_page(
            resource=ARTICLE_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_article(self, article_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_article_per_page,
            data_key=ARTICLE_TAG,
            **{'article_id': article_id}
        )

    def get_article_tag(self, article_tag_id):
        return self._create_get_request(resource=ARTICLE_TAGS, billomat_id=article_tag_id)

    def create_article_tag(self, article_tag_dict):
        return self._create_post_request(resource=ARTICLE_TAGS, send_data=article_tag_dict)

    def delete_article_tag(self, article_tag_id):
        return self._create_delete_request(resource=ARTICLE_TAGS, billomat_id=article_tag_id)

    """
    --------
    Billomat Unit
    --------
    http://www.billomat.com/en/api/units
    """

    def get_units_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=UNITS, per_page=per_page, page=page, params=params)

    def get_all_units(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_units_per_page, data_key=UNIT, params=params)

    def get_unit(self, unit_id):
        return self._create_get_request(resource=UNITS, billomat_id=unit_id)

    def create_unit(self, unit_dict):
        return self._create_post_request(resource=UNITS, send_data=unit_dict)

    def update_unit(self, unit_id, unit_dict):
        return self._create_put_request(resource=UNITS, billomat_id=unit_id, send_data=unit_dict)

    def delete_unit(self, unit_id):
        return self._create_delete_request(resource=UNITS, billomat_id=unit_id)

    """
    --------
    Billomat Invoice
    --------
    http://www.billomat.com/en/api/invoices
    """

    def get_invoices_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=INVOICES, per_page=per_page, page=page, params=params)

    def get_all_invoices(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_invoices_per_page, data_key=INVOICE, params=params)

    def get_invoice(self, invoice_id):
        return self._create_get_request(resource=INVOICES, billomat_id=invoice_id)

    def create_invoice(self, invoice_dict):
        return self._create_post_request(resource=INVOICES, send_data=invoice_dict)

    def update_invoice(self, invoice_id, invoice_dict):
        return self._create_put_request(resource=INVOICES, billomat_id=invoice_id, send_data=invoice_dict)

    def delete_invoice(self, invoice_id):
        return self._create_delete_request(resource=INVOICES, billomat_id=invoice_id)

    """
    --------
    Billomat Invoice Item
    --------
    http://www.billomat.com/en/api/invoices/items
    """

    def get_items_of_invoice_per_page(self, invoice_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'invoice_id': invoice_id}

        return self._get_resource_per_page(
            resource=INVOICE_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_invoice(self, invoice_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_invoice_per_page,
            data_key=INVOICE_ITEM,
            **{'invoice_id': invoice_id}
        )

    def get_all_invoice_items(self, invoice_ids):
        assert(isinstance(invoice_ids, list))
        return self._create_flood_get_request(
            resource=INVOICE_ITEMS,
            data_key=INVOICE_ITEM,
            params=[{'invoice_id': invoice_id, 'per_page': '1000'} for invoice_id in invoice_ids]
        )

    def get_invoice_item(self, invoice_item_id):
        return self._create_get_request(INVOICE_ITEMS, invoice_item_id)

    def create_invoice_item(self, invoice_item_dict):
        return self._create_post_request(resource=INVOICE_ITEMS, send_data=invoice_item_dict)

    def update_invoice_item(self, invoice_item_id, invoice_item_dict):
        return self._create_put_request(resource=INVOICE_ITEMS, billomat_id=invoice_item_id, send_data=invoice_item_dict)

    def delete_invoice_item(self, invoice_item_id):
        return self._create_delete_request(resource=INVOICE_ITEMS, billomat_id=invoice_item_id)

    """
    --------
    Billomat Invoice Comment
    --------
    http://www.billomat.com/en/api/invoices/comments
    """

    def get_comments_of_invoice_per_page(self, invoice_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'invoice_id': invoice_id}

        return self._get_resource_per_page(
            resource=INVOICE_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_invoice(self, invoice_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_invoice_per_page,
            data_key=INVOICE_COMMENT,
            **{'invoice_id': invoice_id}
        )

    def get_invoice_comment(self, invoice_comment_id):
        return self._create_get_request(INVOICE_COMMENTS, invoice_comment_id)

    def create_invoice_comment(self, invoice_comment_dict):
        return self._create_post_request(resource=INVOICE_COMMENTS, send_data=invoice_comment_dict)

    def update_invoice_comment(self, invoice_comment_id, invoice_comment_dict):
        return self._create_put_request(
            resource=INVOICE_COMMENTS,
            billomat_id=invoice_comment_id,
            send_data=invoice_comment_dict
        )

    def delete_invoice_comment(self, invoice_comment_id):
        return self._create_delete_request(resource=INVOICE_COMMENTS, billomat_id=invoice_comment_id)

    """
    --------
    Billomat Invoice Payment
    --------
    http://www.billomat.com/en/api/invoices/payments
    """

    def get_invoice_payments_per_page(self, per_page=1000, page=1, params=None):
        if not params:
            params = {}

        return self._get_resource_per_page(
            resource=INVOICE_PAYMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_invoice_payments(self):
        return self._iterate_through_pages(
            get_function=self.get_invoice_payments_per_page,
            data_key=INVOICE_PAYMENT,
        )

    def get_invoice_payment(self, invoice_payment_id):
        return self._create_get_request(INVOICE_PAYMENTS, invoice_payment_id)

    def create_invoice_payment(self, invoice_payment_dict):
        return self._create_post_request(resource=INVOICE_PAYMENTS, send_data=invoice_payment_dict)

    def delete_invoice_payment(self, invoice_payment_id):
        return self._create_delete_request(resource=INVOICE_PAYMENTS, billomat_id=invoice_payment_id)

    """
    --------
    Billomat Invoice Tags
    --------
    http://www.billomat.com/en/api/invoices/tags
    """
    def get_tags_of_invoice_per_page(self, invoice_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'invoice_id': invoice_id}

        return self._get_resource_per_page(
            resource=INVOICE_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_invoice(self, invoice_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_invoice_per_page,
            data_key=INVOICE_TAG,
            **{'invoice_id': invoice_id}
        )

    def get_invoice_tag(self, invoice_tag_id):
        return self._create_get_request(resource=INVOICE_TAGS, billomat_id=invoice_tag_id)

    def create_invoice_tag(self, invoice_tag_dict):
        return self._create_post_request(resource=INVOICE_TAGS, send_data=invoice_tag_dict)

    def delete_invoice_tag(self, invoice_tag_id):
        return self._create_delete_request(resource=INVOICE_TAGS, billomat_id=invoice_tag_id)

    """
    --------
    Billomat Recurring
    --------
    http://www.billomat.com/en/api/recurrings
    """

    def get_recurrings_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=RECURRINGS, per_page=per_page, page=page, params=params)

    def get_all_recurrings(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_recurrings_per_page, data_key=RECURRING, params=params)

    def get_recurring(self, recurring_id):
        return self._create_get_request(resource=RECURRINGS, billomat_id=recurring_id)

    def create_recurring(self, recurring_dict):
        return self._create_post_request(resource=RECURRINGS, send_data=recurring_dict)

    def update_recurring(self, recurring_id, recurring_dict):
        return self._create_put_request(resource=RECURRINGS, billomat_id=recurring_id, send_data=recurring_dict)

    def delete_recurring(self, recurring_id):
        return self._create_delete_request(resource=RECURRINGS, billomat_id=recurring_id)

    """
    --------
    Billomat Recurring Item
    --------
    http://www.billomat.com/en/api/recurrings/items
    """

    def get_items_of_recurring_per_page(self, recurring_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'recurring_id': recurring_id}

        return self._get_resource_per_page(
            resource=RECURRING_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_recurring(self, recurring_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_recurring_per_page,
            data_key=RECURRING_ITEM,
            **{'recurring_id': recurring_id}
        )

    def get_all_recurring_items(self, recurring_ids):
        assert(isinstance(recurring_ids, list))
        return self._create_flood_get_request(
            resource=RECURRING_ITEMS,
            data_key=RECURRING_ITEM,
            params=[{'recurring_id': recurring_id, 'per_page': '1000'} for recurring_id in recurring_ids]
        )

    def get_recurring_item(self, recurring_item_id):
        return self._create_get_request(RECURRING_ITEMS, recurring_item_id)

    def create_recurring_item(self, recurring_item_dict):
        return self._create_post_request(resource=RECURRING_ITEMS, send_data=recurring_item_dict)

    def update_recurring_item(self, recurring_item_id, recurring_item_dict):
        return self._create_put_request(
            resource=RECURRING_ITEMS,
            billomat_id=recurring_item_id,
            send_data=recurring_item_dict
        )

    def delete_recurring_item(self, recurring_item_id):
        return self._create_delete_request(resource=RECURRING_ITEMS, billomat_id=recurring_item_id)

    """
    --------
    Billomat Recurring Tags
    --------
    http://www.billomat.com/en/api/recurrings/tags
    """
    def get_tags_of_recurring_per_page(self, recurring_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'recurring_id': recurring_id}

        return self._get_resource_per_page(
            resource=RECURRING_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_recurring(self, recurring_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_recurring_per_page,
            data_key=RECURRING_TAG,
            **{'recurring_id': recurring_id}
        )

    def get_recurring_tag(self, recurring_tag_id):
        return self._create_get_request(resource=RECURRING_TAGS, billomat_id=recurring_tag_id)

    def create_recurring_tag(self, recurring_tag_dict):
        return self._create_post_request(resource=RECURRING_TAGS, send_data=recurring_tag_dict)

    def delete_recurring_tag(self, recurring_tag_id):
        return self._create_delete_request(resource=RECURRING_TAGS, billomat_id=recurring_tag_id)

    """
    --------
    Billomat Recurring Email Receiver
    --------
    http://www.billomat.com/en/api/recurrings/receivers
    """
    def get_email_receivers_of_recurring_per_page(self, recurring_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'recurring_id': recurring_id}

        return self._get_resource_per_page(
            resource=RECURRING_EMAIL_RECEIVERS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_email_receivers_of_recurring(self, recurring_id):
        return self._iterate_through_pages(
            get_function=self.get_email_receivers_of_recurring_per_page,
            data_key=RECURRING_EMAIL_RECEIVER,
            **{'recurring_id': recurring_id}
        )

    def get_recurring_email_receiver(self, recurring_email_receiver_id):
        return self._create_get_request(resource=RECURRING_EMAIL_RECEIVERS, billomat_id=recurring_email_receiver_id)

    def create_recurring_email_receiver(self, recurring_email_receiver_dict):
        return self._create_post_request(resource=RECURRING_EMAIL_RECEIVERS, send_data=recurring_email_receiver_dict)

    def delete_recurring_email_receiver(self, recurring_email_receiver_id):
        return self._create_delete_request(resource=RECURRING_EMAIL_RECEIVERS, billomat_id=recurring_email_receiver_id)

    """
    --------
    Billomat Incoming
    --------
    http://www.billomat.com/en/api/incomings
    """

    def get_incomings_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=INCOMINGS, per_page=per_page, page=page, params=params)

    def get_all_incomings(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_incomings_per_page, data_key=INCOMING, params=params)

    def get_incoming(self, incoming_id):
        return self._create_get_request(resource=INCOMINGS, billomat_id=incoming_id)

    def create_incoming(self, incoming_dict):
        return self._create_post_request(resource=INCOMINGS, send_data=incoming_dict)

    def update_incoming(self, incoming_id, incoming_dict):
        return self._create_put_request(resource=INCOMINGS, billomat_id=incoming_id, send_data=incoming_dict)

    def delete_incoming(self, incoming_id):
        return self._create_delete_request(resource=INCOMINGS, billomat_id=incoming_id)

    """
    --------
    Billomat Incoming Comment
    --------
    http://www.billomat.com/en/api/incomings/comments
    """

    def get_comments_of_incoming_per_page(self, incoming_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'incoming_id': incoming_id}

        return self._get_resource_per_page(
            resource=INCOMING_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_incoming(self, incoming_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_incoming_per_page,
            data_key=INCOMING_COMMENT,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_comment(self, incoming_comment_id):
        return self._create_get_request(INCOMING_COMMENTS, incoming_comment_id)

    def create_incoming_comment(self, incoming_comment_dict):
        return self._create_post_request(resource=INCOMING_COMMENTS, send_data=incoming_comment_dict)

    def delete_incoming_comment(self, incoming_comment_id):
        return self._create_delete_request(resource=INCOMING_COMMENTS, billomat_id=incoming_comment_id)

    """
    --------
    Billomat Incoming Payment
    --------
    http://www.billomat.com/en/api/incomings/payments
    """

    def get_payments_of_incoming_per_page(self, incoming_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'incoming_id': incoming_id}

        return self._get_resource_per_page(
            resource=INCOMING_PAYMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_payments_of_incoming(self, incoming_id):
        return self._iterate_through_pages(
            get_function=self.get_payments_of_incoming_per_page,
            data_key=INCOMING_PAYMENT,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_payment(self, incoming_payment_id):
        return self._create_get_request(INCOMING_PAYMENTS, incoming_payment_id)

    def create_incoming_payment(self, incoming_payment_dict):
        return self._create_post_request(resource=INCOMING_PAYMENTS, send_data=incoming_payment_dict)

    def delete_incoming_payment(self, incoming_payment_id):
        return self._create_delete_request(resource=INCOMING_PAYMENTS, billomat_id=incoming_payment_id)

    """
    --------
    Billomat Incoming Properties
    --------
    http://www.billomat.com/en/api/incoming/properties
    """

    def get_incoming_properties_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=INCOMING_PROPERTIES, per_page=per_page, page=page, params=params)

    def get_all_incoming_properties(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(
            self.get_incoming_properties_per_page,
            data_key=INCOMING_PROPERTY,
            params=params
        )

    def get_incoming_property(self, incoming_property_id):
        return self._create_get_request(resource=INCOMING_PROPERTIES, billomat_id=incoming_property_id)

    def set_incoming_property(self, incoming_dict):
        return self._create_post_request(resource=INCOMING_PROPERTIES, send_data=incoming_dict)

    """
    --------
    Billomat Incoming Tags
    --------
    http://www.billomat.com/en/api/incomings/tags
    """
    def get_tags_of_incoming_per_page(self, incoming_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'incoming_id': incoming_id}

        return self._get_resource_per_page(
            resource=INCOMING_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_incoming(self, incoming_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_incoming_per_page,
            data_key=INCOMING_TAG,
            **{'incoming_id': incoming_id}
        )

    def get_incoming_tag(self, incoming_tag_id):
        return self._create_get_request(resource=INCOMING_TAGS, billomat_id=incoming_tag_id)

    def create_incoming_tag(self, incoming_tag_dict):
        return self._create_post_request(resource=INCOMING_TAGS, send_data=incoming_tag_dict)

    def delete_incoming_tag(self, incoming_tag_id):
        return self._create_delete_request(resource=INCOMING_TAGS, billomat_id=incoming_tag_id)

    """
    --------
    Billomat Inbox Documents
    --------
    http://www.billomat.com/en/api/incomings/inbox
    """
    def get_inbox_documents_per_page(self, per_page=1000, page=1, params=None):
        if not params:
            params = {}

        return self._get_resource_per_page(
            resource=INBOX_DOCUMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_inbox_documents(self):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_incoming_per_page,
            data_key=INBOX_DOCUMENT,
        )

    def get_inbox_document(self, inbox_document_id):
        return self._create_get_request(resource=INBOX_DOCUMENTS, billomat_id=inbox_document_id)

    def create_inbox_document(self, inbox_document_dict):
        return self._create_post_request(resource=INBOX_DOCUMENTS, send_data=inbox_document_dict)

    def delete_inbox_document(self, inbox_document_id):
        return self._create_delete_request(resource=INBOX_DOCUMENTS, billomat_id=inbox_document_id)

    """
    --------
    Billomat Offer
    --------
    http://www.billomat.com/en/api/estimates
    """

    def get_offers_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=OFFERS, per_page=per_page, page=page, params=params)

    def get_all_offers(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_offers_per_page, data_key=OFFER, params=params)

    def get_offer(self, offer_id):
        return self._create_get_request(resource=OFFERS, billomat_id=offer_id)

    def create_offer(self, offer_dict):
        return self._create_post_request(resource=OFFERS, send_data=offer_dict)

    def update_offer(self, offer_id, offer_dict):
        return self._create_put_request(resource=OFFERS, billomat_id=offer_id, send_data=offer_dict)

    def delete_offer(self, offer_id):
        return self._create_delete_request(resource=OFFERS, billomat_id=offer_id)

    """
    --------
    Billomat Offer Item
    --------
    http://www.billomat.com/en/api/estimates/items
    """

    def get_items_of_offer_per_page(self, offer_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'offer_id': offer_id}

        return self._get_resource_per_page(
            resource=OFFER_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_offer(self, offer_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_offer_per_page,
            data_key=OFFER_ITEM,
            **{'offer_id': offer_id}
        )

    def get_all_offer_items(self, offer_ids):
        assert(isinstance(offer_ids, list))
        return self._create_flood_get_request(
            resource=OFFER_ITEMS,
            data_key=OFFER_ITEM,
            params=[{'offer_id': offer_id, 'per_page': '1000'} for offer_id in offer_ids]
        )

    def get_offer_item(self, offer_item_id):
        return self._create_get_request(OFFER_ITEMS, offer_item_id)

    def create_offer_item(self, offer_item_dict):
        return self._create_post_request(resource=OFFER_ITEMS, send_data=offer_item_dict)

    def update_offer_item(self, offer_item_id, offer_item_dict):
        return self._create_put_request(resource=OFFER_ITEMS, billomat_id=offer_item_id, send_data=offer_item_dict)

    def delete_offer_item(self, offer_item_id):
        return self._create_delete_request(resource=OFFER_ITEMS, billomat_id=offer_item_id)

    """
    --------
    Billomat Offer Comments
    --------
    http://www.billomat.com/en/api/estimates/comments
    """

    def get_comments_of_offer_per_page(self, offer_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'offer_id': offer_id}

        return self._get_resource_per_page(
            resource=OFFER_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_offer(self, offer_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_offer_per_page,
            data_key=OFFER_COMMENT,
            **{'offer_id': offer_id}
        )

    def get_offer_comment(self, offer_comment_id):
        return self._create_get_request(OFFER_COMMENTS, offer_comment_id)

    def create_offer_comment(self, offer_comment_dict):
        return self._create_post_request(resource=OFFER_COMMENTS, send_data=offer_comment_dict)

    def update_offer_comment(self, offer_comment_id, offer_comment_dict):
        return self._create_put_request(
            resource=OFFER_COMMENTS,
            billomat_id=offer_comment_id,
            send_data=offer_comment_dict
        )

    def delete_offer_comment(self, offer_comment_id):
        return self._create_delete_request(resource=OFFER_COMMENTS, billomat_id=offer_comment_id)

    """
    --------
    Billomat Offer Tags
    --------
    http://www.billomat.com/en/api/estimates/tags
    """
    def get_tags_of_offer_per_page(self, offer_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'offer_id': offer_id}

        return self._get_resource_per_page(
            resource=OFFER_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_offer(self, offer_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_offer_per_page,
            data_key=OFFER_TAG,
            **{'offer_id': offer_id}
        )

    def get_offer_tag(self, offer_tag_id):
        return self._create_get_request(resource=OFFER_TAGS, billomat_id=offer_tag_id)

    def create_offer_tag(self, offer_tag_dict):
        return self._create_post_request(resource=OFFER_TAGS, send_data=offer_tag_dict)

    def delete_offer_tag(self, offer_tag_id):
        return self._create_delete_request(resource=OFFER_TAGS, billomat_id=offer_tag_id)

    """
    --------
    Billomat Credit Note
    --------
    http://www.billomat.com/en/api/credit-notes
    """

    def get_credit_notes_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=CREDIT_NOTES, per_page=per_page, page=page, params=params)

    def get_all_credit_notes(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_credit_notes_per_page, data_key=CREDIT_NOTE, params=params)

    def get_credit_note(self, credit_note_id):
        return self._create_get_request(resource=CREDIT_NOTES, billomat_id=credit_note_id)

    def create_credit_note(self, credit_note_dict):
        return self._create_post_request(resource=CREDIT_NOTES, send_data=credit_note_dict)

    def update_credit_note(self, credit_note_id, credit_note_dict):
        return self._create_put_request(resource=CREDIT_NOTES, billomat_id=credit_note_id, send_data=credit_note_dict)

    def delete_credit_note(self, credit_note_id):
        return self._create_delete_request(resource=CREDIT_NOTES, billomat_id=credit_note_id)

    """
    --------
    Billomat Credit Note Item
    --------
    http://www.billomat.com/en/api/credit-notes/items
    """

    def get_items_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'credit_note_id': credit_note_id}

        return self._get_resource_per_page(
            resource=CREDIT_NOTE_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_credit_note(self, credit_note_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_credit_note_per_page,
            data_key=CREDIT_NOTE_ITEM,
            **{'credit_note_id': credit_note_id}
        )

    def get_all_credit_note_items(self, credit_note_ids):
        assert(isinstance(credit_note_ids, list))
        return self._create_flood_get_request(
            resource=CREDIT_NOTE_ITEMS,
            data_key=CREDIT_NOTE_ITEM,
            params=[{'credit_note_id': credit_note_id, 'per_page': '1000'} for credit_note_id in credit_note_ids]
        )

    def get_credit_note_item(self, credit_note_item_id):
        return self._create_get_request(CREDIT_NOTE_ITEMS, credit_note_item_id)

    def create_credit_note_item(self, credit_note_item_dict):
        return self._create_post_request(resource=CREDIT_NOTE_ITEMS, send_data=credit_note_item_dict)

    def update_credit_note_item(self, credit_note_item_id, credit_note_item_dict):
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

    def get_comments_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'credit_note_id': credit_note_id}

        return self._get_resource_per_page(
            resource=CREDIT_NOTE_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_credit_note(self, credit_note_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_offer_per_page,
            data_key=CREDIT_NOTE_COMMENT,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_comment(self, credit_note_comment_id):
        return self._create_get_request(CREDIT_NOTE_COMMENTS, credit_note_comment_id)

    def create_credit_note_comment(self, credit_note_comment_dict):
        return self._create_post_request(resource=CREDIT_NOTE_COMMENTS, send_data=credit_note_comment_dict)

    def update_credit_note_comment(self, credit_note_comment_id, credit_note_comment_dict):
        return self._create_put_request(
            resource=CREDIT_NOTE_COMMENTS,
            billomat_id=credit_note_comment_id,
            send_data=credit_note_comment_dict
        )

    def delete_credit_note_comment(self, credit_note_comment_id):
        return self._create_delete_request(resource=CREDIT_NOTE_COMMENTS, billomat_id=credit_note_comment_id)

    """
    --------
    Billomat Credit Note Payment
    --------
    http://www.billomat.com/en/api/credit-notes/payments
    """

    def get_payments_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'credit_note_id': credit_note_id}

        return self._get_resource_per_page(
            resource=CREDIT_NOTE_PAYMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_payments_of_credit_note(self, credit_note_id):
        return self._iterate_through_pages(
            get_function=self.get_payments_of_credit_note_per_page,
            data_key=CREDIT_NOTE_PAYMENT,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_payment(self, credit_note_payment_id):
        return self._create_get_request(CREDIT_NOTE_PAYMENTS, credit_note_payment_id)

    def create_credit_note_payment(self, credit_note_payment_dict):
        return self._create_post_request(resource=CREDIT_NOTE_PAYMENTS, send_data=credit_note_payment_dict)

    def delete_credit_note_payment(self, credit_note_payment_id):
        return self._create_delete_request(resource=CREDIT_NOTE_PAYMENTS, billomat_id=credit_note_payment_id)

    """
    --------
    Billomat Credit Note Tags
    --------
    http://www.billomat.com/en/api/credit-notes/tags
    """
    def get_tags_of_credit_note_per_page(self, credit_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'credit_note_id': credit_note_id}

        return self._get_resource_per_page(
            resource=CREDIT_NOTE_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_credit_note(self, credit_note_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_credit_note_per_page,
            data_key=CREDIT_NOTE_TAG,
            **{'credit_note_id': credit_note_id}
        )

    def get_credit_note_tag(self, credit_note_tag_id):
        return self._create_get_request(resource=CREDIT_NOTE_TAGS, billomat_id=credit_note_tag_id)

    def create_credit_note_tag(self, credit_note_tag_dict):
        return self._create_post_request(resource=CREDIT_NOTE_TAGS, send_data=credit_note_tag_dict)

    def delete_credit_note_tag(self, credit_note_tag_id):
        return self._create_delete_request(resource=CREDIT_NOTE_TAGS, billomat_id=credit_note_tag_id)

    """
    --------
    Billomat Confirmation
    --------
    http://www.billomat.com/en/api/credit-notes
    """

    def get_confirmations_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=CONFIRMATIONS, per_page=per_page, page=page, params=params)

    def get_all_confirmations(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_confirmations_per_page, data_key=CONFIRMATION, params=params)

    def get_confirmation(self, confirmation_id):
        return self._create_get_request(resource=CONFIRMATIONS, billomat_id=confirmation_id)

    def create_confirmation(self, confirmation_dict):
        return self._create_post_request(resource=CONFIRMATIONS, send_data=confirmation_dict)

    def update_confirmation(self, confirmation_id, confirmation_dict):
        return self._create_put_request(
            resource=CONFIRMATIONS,
            billomat_id=confirmation_id,
            send_data=confirmation_dict
        )

    def delete_confirmation(self, confirmation_id):
        return self._create_delete_request(resource=CONFIRMATIONS, billomat_id=confirmation_id)

    """
    --------
    Billomat Confirmation Item
    --------
    http://www.billomat.com/en/api/confirmations/items
    """

    def get_items_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'confirmation_id': confirmation_id}

        return self._get_resource_per_page(
            resource=CONFIRMATION_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_confirmation(self, confirmation_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_credit_note_per_page,
            data_key=CONFIRMATION_ITEM,
            **{'confirmation_id': confirmation_id}
        )

    def get_all_confirmation_items(self, confirmation_ids):
        assert(isinstance(confirmation_ids, list))
        return self._create_flood_get_request(
            resource=CONFIRMATION_ITEMS,
            data_key=CONFIRMATION_ITEM,
            params=[{'confirmation_id': confirmation_id, 'per_page': '1000'} for confirmation_id in confirmation_ids]
        )

    def get_confirmation_item(self, confirmation_item_id):
        return self._create_get_request(CONFIRMATION_ITEMS, confirmation_item_id)

    def create_confirmation_item(self, confirmation_item_dict):
        return self._create_post_request(resource=CONFIRMATION_ITEMS, send_data=confirmation_item_dict)

    def update_confirmation_item(self, confirmation_item_id, confirmation_item_dict):
        return self._create_put_request(
            resource=CONFIRMATION_ITEMS,
            billomat_id=confirmation_item_id,
            send_data=confirmation_item_dict
        )

    def delete_confirmation_item(self, confirmation_item_id):
        return self._create_delete_request(resource=CONFIRMATION_ITEMS, billomat_id=confirmation_item_id)

    """
    --------
    Billomat Confirmation Comments
    --------
    http://www.billomat.com/en/api/confirmation/comments
    """

    def get_comments_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'confirmation_id': confirmation_id}

        return self._get_resource_per_page(
            resource=CONFIRMATION_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_confirmation(self, confirmation_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_confirmation_per_page,
            data_key=CONFIRMATION_COMMENT,
            **{'confirmation_id': confirmation_id}
        )

    def get_confirmation_comment(self, confirmation_comment_id):
        return self._create_get_request(CONFIRMATION_COMMENTS, confirmation_comment_id)

    def create_confirmation_comment(self, confirmation_comment_dict):
        return self._create_post_request(resource=CONFIRMATION_COMMENTS, send_data=confirmation_comment_dict)

    def update_confirmation_comment(self, confirmation_comment_id, confirmation_comment_dict):
        return self._create_put_request(
            resource=CONFIRMATION_COMMENTS,
            billomat_id=confirmation_comment_id,
            send_data=confirmation_comment_dict
        )

    def delete_confirmation_comment(self, confirmation_comment_id):
        return self._create_delete_request(resource=CONFIRMATION_COMMENTS, billomat_id=confirmation_comment_id)

    """
    --------
    Billomat Confirmation Tags
    --------
    http://www.billomat.com/en/api/confirmations/tags
    """
    def get_tags_of_confirmation_per_page(self, confirmation_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'confirmation_id': confirmation_id}

        return self._get_resource_per_page(
            resource=CONFIRMATION_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_confirmation(self, confirmation_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_confirmation_per_page,
            data_key=CONFIRMATION_TAG,
            **{'confirmation_id': confirmation_id}
        )

    def get_confirmation_tag(self, confirmation_tag_id):
        return self._create_get_request(resource=CONFIRMATION_TAGS, billomat_id=confirmation_tag_id)

    def create_confirmation_tag(self, confirmation_tag_dict):
        return self._create_post_request(resource=CONFIRMATION_TAGS, send_data=confirmation_tag_dict)

    def delete_confirmation_tag(self, confirmation_tag_id):
        return self._create_delete_request(resource=CONFIRMATION_TAGS, billomat_id=confirmation_tag_id)

    """
    --------
    Billomat Reminder
    --------
    http://www.billomat.com/en/api/reminders
    """

    def get_reminders_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=REMINDERS, per_page=per_page, page=page, params=params)

    def get_all_reminders(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_reminders_per_page, data_key=REMINDER, params=params)

    def get_reminder(self, reminder_id):
        return self._create_get_request(resource=REMINDERS, billomat_id=reminder_id)

    def create_reminder(self, reminder_dict):
        return self._create_post_request(resource=REMINDERS, send_data=reminder_dict)

    def update_reminder(self, reminder_id, reminder_dict):
        return self._create_put_request(
            resource=REMINDERS,
            billomat_id=reminder_id,
            send_data=reminder_dict
        )

    def delete_reminder(self, reminder_id):
        return self._create_delete_request(resource=REMINDERS, billomat_id=reminder_id)

    """
    --------
    Billomat Reminder Item
    --------
    http://www.billomat.com/en/api/reminders/items
    """

    def get_items_of_reminder_per_page(self, reminder_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'reminder_id': reminder_id}

        return self._get_resource_per_page(
            resource=REMINDER_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_reminder(self, reminder_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_reminder_per_page,
            data_key=REMINDER_ITEM,
            **{'reminder_id': reminder_id}
        )

    def get_all_reminder_items(self, reminder_ids):
        assert(isinstance(reminder_ids, list))
        return self._create_flood_get_request(
            resource=REMINDER_ITEMS,
            data_key=REMINDER_ITEM,
            params=[{'reminder_id': reminder_id, 'per_page': '1000'} for reminder_id in reminder_ids]
        )

    def get_reminder_item(self, reminder_item_id):
        return self._create_get_request(REMINDER_ITEMS, reminder_item_id)

    def create_reminder_item(self, reminder_item_dict):
        return self._create_post_request(resource=REMINDER_ITEMS, send_data=reminder_item_dict)

    def update_reminder_item(self, reminder_item_id, reminder_item_dict):
        return self._create_put_request(
            resource=REMINDER_ITEMS,
            billomat_id=reminder_item_id,
            send_data=reminder_item_dict
        )

    def delete_reminder_item(self, reminder_item_id):
        return self._create_delete_request(resource=REMINDER_ITEMS, billomat_id=reminder_item_id)

    """
    --------
    Billomat Reminder Tags
    --------
    http://www.billomat.com/en/api/reminders/tags
    """
    def get_tags_of_reminder_per_page(self, reminder_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'reminder_id': reminder_id}

        return self._get_resource_per_page(
            resource=REMINDER_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_reminder(self, reminder_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_reminder_per_page,
            data_key=REMINDER_TAG,
            **{'reminder_id': reminder_id}
        )

    def get_reminder_tag(self, reminder_tag_id):
        return self._create_get_request(resource=REMINDER_TAGS, billomat_id=reminder_tag_id)

    def create_reminder_tag(self, reminder_tag_dict):
        return self._create_post_request(resource=REMINDER_TAGS, send_data=reminder_tag_dict)

    def delete_reminder_tag(self, reminder_tag_id):
        return self._create_delete_request(resource=REMINDER_TAGS, billomat_id=reminder_tag_id)

    """
    --------
    Billomat Delivery Notes
    --------
    http://www.billomat.com/en/api/delivery-notes
    """

    def get_delivery_notes_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=DELIVERY_NOTES, per_page=per_page, page=page, params=params)

    def get_all_delivery_notes(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_delivery_notes_per_page, data_key=DELIVERY_NOTE, params=params)

    def get_delivery_note(self, delivery_note_id):
        return self._create_get_request(resource=DELIVERY_NOTES, billomat_id=delivery_note_id)

    def create_delivery_note(self, delivery_note_dict):
        return self._create_post_request(resource=DELIVERY_NOTES, send_data=delivery_note_dict)

    def update_delivery_note(self, delivery_note_id, delivery_note_dict):
        return self._create_put_request(
            resource=DELIVERY_NOTES,
            billomat_id=delivery_note_id,
            send_data=delivery_note_dict
        )

    def delete_delivery_note(self, delivery_note_id):
        return self._create_delete_request(resource=DELIVERY_NOTES, billomat_id=delivery_note_id)

    """
    --------
    Billomat Delivery Note Item
    --------
    http://www.billomat.com/en/api/delivery-notes/items
    """

    def get_items_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'delivery_note_id': delivery_note_id}

        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_ITEMS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_items_of_delivery_note(self, delivery_note_id):
        return self._iterate_through_pages(
            get_function=self.get_items_of_delivery_note_per_page,
            data_key=DELIVERY_NOTE_ITEM,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_all_delivery_note_items(self, delivery_note_ids):
        assert(isinstance(delivery_note_ids, list))
        return self._create_flood_get_request(
            resource=DELIVERY_NOTE_ITEMS,
            data_key=DELIVERY_NOTE_ITEM,
            params=[{'delivery_note_id': delivery_note_id, 'per_page': '1000'} for delivery_note_id in delivery_note_ids]
        )

    def get_delivery_note_item(self, delivery_note_item_id):
        return self._create_get_request(REMINDER_ITEMS, delivery_note_item_id)

    def create_delivery_note_item(self, delivery_note_item_dict):
        return self._create_post_request(resource=DELIVERY_NOTE_ITEMS, send_data=delivery_note_item_dict)

    def update_delivery_note_item(self, delivery_note_item_id, delivery_note_item_dict):
        return self._create_put_request(
            resource=DELIVERY_NOTE_ITEMS,
            billomat_id=delivery_note_item_id,
            send_data=delivery_note_item_dict
        )

    def delete_delivery_note_item(self, delivery_note_item_id):
        return self._create_delete_request(resource=DELIVERY_NOTE_ITEMS, billomat_id=delivery_note_item_id)

    """
    --------
    Billomat Delivery Note Comments
    --------
    http://www.billomat.com/en/api/delivery-notes/comments
    """

    def get_comments_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'delivery_note_id': delivery_note_id}

        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_delivery_note(self, delivery_note_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_confirmation_per_page,
            data_key=DELIVERY_NOTE_COMMENT,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_delivery_note_comment(self, delivery_note_comment_id):
        return self._create_get_request(DELIVERY_NOTE_COMMENTS, delivery_note_comment_id)

    def create_delivery_note_comment(self, delivery_note_comment_dict):
        return self._create_post_request(resource=DELIVERY_NOTE_COMMENTS, send_data=delivery_note_comment_dict)

    def update_delivery_note_comment(self, delivery_note_comment_id, delivery_note_comment_dict):
        return self._create_put_request(
            resource=DELIVERY_NOTE_COMMENTS,
            billomat_id=delivery_note_comment_id,
            send_data=delivery_note_comment_dict
        )

    def delete_delivery_note_comment(self, delivery_note_comment_id):
        return self._create_delete_request(resource=DELIVERY_NOTE_COMMENTS, billomat_id=delivery_note_comment_id)

    """
    --------
    Billomat Delivery Note Tags
    --------
    http://www.billomat.com/en/api/delivery-notes/tags
    """
    def get_tags_of_delivery_note_per_page(self, delivery_note_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'delivery_note_id': delivery_note_id}

        return self._get_resource_per_page(
            resource=DELIVERY_NOTE_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_delivery_note(self, delivery_note_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_delivery_note_per_page,
            data_key=DELIVERY_NOTE_TAG,
            **{'delivery_note_id': delivery_note_id}
        )

    def get_delivery_note_tag(self, delivery_note_tag_id):
        return self._create_get_request(resource=DELIVERY_NOTE_TAGS, billomat_id=delivery_note_tag_id)

    def create_delivery_note_tag(self, delivery_note_tag_dict):
        return self._create_post_request(resource=DELIVERY_NOTE_TAGS, send_data=delivery_note_tag_dict)

    def delete_delivery_note_tag(self, delivery_note_tag_id):
        return self._create_delete_request(resource=DELIVERY_NOTE_TAGS, billomat_id=delivery_note_tag_id)

    """
    --------
    Billomat Letters
    --------
    http://www.billomat.com/en/api/letters
    """

    def get_letters_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=LETTERS, per_page=per_page, page=page, params=params)

    def get_all_letters(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_letters_per_page, data_key=LETTER, params=params)

    def get_letter(self, letter_id):
        return self._create_get_request(resource=LETTERS, billomat_id=letter_id)

    def create_letter(self, letter_dict):
        return self._create_post_request(resource=LETTERS, send_data=letter_dict)

    def update_letter(self, letter_id, letter_dict):
        return self._create_put_request(
            resource=LETTERS,
            billomat_id=letter_id,
            send_data=letter_dict
        )

    def delete_letter(self, letter_id):
        return self._create_delete_request(resource=LETTERS, billomat_id=letter_id)

    """
    --------
    Billomat Letter Comments
    --------
    http://www.billomat.com/en/api/letters/comments
    """

    def get_comments_of_letter_per_page(self, letter_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'letter_id': letter_id}

        return self._get_resource_per_page(
            resource=LETTER_COMMENTS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_comments_of_letter(self, letter_id):
        return self._iterate_through_pages(
            get_function=self.get_comments_of_letter_per_page,
            data_key=LETTER_COMMENT,
            **{'letter_id': letter_id}
        )

    def get_letter_comment(self, letter_comment_id):
        return self._create_get_request(LETTER_COMMENTS, letter_comment_id)

    def create_letter_comment(self, letter_comment_dict):
        return self._create_post_request(resource=LETTER_COMMENTS, send_data=letter_comment_dict)

    def update_letter_comment(self, letter_comment_id, letter_comment_dict):
        return self._create_put_request(
            resource=LETTER_COMMENTS,
            billomat_id=letter_comment_id,
            send_data=letter_comment_dict
        )

    def delete_letter_comment(self, letter_comment_id):
        return self._create_delete_request(resource=LETTER_COMMENTS, billomat_id=letter_comment_id)

    """
    --------
    Billomat Letter Tags
    --------
    http://www.billomat.com/en/api/letters/tags
    """
    def get_tags_of_letter_per_page(self, letter_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'letter_id': letter_id}

        return self._get_resource_per_page(
            resource=LETTER_TAGS,
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_tags_of_letter(self, letter_id):
        return self._iterate_through_pages(
            get_function=self.get_tags_of_letter_per_page,
            data_key=REMINDER_TAG,
            **{'letter_id': letter_id}
        )

    def get_letter_tag(self, letter_tag_id):
        return self._create_get_request(resource=LETTER_TAGS, billomat_id=letter_tag_id)

    def create_letter_tag(self, letter_tag_dict):
        return self._create_post_request(resource=LETTER_TAGS, send_data=letter_tag_dict)

    def delete_letter_tag(self, letter_tag_id):
        return self._create_delete_request(resource=LETTER_TAGS, billomat_id=letter_tag_id)

    """
    --------
    Billomat Template
    --------
    http://www.billomat.com/en/api/templates
    """

    def get_templates_per_page(self, per_page=1000, page=1, params=None):
        return self._get_resource_per_page(resource=TEMPLATES, per_page=per_page, page=page, params=params)

    def get_all_templates(self, params=None):
        if not params:
            params = {}
        return self._iterate_through_pages(self.get_templates_per_page, data_key=TEMPLATE, params=params)

    def get_template(self, template_id):
        return self._create_get_request(resource=TEMPLATES, billomat_id=template_id)

    def create_template(self, template_dict):
        return self._create_post_request(resource=TEMPLATES, send_data=template_dict)

    def update_template(self, template_id, template_dict):
        return self._create_put_request(
            resource=TEMPLATES,
            billomat_id=template_id,
            send_data=template_dict
        )

    def delete_template(self, template_id):
        return self._create_delete_request(resource=TEMPLATES, billomat_id=template_id)
