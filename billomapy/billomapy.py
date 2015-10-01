import json
import math
import logging
import collections

from tornado import ioloop, httpclient
from tornado.httputil import url_concat

from .resources import *

logger = logging.getLogger(__name__)


class BillomapyResponseError(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Request hatte einen Fehler: Code: {}, Message: {}'.format(self.code, self.message)


class BillomapyParseError(Exception):

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return 'Folgender Inhalt konnte nicht in JSON geparsed werden: {}'.format(self.content)


class Billomapy(object):

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
        self.http_client = httpclient.AsyncHTTPClient()
        self.request_counter = 0
        self.responses = []

    def gen_dict_extract(self, key, var):
        if hasattr(var, 'iteritems'):
            for k, v in var.iteritems():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.gen_dict_extract(key, d):
                            yield result

    def _save_response_to_responses(self, response):
        try:
            temp_response_body = json.loads(response.body)
            self.responses.append(temp_response_body)
        except ValueError, TypeError:
            if response.request.method != 'PUT' and response.request.method != 'DELETE':
                raise BillomapyParseError(response.body)
            else:
                temp_response_body = response
        return temp_response_body

    def _handle_request_counter(self):
        self.request_counter -= 1

        if self.request_counter == 0:
            ioloop.IOLoop.instance().stop()

    def handle_request(self, response):
        try:
            self._save_response_to_responses(response)
        # CATCH EM ALL!!!
        except Exception as e:
            ioloop.IOLoop.instance().stop()
            raise e

        self._handle_request_counter()

    def handle_pagination_request(self, response):
        temp_response_body = self._save_response_to_responses(response)
        total = [total for total in self.gen_dict_extract('@total', temp_response_body)]
        per_page = [per_page for per_page in self.gen_dict_extract('@per_page', temp_response_body)]

        for page in range(1, int(math.ceil(float(total[0]) / float(per_page[0])))):
            response.request.params['page'] = (
                response.request.params['page'] + 1
                if 'page' in response.request.params else 2
            )

            self.queue_get_request(
                resource=response.request.resource,
                params=response.request.params,
            )

        self._handle_request_counter()

    def _create_http_get_request(self, resource, params=None):
        http_request = httpclient.HTTPRequest(
            url=url_concat(self.api_url + resource, params),
            method='GET',
            connect_timeout=1000,
            request_timeout=1000,
            headers=self.billomat_header,
        )

        http_request.resource = resource
        http_request.params = params
        return http_request

    def queue_pagination_request(self, resource, params=None):
        if not params:
            params = {}

        self.http_client.fetch(
            self._create_http_get_request(resource, params),
            self.handle_pagination_request
        )
        self.request_counter += 1

    def queue_get_request(self, resource, params=None):
        if not params:
            params = {}
        self.http_client.fetch(
            self._create_http_get_request(resource, params),
            self.handle_request
        )
        self.request_counter += 1

    def queue_post_request(self, resource, post_data, params=None):
        if not params:
            params = {}

        self.http_client.fetch(
            httpclient.HTTPRequest(
                url=url_concat(self.api_url + resource, params),
                method='POST',
                body=json.dumps(post_data),
                connect_timeout=500,
                request_timeout=500,
                headers=self.billomat_header,
            ),
            self.handle_request
        )
        self.request_counter += 1

    def queue_put_request(self, resource, put_data, params):
        if not params:
            params = {}

        self.http_client.fetch(
            httpclient.HTTPRequest(
                url=url_concat(self.api_url + resource, params),
                method='PUT',
                body=json.dumps(put_data),
                connect_timeout=500,
                request_timeout=500,
                headers=self.billomat_header,
            ),
            self.handle_request
        )
        self.request_counter += 1

    def queue_delete_request(self, resource, params):
        if not params:
            params = {}

        self.http_client.fetch(
            httpclient.HTTPRequest(
                url=url_concat(self.api_url + resource, params),
                method='DELETE',
                connect_timeout=500,
                request_timeout=500,
                headers=self.billomat_header,
            ),
            self.handle_request
        )
        self.request_counter += 1

    def start_requests(self):
        ioloop.IOLoop.instance().start()

    def _get_all_data(self, resource, params=None):
        self.responses = []
        if not params:
            params = {'per_page': 100, 'page': 1}
        else:
            temp_params = {'per_page': 100, 'page': 1}
            temp_params.update(params)
            params = temp_params

        self.queue_pagination_request(resource, params)
        self.start_requests()
        return self.responses

    def _get_item_data(self, resource, foreign_ids, foreign_key, params=None):
        assert (isinstance(foreign_ids, collections.Iterable))
        self.responses = []
        if not params:
            params = {'per_page': 100, 'page': 1}
        else:
            temp_params = {'per_page': 100, 'page': 1}
            temp_params.update(params)
            params = temp_params

        for foreign_id in foreign_ids:
            temp_params = params.copy()
            temp_params.update({foreign_key: foreign_id})
            self.queue_pagination_request(resource, temp_params)
        self.start_requests()
        return self.responses

    def _get_specific_data(self, billomat_id, resource, params=None):
        assert (isinstance(billomat_id, int) or isinstance(billomat_id, basestring))
        self.responses = []
        if not params:
            params = {'per_page': 100, 'page': 1}
        else:
            temp_params = {'per_page': 100, 'page': 1}
            temp_params.update(params)
            params = temp_params

        self.queue_get_request(resource + '/' + str(billomat_id), params)
        self.start_requests()
        return self.responses

    def _create_specific_data(self, resource, data, params=None):
        assert (isinstance(data, dict))
        self.responses = []
        if not params:
            params = {}

        self.queue_post_request(resource, data, params)
        self.start_requests()
        return self.responses

    def _edit_specific_data(self, billomat_id, resource, data, params=None):
        assert (isinstance(data, dict))
        assert (isinstance(billomat_id, int) or isinstance(billomat_id, basestring))
        self.responses = []
        if not params:
            params = {}

        self.queue_put_request(resource + '/' + str(billomat_id), data, params)
        self.start_requests()
        return self.responses

    def _delete_specific_data(self, billomat_id, resource, params=None):
        assert (isinstance(billomat_id, int) or isinstance(billomat_id, basestring))
        self.responses = []
        if not params:
            params = {}

        self.queue_delete_request(resource + '/' + str(billomat_id), params)
        self.start_requests()
        return self.responses

    def resolve_response_data(self, responses, head_key=None, data_key=None):
        temp_data = []
        for response in responses:
            if head_key and data_key:
                temp_data += self._resolve_group_response_data(response, head_key, data_key)
            elif not head_key and data_key:
                temp_data += self._resolve_specific_response_data(response, data_key)
        return temp_data

    def _resolve_group_response_data(self, response, head_key, data_key):
        temp_data = []
        if head_key in response and data_key in response[head_key]:
            if isinstance(response[head_key][data_key], dict):
                response[head_key][data_key] = [response[head_key][data_key]]
            temp_data += response[head_key][data_key]
        return temp_data

    def _resolve_specific_response_data(self, response, data_key):
        temp_data = []
        if data_key in response:
            if isinstance(response[data_key], dict):
                response[data_key] = [response[data_key]]
            temp_data += response[data_key]
        return temp_data

# GET ALL DATA

    def get_all_clients(self, params=None):
        return self._get_all_data(CLIENTS, params)

    def get_all_client_properties(self, params=None):
        return self._get_all_data(CLIENT_PROPERTIES, params)

    def get_all_contacts(self, client_ids):
        return self._get_item_data(CONTACTS, client_ids, 'client_id')

    def get_all_suppliers(self, params=None):
        return self._get_all_data(SUPPLIERS, params)

    def get_all_articles(self, params=None):
        return self._get_all_data(ARTICLES, params)

    def get_all_units(self, params=None):
        return self._get_all_data(UNITS, params)

    def get_all_invoices(self, params=None):
        return self._get_all_data(INVOICES, params)

    def get_all_invoice_items(self, invoice_ids):
        return self._get_item_data(INVOICE_ITEMS, invoice_ids, 'invoice_id')

    def get_all_recurrings(self, params=None):
        return self._get_all_data(RECURRINGS, params)

    def get_all_recurring_items(self, recurring_ids):
        return self._get_item_data(RECURRING_ITEMS, recurring_ids, 'recurring_id')

    def get_all_incomings(self, params=None):
        return self._get_all_data(INCOMINGS, params)

    def get_all_offers(self, params=None):
        return self._get_all_data(OFFERS, params)

    def get_all_offer_items(self, offer_ids):
        return self._get_item_data(OFFER_ITEMS, offer_ids, 'offer_id')

    def get_all_credit_notes(self, params=None):
        return self._get_all_data(CREDIT_NOTES, params)

    def get_all_credit_note_items(self, credit_note_ids):
        return self._get_item_data(CREDIT_NOTES, credit_note_ids, 'credit_note_id')

    def get_all_confirmations(self, params=None):
        return self._get_all_data(CONFIRMATIONS, params)

    def get_all_confirmation_items(self, confirmation_ids):
        return self._get_item_data(CONFIRMATION_ITEMS, confirmation_ids, 'confirmation_id')

    def get_all_reminders(self, params=None):
        return self._get_all_data(REMINDERS, params)

    def get_all_reminder_items(self, reminder_ids):
        return self._get_item_data(REMINDER_ITEMS, reminder_ids, 'reminder_id')

    def get_all_delivery_notes(self, params=None):
        return self._get_all_data(DELIVERY_NOTES, params)

    def get_all_delivery_note_items(self, delivery_note_ids):
        return self._get_item_data(DELIVERY_NOTE_ITEMS, delivery_note_ids, 'delivery_note_id')

    def get_all_letters(self, params=None):
        return self._get_all_data(LETTERS, params)

    def get_all_templates(self, params=None):
        return self._get_all_data(TEMPLATES, params)

# GET SPECIFIC DATA

    def get_specific_client(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CLIENTS, params)

    def get_specific_client_property(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CLIENT_PROPERTIES, params)

    def get_specific_contact(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CONTACTS, params)

    def get_specific_supplier(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, SUPPLIERS, params)

    def get_specific_article(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, ARTICLES, params)

    def get_specific_unit(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, UNITS, params)

    def get_specific_invoice(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, INVOICES, params)

    def get_invoice_pdf(self, billomat_id, params=None):
        return self._get_specific_data(str(billomat_id) + '/pdf', INVOICES, params)

    def get_specific_invoice_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, INVOICE_ITEMS, params)

    def get_invoice_items_for_invoice(self, invoice_id):
        return self._get_specific_data('', INVOICE_ITEMS, {'invoice_id': invoice_id})

    def get_specific_recurring(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, RECURRINGS, params)

    def get_specific_recurring_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, RECURRING_ITEMS, params)

    def get_specific_incoming(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, INCOMINGS, params)

    def get_specific_offer(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, OFFERS, params)

    def get_specific_offer_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, OFFER_ITEMS, params)

    def get_specific_credit_note(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CREDIT_NOTES, params)

    def get_specific_credit_note_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CREDIT_NOTE_ITEMS, params)

    def get_specific_confirmation(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CONFIRMATIONS, params)

    def get_specific_confirmation_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, CONFIRMATION_ITEMS, params)

    def get_specific_reminder(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, REMINDERS, params)

    def get_specific_reminder_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, REMINDER_ITEMS, params)

    def get_specific_delivery_note(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, DELIVERY_NOTES, params)

    def get_specific_delivery_note_item(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, DELIVERY_NOTE_ITEMS, params)

    def get_specific_letter(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, LETTERS, params)

    def get_specific_template(self, billomat_id, params=None):
        return self._get_specific_data(billomat_id, TEMPLATES, params)

