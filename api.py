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

    --------
    Searching
    --------
    Parameter	        Description
    name	            Company name
    email	            e-mail address
    first_name	        First name of the contact person
    last_name	        Last name of the contact person
    country_code	    Country code as ISO 3166 Alpha-2
    creditor_identifier	SEPA creditor identifier
    note	            Note
    client_number	    Client number you may have at this supplier.
    incoming_id	        ID of an incoming of this supplier, multiple values seperated with commas
    tags	            Comma seperated list of tags

    --------
    Creating
    --------
    element	            Description	                                Type	    Default value	        Mandatory
    name	            Company name	                            ALNUM
    street	            Street	                                    ALNUM
    zip	                Zip code	                                ALNUM
    city	            City	                                    ALNUM
    state	            State, county, district, region	            ALNUM
    country_code	    Land	Country code as ISO 3166            Alpha-2	    Value from settings
    first_name	        First name	                                ALNUM
    last_name	        Last name	                                ALNUM
    salutation	        Salutation	                                ALNUM
    phone	            Phone	                                    ALNUM
    fax	                Fax	                                        ALNUM
    mobile	            mobile number	                            ALNUM
    email	            Email	                                    EMAIL
    www	                Website	                                    URL
                                                                    (w/o http)
    tax_number	        Tax number	                                ALNUM
    vat_number	        VAT number	valid                           VAT number
    creditor_identifier	SEPA creditor identifier	                valid creditor
                                                                    identifier
    bank_account_number	Kontonummer	                                ALNUM
    bank_account_owner	Bank account number	                        ALNUM
    bank_number     	Bank identifier code	                    ALNUM
    bank_name	        Bank name	                                ALNUM
    bank_swift	        SWIFT/BIC	                                ALNUM
    bank_iban	        IBAN	                                    valid IBAN
    note	            Note	                                    ALNUM
    client_number	    Client number you may have at this supplier ALNUM
    currency_code	    The currency for this client.
                        If this field is empty,
                        the account currency is used.	            ISO currency code
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

    --------
    Searching
    --------
    Parameter	            Description
    supplier_id	            ID of a supplier
    supplier_property_id	ID of an attribute
    value	                Value of an attribute

    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    supplier_id	            ID of the supplier	                        INT		                            yes
    supplier_property_id	ID of the property	                        INT		                            yes
    value	                Property value	                            ALNUM		                        yes
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

    --------
    Retrieving
    --------
    You can only retrieve tags of a supplier therefore you have to give the supplier_id every request

    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    supplier_id	            ID of the supplier	                        INT		                            yes
    name	                Tag	                                        ALNUM		                        yes
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

    --------
    Searching
    --------
    Parameter	    Description
    article_number	Article number
    title	        Title
    description	    Description
    currency_code	ISO code of the currency
    unit_id	        ID of the chosen unit
    tags	        Comma seperated list of tags
    supplier_id	    ID of the chosen supplier

    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    number_pre	            Prefix	                                    ALNUM	    Value from settings
    number	                Sequential number	                        INT	        next free number
    number_length	        Minimum length of the customer number
                            (to be filled with leading zeros)	        INT	        Value from settings
    title	                Title	                                    ALN         Empty string
    description	            Description	                                ALNUM	    Empty string
    sales_price	            Price	                                    FLOAT	    0.0
    sales_price2	        Price for clients which are members
                            of pricegroup 2. The normal price
                            is used if no price is defined.	            FLOAT
    sales_price3	        Price for clients which are members
                            of pricegroup 3. The normal price
                            is used if no price is defined.	            FLOAT
    sales_price4	        Price for clients which are members
                            of pricegroup 4. The normal price
                            is used if no price is defined.	            FLOAT
    sales_price5	        Price for clients which are members
                            of pricegroup 5. The normal price
                            is used if no price is defined.	            FLOAT
    currency_code	        Currency	                                ISO
                                                                        currency codeDefault currency from settings
    unit_id	                ID of the chosen unit	                    INT	        null
    tax_id	                ID of the chosen tax rate	                INT	        null
    purchase_price	        Purchase price	                            FLOAT	    null
    purchase_price_net_grossPrice basis of purchase price
                            (gross or net prices)	                    ALNUM
                                                                        ("NET",
                                                                        "GROSS")	NET
    supplier_id	            ID of the chosen supplier	                INT	        null
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

    --------
    Searching
    --------
    Parameter	            Description
    article_id	            ID of an article
    article_property_id	    ID of an attribute
    value	                Value of an attribute
    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    article_id	            ID of the article	                        INT		                            yes
    article_property_id	    ID of the property	                        INT		                            yes
    value	                Value of the property	                    ALNUM		                        yes
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

    --------
    Retrieving
    --------
    You can only retrieve tags of an article therefore you have to give the article_id every request

    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    article_id 	            ID of the article	                        INT		                            yes
    name	                Tag	                                        ALNUM		                        yes
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

    --------
    Searching
    --------
    Parameter	        Description
    name	            Name of the unit

    --------
    Creating
    --------
    element	            Description	                                Type	    Default value	        Mandatory
    name	            Name of the unit	                        ALNUM		                        yes
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

    --------
    Searching
    --------
    Parameter	        Description
    client_id	        ID of the client
    contact_id	        ID of the contact
    invoice_number	    invoice number
    status	            Status (DRAFT, OPEN, PAID, OVERDUE, CANCELED).
                        More than one statuses could be given as a comma separated list.
                        Theses statuses will be logically OR-connected.
    payment_type	    Payment Type (eg. CASH, BANK_TRANSFER, PAYPAL, ...).
                        More than one payment type could be given as a comma separated list.
                        Theses payment types will be logically OR-connected.
                        You can find a overview of all payment types at API documentation of payments.
    from	            Only show invoices since this date (format YYYY-MM-DD)
    to	                Only show invoices up to this date (format YYYY-MM-DD)
    label	            Free text search in label text
    intro	            Free text search in introductory text
    note	            Free text search in explanatory notes
    tags	            Comma seperated list of tags
    article_id	        ID of an article

    --------
    Creating
    --------
    element	            Description	                                Type	    Default value	        Mandatory
    client_id	        ID of the client	                        INT		                            yes
    contact_id	        ID of the contact	                        INT
    address	            the address	                                ALNUM	client's address
    number_pre	        invoice number prefix	                    ALNUM	Value taken from the settings
    number	            serial number	                            INT	next free number
    number_length	    Minimum length of the invoice number
                        (to be filled with leading zeros)	        INT	Value taken from the settings
    date	            Invoice date	                            DATE	today
    supply_date	        supply/delivery date	                    MIXED (DATE/ALNUM)
    supply_date_type	type of supply/delivery date	            ALNUM
                                                                    ("SUPPLY_DATE",
                                                                    "DELIVERY_DATE",
                                                                    "SUPPLY_TEXT",
                                                                    "DELIVERY_TEXT")
    due_date	        due date	                                DATE	date + due days taken from the settings
    discount_rate	    Cash discount	                            INT	Value from the settings
    discount_date	    Cash discount date	                        DATE	date + cash discount days taken from the settings
    title	            Title of the document	                    ALNUM
    label	            Label text to describe the project	        ALNUM
    intro	            Introductory text	                        ALNUM	Default value taken from the settings
    note	            Explanatory notes	                        ALNUM	default value taken from the settings
    reduction	        Reduction (absolute or percent: 10/10%)	    ALNUM
    currency_code	    Currency	ISO currency code	            Default currency
    net_gross	        Price basis (gross or net prices)	        ALNUM
                                                                    ("NET",
                                                                    "GROSS")    Default value taken from the settings
    quote	            Currency quote
                        (for conversion into standard currency)	    FLOAT	1.0000
    payment_types	    List (separated by comma)
                        of all accepted payment types.	            FLOAT	Default value taken from the settings
    invoice_id	        The ID of the corrected invoice,
                        if it is an invoice correction.	            INT
    offer_id	        The ID of the estimate,
                        if the invoice was created from an estimate.INT
    confirmation_id	    The ID of the confirmation,
                        if the invoice was created from a confirmation.INT
    recurring_id	    The ID of the recurring,
                        if the invoice was created from a recurring.    INT
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

    --------
    Retrieving
    --------
    You can only get items of an invoice therefore the invoice_id has to be given in the request

    --------
    Creating
    --------
    element	        Description	                                Type	Default value	Mandatory
    invoice_id	    ID of the invoice	                        INT		yes (except for creation of an invoice)
    article_id	    ID of the article, sets additionally
                    the values from the article on creation	    INT
    unit	        Unit	                                    ALNUM
    quantity	    Quantity	                                FLOAT	0.0
    unit_price	    Price per unit	                            FLOAT	0.0
    tax_name	    Name of the tax	                            ALNUM	Default tax rate
    tax_rate	    rate of taxation	                        FLOAT	Default tax rate
    title	        Title	                                    ALNUM
    description	    Description                             	ALNUM
    reduction	    Reduction (absolute or percent: 10/10%)	    ALNUM
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

    --------
    Retrieving
    --------
    You can only get comments of an invoice therefore the invoice_id has to be given in the request

    --------
    Creating
    --------
    element	        Description	                                Type	Default value	Mandatory
    invoice_id	    ID of the invoice	                        INT		                yes
    comment	        Comment text	                            ALNUM		            yes
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

    --------
    Searching
    --------
    Parameter       Description
    invoice_id	    ID of the invoice
    from	        Only payments since this date (format YYYY-MM-DD)
    to	            Only payments up to this date (format YYYY-MM-DD)
    type	        Payment type (eg. CASH, BANK_TRANSFER, PAYPAL, ...).
                    More than one payment type could be given as a comma separated list.
                    Theses payment types will be logically OR-connected.
    user_id	        ID of the user

    --------
    Creating
    --------
    element	                Description	                                Type	Default value	Mandatory
    invoice_id	            ID of the invoice	                        INT		                yes
    date	                Date of payment	                            DATE	today
    amount	                Payed ammount	                            FLOAT	                yes
    comment	                Comment text	                            ALNUM
    type	                Payment type	                            ALNUM
                            ("CREDIT_NOTE", "BANK_CARD", "BANK_TRANSFER",
                            "DEBIT", "CASH", "CHECK", "PAYPAL",
                            "CREDIT_CARD", "COUPON", "MISC")
    mark_invoice_as_paid	Indicates whether the associated invoice
                            should be marked as paid
                            (set status to PAID).	                    BOOL	0 (false)
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

    --------
    Retrieving
    --------
    You can only retrieve tags of an invoice therefore you have to give the invoice_id every request

    --------
    Creating
    --------
    element	                Description	                                Type	    Default value	        Mandatory
    invoice_id 	            ID of the invoice	                        INT		                            yes
    name	                Tag	                                        ALNUM		                        yes
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
