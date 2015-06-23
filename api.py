import math
import json
import logging

import requests

from resources import *

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
        self.api_url = "https://{}.billomat.net/api/".format(billomat_id)
        self.session = self._create_session()

    def _create_session(self):
        """
        Creates the billomat session and returns it
        """
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-BillomatApiKey': self.api_key,
                'X-AppId': self.app_id,
                'X-AppSecret': self.app_secret,
            }
        )
        session.verify = True
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
    Billomat article Properties
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