# CREATE DATA

    def create_client(self, data, params=None):
        return self._create_specific_data(CLIENTS, data, params)

    def create_client_property(self, data, params=None):
        return self._create_specific_data(CLIENT_PROPERTIES , data, params)

    def create_supplier(self, data, params=None):
        return self._create_specific_data(SUPPLIERS, data, params)

    def create_article(self, data, params=None):
        return self._create_specific_data(ARTICLES, data, params)

    def create_unit(self, data, params=None):
        return self._create_specific_data(UNITS, data, params)

    def create_invoice(self, data, params=None):
        return self._create_specific_data(INVOICES, data, params)

    def create_invoice_item(self, data, params=None):
        return self._create_specific_data(INVOICE_ITEMS, data, params)

    def create_recurring(self, data, params=None):
        return self._create_specific_data(RECURRINGS, data, params)

    def create_recurring_item(self, data, params=None):
        return self._create_specific_data(RECURRING_ITEMS, data, params)

    def create_incoming(self, data, params=None):
        return self._create_specific_data(INCOMINGS, data, params)

    def create_offer(self, data, params=None):
        return self._create_specific_data(OFFERS, data, params)

    def create_offer_item(self, data, params=None):
        return self._create_specific_data(OFFER_ITEMS, data, params)

    def create_credit_note(self, data, params=None):
        return self._create_specific_data(CREDIT_NOTES, data, params)

    def create_credit_note_item(self, data, params=None):
        return self._create_specific_data(CREDIT_NOTE_ITEMS, data, params)

    def create_confirmation(self, data, params=None):
        return self._create_specific_data(CONFIRMATIONS, data, params)

    def create_confirmation_item(self, data, params=None):
        return self._create_specific_data(CONFIRMATION_ITEMS, data, params)

    def create_reminder(self, data, params=None):
        return self._create_specific_data(REMINDERS, data, params)

    def create_reminder_item(self, data, params=None):
        return self._create_specific_data(REMINDER_ITEMS, data, params)

    def create_delivery_note(self, data, params=None):
        return self._create_specific_data(DELIVERY_NOTES, data, params)

    def create_delivery_note_item(self, data, params=None):
        return self._create_specific_data(DELIVERY_NOTE_ITEMS, data, params)

    def create_letter(self, data, params=None):
        return self._create_specific_data(LETTERS, data, params)

    def create_template(self, data, params=None):
        return self._create_specific_data(TEMPLATES, data, params)

