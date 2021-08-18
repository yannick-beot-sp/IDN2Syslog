from dotenv.main import set_key
from requests.exceptions import HTTPError
from requests_toolbelt import sessions
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from Helper import Helper


class IDNClient(object):
    def __init__(self, tenant: str, client_id: str, client_secret: str, helper: Helper, proxy_uri=None):
        self.tenant = tenant
        self.client_id = client_id
        self.client_secret = client_secret
        self.helper = helper
        self.http = sessions.BaseUrlSession(
            'https://{}.api.identitynow.com/'.format(tenant))
        self.requests_proxy = None
        if proxy_uri:
            self.requests_proxy = {'http': proxy_uri, 'https': proxy_uri}
        self._init_request_session()

    def send_http_request(self, url, method, parameters=None, payload=None, headers=None, cookies=None, verify=True,
                          cert=None, timeout=None):

        # connect and read timeouts in tuple
        requests_args = {'timeout': (5.0, 25.0), 'verify': verify}
        if parameters:
            requests_args['params'] = parameters
        if payload:
            if isinstance(payload, (dict, list)):
                requests_args['json'] = payload
            else:
                requests_args['data'] = str(payload)
        if headers:
            requests_args['headers'] = headers
        if cookies:
            requests_args['cookies'] = cookies
        if cert:
            requests_args['cert'] = cert
        if timeout is not None:
            requests_args['timeout'] = timeout

        if self.requests_proxy:
            requests_args['proxies'] = self.requests_proxy

        req = self.http.request(method, url, **requests_args)
        return req

    def _init_request_session(self):

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

    def get_access_token(self):

        tokenparams = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        token_url = "/oauth/token"

        access_token = ""

        token_response = self.send_http_request(
            token_url, "POST", parameters=tokenparams, payload=None, headers=None, cookies=None, verify=True, cert=None, timeout=None)

        if token_response is not None:
            try:
                token_response.raise_for_status()

                access_token = token_response.json()["access_token"]
                return access_token
            except HTTPError as http_err:
                self.helper.log_error("Error getting token: " +
                                      str(token_response.status_code))
                return 0
            except KeyError:
                self.helper.log_error("Access token not granted...")
            except ValueError:
                self.helper.log_error("No json response received...")

    def search(self, query, query_type="SAILPOINT", sort=["created"], indices=["events"], timezone="UTC"):
        self.helper.log_debug(">IDNClient.search query={}".format(query))
        limit = 250
        offset = 0
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.get_access_token()
        }

        searchpayload = {
            "indices": indices,
            "queryType": query_type,
            "query": {
                "query": query,
                "timeZone": timezone
            },
            "queryResultFilter": {},
            "sort": sort,
            "searchAfter": []
        }

        audit_url = "/v3/search"
        count = "true"
        x_total_count = -1
        while True:

            queryparams = {
                "count": count,
                "offset": offset,
                "limit": limit
            }

            # Initiate request
            response = self.send_http_request(audit_url, "POST", parameters=queryparams, payload=searchpayload,
                                              headers=headers, cookies=None, verify=True, cert=None, timeout=None)
            if count == "true":
                x_total_count = int(response.headers['x-total-count'])
                self.helper.log_debug("Found {} result".format(x_total_count))
                count = "false"

            if x_total_count > 0 and (results := response.json()) is not None:
                try:
                    yield from results
                    if offset + limit < x_total_count:
                        offset += limit
                    else:
                        break
                except KeyError:
                    self.helper.log_error("Response does not contain items")
                    break
            else:
                # Nothing more. Quit
                break
