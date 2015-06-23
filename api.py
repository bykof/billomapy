import math
import json
import logging

import requests

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

    --------
    Searching
    --------
    Parameter       Description
    name            the name of the company or client you are searching for
    client_number   the client number
    email           the email address
    first_name      the first name of the contact person
    last_name       the last name of the contact person
    country_code    the country code by ISO 3166 Alpha-2
    note            the note of the client
    invoice_id      the invoice id you created for the customer (comma separated if there are many)
    tags            the tags (comma separated if there are many)

    --------
    Creating
    --------
    If you will create or update a client, here are the fields you can edit.
    element	                    Description	                                Type	    Default value	    Mandatory
    archived	                State of archival storage.
                                1=archived, 0=active	                    BOOL	    0
    number_pre	                Prefix	                                    ALNUM	    Value from settings
    number	                    sequential number	                        INT	        next free number
    number_length	            Minimum length of the customer number
                                (to be filled with leading zeros)	        INT	        Value from settings
    name	                    Company name	                            ALNUM
    street	                    Street	                                    ALNUM
    zip	                        Zip code	                                ALNUM
    city	                    City	                                    ALNUM
    state	                    State, county, district, region         	ALNUM
    country_code	            Country	Country code as                     ISO 3166
                                                                            Alpha-2	    Value from settings
    first_name	                First name	                                ALNUM
    last_name	                Last name	                                ALNUM
    salutation	                Salutation	                                ALNUM
    phone	                    Phone	                                    ALNUM
    fax	                        Fax	                                        ALNUM
    mobile	                    mobile number	                            ALNUM
    email	                    Email	                                    EMAIL
    www	                        Website	                                    URL
                                                                            (w/o http)
    tax_number	                Tax number	                                ALNUM
    vat_number	                VAT number	                                VAT number
    bank_account_number	        Bank account number	                        ALNUM
    bank_account_owner	        Bank account owner	                        ALNUM
    bank_number	                Bank identifier code	                    ALNUM
    bank_name	                Bank name	                                ALNUM
    bank_swift	                SWIFT/BIC	                                ALNUM
    bank_iban	                IBAN	valid IBAN
    sepa_mandate	            Mandate reference of a
                                SEPA Direct Debit mandate	                ALNUM
    sepa_mandate_date	        Date of issue of the
                                SEPA Direct Debit mandate	                DATE
    locale	                    Locale of the client.
                                If no value is passed, the locale of the
                                account will be applied to the client.  	ALNUM
    tax_rule	                Tax Rule	                                TAX,
                                                                            NO_TAX,
                                                                            COUNTRY	    COUNTRY
    default_payment_types	    Payment Type
                                (eg. CASH, BANK_TRANSFER, PAYPAL, ...).
                                More than one payment type could be given
                                as a comma separated list.
                                Theses payment types will be logically
                                OR-connected. You can find a overview of
                                all payment types at API documentation of
                                payments. If no value is passed,
                                the customer will be offered the payment
                                types specified at the account settings.    ALNUM
    net_gross	                Price basis
                                (net, gross, according to account settings)	NET,
                                                                            GROSS,
                                                                            SETTINGS    SETTINGS
    note	                    Note            	                        ALNUM
    discount_rate_type	        Type of the default value for
                                discount rate	                            SETTINGS,
                                                                            ABSOLUTE,
                                                                            RELATIVE    SETTINGS
    discount_rate	            Discount rate	                            FLOAT
    discount_days_type	        Type of the default value for
                                discount interval	                        SETTINGS,
                                                                            ABSOLUTE,
                                                                            RELATIVE	SETTINGS
    discount_days	            Discount period in days	                    FLOAT
    due_days_type	            Type of the default value for maturity	    SETTINGS,
                                                                            ABSOLUTE,
                                                                            RELATIVE	SETTINGS
    due_days	                Maturity in days from invoice date	        INT
    reminder_due_days_type	    Type of the default value for
                                reminder maturity	                        SETTINGS,
                                                                            ABSOLUTE,
                                                                            RELATIVE    SETTINGS
    reminder_due_days	        Reminder maturity	                        INT
    offer_validity_days_type	Type of the default value for
                                validity of estimates	                    SETTINGS,
                                                                            ABSOLUTE,
                                                                            RELATIVE	SETTINGS
    offer_validity_days         Validity of estimates	                    INT
    currency_code	            The currency for this client.
                                If this field is empty,
                                the account currency is used.	            ISO currency code
    price_group             	Articles can have several prices.
                                The pricegroup defines which
                                price applies to the client.	            INT

    --------
    Deleting
    --------
    Deleting is only possible if no documents exist for this client.
    """

    def get_clients_per_page(self, per_page=1000, page=1, params=None):
        """
        Get clients per page
        :param per_page: How many clients per page. Default: 1000
        :param page: Which page. Default: 1
        :param params: Search parameters. Default: {}
        :return: dict
        """
        return self._get_resource_per_page(resource='clients', per_page=per_page, page=page, params=params)

    def get_all_clients(self, params=None):
        """
        Get all clients
        :param params: Search parameters. Default: {
        :return: dict
        """
        return self._iterate_through_pages(self.get_clients_per_page, 'client', params=params)

    def get_client(self, client_id):
        """
        Get a specific client by the billomat client id
        :param client_id: The specific client id
        :return: dict
        """
        return self._create_get_request(resource='clients', billomat_id=client_id)

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
        return self._create_post_request('clients', client_dict)

    def update_client(self, client_id, client_dict):
        """
        Updates a client with the given keys and values in the dict
        :param client_id: the client which you want to update
        :param client_dict: the key, value pairs (see doc)
        :return: response dict of billomat
        """
        return self._create_put_request('clients', client_id, client_dict)

    def delete_client(self, client_id):
        """
        Deletes a client
        :param client_id: the client billomat id
        :return: the response object
        """
        return self._create_delete_request('clients', client_id)

    """
    --------
    Billomat Client Properties
    --------

    --------
    Searching
    --------
    Parameter	        Description
    client_id	        ID of a client
    client_property_id	ID of an attribute
    value	            Value of an attribute

    --------
    Creating
    --------
    element	            Description	            Type	    Default value	Mandatory
    client_id	        ID of the client	    INT		                    yes
    client_property_id	ID of the property	    INT		                    yes
    value	            Property value	        ALNUM		                yes
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
        return self._iterate_through_pages(self.get_client_properties_per_page, 'client-property-value', params=params)

    def get_client_property(self, client_property_id):
        """
        Get a client property by the billomat id of a client property
        :param client_propery_id: the billomat id
        :return: the found client property dict
        """
        return self._create_get_request(resource='client-property-values', billomat_id=client_property_id)

    def create_client_property(self, client_property_dict):
        """
        Sets a client property
        :param client_property_dict: the client property
        :return:
        """
        return self._create_post_request(resource='client-property-values', send_data=client_property_dict)

    """
    --------
    Billomat Client Tags
    --------

    --------
    Searching
    --------
    Parameter	        Description
    client_id           ID of a client

    --------
    Creating
    --------
    element	    Description	        Type	Default value	Mandatory
    client_id	ID of the client	INT		                yes
    name	    Tag	                ALNUM		            yes
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
        return self._iterate_through_pages(self.get_client_tags_per_page, 'client-tags', params=params)

    def get_client_tag(self, client_tag_id):
        """
        Get a specific client tag by the billomat id
        :param client_tag_id: billomat id of the client tag
        :return: the specific client tag
        """
        return self._create_get_request(resource='client-tags', billomat_id=client_tag_id)

    def create_client_tag(self, client_tag_dict):
        """
        Creates a client atg
        :param client_tag_dict:
        :return:
        """
        return self._create_post_request(resource='client-tags', send_data=client_tag_dict)

    def delete_client_tag(self, client_tag_id):
        """
        Delete a specific client tag by the client tag id
        :param client_tag_id: the billomat id
        :return: Response Object
        """
        return self._create_delete_request(resource='client-tags', billomat_id=client_tag_id)

    """
    --------
    Billomat Client Contacts
    --------

    --------
    Retrieving
    --------
    You can only get contacts of a client therefore the client_id has to be given in the request

    --------
    Creating
    --------
    element	        Description	                                Type	Default value	Mandatory
    client_id	    ID of the client	                        INT		                yes
    label	        Label	                                    ALNUM
    name	        Company name	                            ALNUM
    street	        Street	                                    ALNUM
    zip	            Zip code	                                ALNUM
    city	        City	                                    ALNUM
    state	        State, county, district, region             ALNUM
    country_code	Country	Country code as ISO 3166            Alpha-2
    first_name	    First name	                                ALNUM
    last_name	    Last name	                                ALNUM
    salutation	    Salutation	                                ALNUM
    phone	        Phone	                                    ALNUM
    fax	            Fax	                                        ALNUM
    mobile	        Mobile Number	                            ALNUM
    email	        Email	                                    EMAIL
    www	            Website	                                    URL
                                                                (w/o http)
    """

    def get_contacts_of_client_per_page(self, client_id, per_page=1000, page=1, params=None):
        if not params:
            params = {'client_id': client_id}

        return self._get_resource_per_page(
            resource='contacts',
            per_page=per_page,
            page=page,
            params=params,
        )

    def get_all_contacts_of_client(self, client_id):
        return self._iterate_through_pages(
            get_function=self.get_contacts_of_client_per_page,
            data_key='contact',
            **{'client_id': client_id}
        )

    def get_contact_of_client(self, contact_id):
        return self._create_get_request('contacts', contact_id)

    def create_contact_of_client(self, contact_dict):
        return self._create_post_request(resource='contacts', send_data=contact_dict)

    def update_contact_of_client(self, contact_dict):
        return self._create_put_request(resource='contacts', send_data=contact_dict)

    def delete_contact_of_client(self, client_id):
        return self._create_delete_request(resource='contacts', billomat_id=client_id)