# SEND DATA

    def send_invoice_mail(self, billomat_id, data, params=None):
        mail_data = {'email': {}}
        if data:
            mail_data['email'].update(data)
        return self._create_specific_data(INVOICES + '/' + str(billomat_id) + '/email', mail_data, params)

# EDIT DATA

    def edit_client(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, CLIENTS, data, params)

    def edit_supplier(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, SUPPLIERS, data, params)

    def edit_article(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, ARTICLES, data, params)

    def edit_unit(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, UNITS, data, params)

    def edit_invoice(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, INVOICES, data, params)

    def complete_invoice(self, billomat_id, data={}, params=None):
        complete_data = {'complete': {}}
        if data:
            complete_data['complete'].update(data)
        return self._edit_specific_data(str(billomat_id) + '/complete', INVOICES, complete_data, params)

    def edit_invoice_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, INVOICE_ITEMS, data, params)

    def edit_recurring(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, RECURRINGS, data, params)

    def edit_recurring_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, RECURRING_ITEMS, data, params)

    def edit_incoming(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, INCOMINGS, data, params)

    def edit_offer(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, OFFERS, data, params)

    def edit_offer_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, OFFER_ITEMS, data, params)

    def edit_credit_note(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, CREDIT_NOTES, data, params)

    def edit_credit_note_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, CREDIT_NOTE_ITEMS, data, params)

    def edit_cofirmation(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, CONFIRMATIONS, data, params)

    def edit_confirmation_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, CONFIRMATION_ITEMS, data, params)

    def edit_reminder(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, REMINDERS, data, params)

    def edit_reminder_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, REMINDER_ITEMS, data, params)

    def edit_delivery_note(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, DELIVERY_NOTES, data, params)

    def edit_delivery_note_item(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, DELIVERY_NOTE_ITEMS, data, params)

    def edit_letter(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, LETTERS, data, params)

    def edit_template(self, billomat_id, data, params=None):
        return self._edit_specific_data(billomat_id, TEMPLATES, data, params)

