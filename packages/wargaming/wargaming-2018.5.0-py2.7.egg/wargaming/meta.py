import os
import json
import requests
import six
from retrying import retry
from datetime import datetime
from bs4 import BeautifulSoup

from wargaming.exceptions import RequestError, ValidationError
from wargaming.settings import (
    ALLOWED_GAMES,
    ALLOWED_REGIONS,
    HTTP_USER_AGENT_HEADER,
    RETRY_COUNT,
    GAME_API_ENDPOINTS,
    REGION_TLD_MAP,
)
from wargaming import parser


def check_allowed_game(game):
    if game not in ALLOWED_GAMES:
        raise ValidationError("Game '%s' is not in allowed list: %s" %
                              (game, ', '.join(ALLOWED_GAMES)))


def check_allowed_region(region):
    if region not in ALLOWED_REGIONS:
        raise ValidationError("Region %s is not in allowed list: %s" %
                              (region, ', '.join(ALLOWED_REGIONS)))


def region_url(region, game):
    check_allowed_game(game)
    check_allowed_region(region)

    # all api calls for all project goes to api.worldoftanks.*
    # maybe WG would move this api to api.wargaming.net
    return GAME_API_ENDPOINTS[game].format(region=REGION_TLD_MAP.get(region, region))


@six.python_2_unicode_compatible
class WGAPI(object):
    """Result from WG API request"""

    def __init__(self, url, http_method='GET', parser=None, stop_max_attempt_number=RETRY_COUNT, **kwargs):
        self.url = url
        for name, value in kwargs.items():
            if isinstance(value, list) or isinstance(value, tuple):
                kwargs[name] = ','.join(str(i) for i in value)
            elif isinstance(value, datetime):
                kwargs[name] = value.isoformat()
        self.parser = parser
        self.params = kwargs
        self.http_method = http_method
        self._data = None
        self.error = None

        # Retry only if SOURCE_NOT_AVAILABLE error
        self._fetch_data = retry(
            stop_max_attempt_number=stop_max_attempt_number,
            retry_on_exception=lambda ex: isinstance(ex, RequestError) and ex.code == 504
        )(self._fetch_data)

    def _fetch_data(self):
        # method can be GET/POST
        if self.http_method == 'GET':
            response = requests.get(self.url, params=self.params, headers={
                'User-Agent': HTTP_USER_AGENT_HEADER,
            })
        elif self.http_method == 'POST':
            response = requests.post(self.url, data=self.params, headers={
                'User-Agent': HTTP_USER_AGENT_HEADER,
            })
        else:
            raise RequestError('Unknown HTTP method %s' % self.http_method)

        try:
            data = response.json()
        except requests.exceptions.ContentDecodingError:
            raise RequestError('Unable to decode json')

        if data.get('status', '') == 'error':
            self.error = data['error']
            raise RequestError(**self.error)

        data = data.get('data', data)
        if self.parser:
            data = self.parser.parse_response_data(data)
        return data

    @property
    def data(self):
        if not self._data:
            self._data = self._fetch_data()
        return self._data

    @data.setter
    def data(self, value):
        """setter is used if needed to fake response or reset data"""
        self._data = value

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def __getitem__(self, item):
        """__getitem__ with smart type detection
        would try to lookup data['123']
        if not found would try data[123] and vise versa
        """
        data = self.data
        try:
            return data[item]
        except KeyError:
            item = int(item) if type(item) == str and item.isdigit() else str(item)
            return data[item]

    def __repr__(self):
        res = str(self.data)
        return res[0:200] + ('...' if len(res) > 200 else '')


class PaginatedWGAPI(WGAPI):
    def __init__(self, *args, **kwargs):
        super(PaginatedWGAPI, self).__init__(*args, **kwargs)
        self.params['page_no'] = int(self.params.get('page_no', 1))
        self._data = []
        self._iter = iter(self._data)
        self._fetch_next = True

    def _fetch_next_data(self):
        data = self._fetch_data()
        self._data.extend(data)
        self.params['page_no'] += 1  # set next page_no
        self._fetch_next = False

    def __iter__(self):
        return self

    def next(self):
        if self._fetch_next:
            self._fetch_next_data()
        value = next(self._iter)
        if value == self._data[-1]:
            self._fetch_next = True
        return value

    def __len__(self):
        raise TypeError("WGAPI paginated objects has no len()")

    @property
    def data(self):
        return self._data


class ModuleAPI(object):
    _module_dict = {}

    def __init__(self, application_id, language, base_url, enable_parser):
        """
        :param application_id: WG application id
        :param language: default language param
        :param base_url: base url of module api
        """
        self.application_id = application_id
        self.language = language
        self.base_url = base_url
        self._enable_parser = enable_parser