# DELETE DATA

    def delete_client(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, CLIENTS, params)

    def delete_supplier(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, SUPPLIERS, params)

    def delete_article(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, ARTICLES, params)

    def delete_unit(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, UNITS, params)

    def delete_invoice(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, INVOICES, params)

    def delete_invoice_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, INVOICE_ITEMS, params)

    def delete_recurring(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, RECURRINGS, params)

    def delete_recurring_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, RECURRING_ITEMS, params)

    def delete_incoming(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, INCOMINGS, params)

    def delete_offer(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, OFFERS, params)

    def delete_offer_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, OFFER_ITEMS, params)

    def delete_credit_note(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, CREDIT_NOTES, params)

    def delete_credit_note_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, CREDIT_NOTE_ITEMS, params)

    def delete_confirmation(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, CONFIRMATIONS, params)

    def delete_confirmation_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, CONFIRMATION_ITEMS, params)

    def delete_reminder(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, REMINDERS, params)

    def delete_reminder_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, REMINDER_ITEMS, params)

    def delete_delivery_note(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, DELIVERY_NOTES, params)

    def delete_delivery_note_item(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, DELIVERY_NOTE_ITEMS, params)

    def delete_letter(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, LETTERS, params)

    def delete_template(self, billomat_id, params=None):
        return self._delete_specific_data(billomat_id, TEMPLATES, params)

# CANCEL DATA

    def cancel_invoice(self, billomat_id, data={}, params=None):
        return self._edit_specific_data(str(billomat_id) + '/cancel', INVOICES, data, params)