class BaseAPI(object):
    _module_dict = {}

    def __init__(self, application_id, language, region, enable_parser=False):
        """
        :param application_id: WG application id
        :param language: default language param
        :param region: game geo region short name
        """
        self.application_id = application_id
        self.language = language
        self.region = region
        self.base_url = region_url(region, self.__class__.__name__.lower())
        self._enable_parser = enable_parser
        for k, v in self._module_dict.items():
            setattr(self, k, v(application_id, language, self.base_url, enable_parser))

    def __repr__(self):
        return str("<%s at %s, language=%s>" % (self.__class__.__name__, self.base_url, self.language))


class MetaAPI(type):
    """MetaClass Loads current scheme from schema.json file
    and creates API structure based on scheme.

    Scheme format:
    {'module_name': {                         # account, globalmap, etc
        'function_name': {                    # list, provinces, etc
            '__doc__': description,           # text description
            'parameter': 'type of parameter'  # allowed parameters
        }
    }}
    """

    def __new__(mcs, name, bases, attrs):
        cls = super(MetaAPI, mcs).__new__(mcs, name, bases, attrs)
        cls._module_dict = {}

        def make_api_call(call_schema):
            """
            API function generator (list, info, etc.)
            :param call_schema:  allowed fields
            :return: api call function
            """
            url = call_schema['url']
            if not url.endswith('/'):
                url += '/'

            default_http_method = call_schema['allowed_http_methods'][0]

            parameters = {
                parameter['name']: parameter
                for parameter in call_schema['parameters']
            }

            fields_parser = parser.Parser(call_schema.get('fields', []))

            def api_call(self, http_method=default_http_method, **kwargs):
                """API call to WG public API
                :param self: instance of sub module
                :param kwargs: params to WG public API
                :return: WGAPI instance
                """
                # enable infinite pagination if page_no is in parameters
                all_pages = 'page_no' in parameters and kwargs.pop('all_pages', False)

                # check that specified http_method is in allowed_http_methods
                if http_method not in call_schema['allowed_http_methods']:
                    raise ValidationError('Wrong http_method: %s. Possible values: %s.' % (
                        http_method, ', '.merge(call_schema['allowed_http_methods'])))

                for field, value in kwargs.items():
                    if field not in parameters:
                        # this make available such calls wot.account.info(account=accounts)
                        # instead if wot.account.info(account_id=[i['account_id'] for i in accounts])
                        field_id = field + '_id'
                        value = value.data if isinstance(value, WGAPI) else value
                        if field_id in parameters and isinstance(value, dict) and field_id in value:
                            kwargs[field_id] = value[field_id]
                            del kwargs[field]
                        elif field_id in parameters and isinstance(value, list) and \
                                isinstance(value[0], dict) and field_id in value[0]:
                            kwargs[field_id] = [i[field_id] for i in value]
                            del kwargs[field]
                        else:
                            raise ValidationError('Wrong parameter: {0}'.format(field))

                if 'language' not in kwargs:
                    kwargs['language'] = self.language

                if 'application_id' not in kwargs:
                    kwargs['application_id'] = self.application_id

                for field, params in parameters.items():
                    if params.get('required') and field not in kwargs:
                        raise ValidationError('Missing required parameter : {0}'.format(field))

                # set parameters in kwargs to pass with API arguments to the WGAPI class
                kwargs['parser'] = fields_parser if self._enable_parser else None
                kwargs['http_method'] = http_method

                if all_pages:
                    return PaginatedWGAPI(self.base_url + url, **kwargs)
                else:
                    return WGAPI(self.base_url + url, **kwargs)

            # BeautifulSoup is used because of HTML in description field
            doc = BeautifulSoup(call_schema['description'], "html.parser").get_text()
            doc += "\n\nKeyword arguments:\n"
            for field in call_schema['parameters']:
                doc += "%-20s  doc:      %s\n" % (
                    field['name'], BeautifulSoup(field['description'], "html.parser").get_text())
                doc += "%-20s  required: %s\n" % ('', field.get('required', False))
                doc += "%-20s  type:     %s\n\n" % ('', field['type'])
            api_call.__doc__ = doc
            api_call.__name__ = str(url.split('/')[-1])
            api_call.__module__ = str(url.split('/')[0])
            return api_call

        # check if values are correct
        check_allowed_game(name.lower())

        # Loading schema from file
        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schema')
        source_file = os.path.join(base_dir, '%s-schema.json' % name.lower())
        schema = json.load(open(source_file))

        # Creating objects for class
        for obj_name, obj in schema.items():
            # make object name
            obj_full_name = "%s.%s" % (name, obj_name)
            # save module to _module_dict for initialization on class creation
            cls._module_dict[obj_name] = module_obj = type(str(obj_full_name), (ModuleAPI, ), {})

            # make this work without class initialization
            setattr(cls, obj_name, module_obj)

            for func_name, api_call_schema in obj.items():
                setattr(module_obj, func_name, make_api_call(api_call_schema))

        return cls
