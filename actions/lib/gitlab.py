from st2common.runners.base_action import Action

# silence SSL warnings
try:
    import requests
    requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member
except ImportError:
    pass

try:
    from urllib.parse import quote_plus
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    from urllib import quote_plus


def override_token(func):
    def wrap(*args, **kwargs):
        header = kwargs.get('headers')
        if header['PRIVATE-TOKEN'] != kwargs.get('token'):
            header['PRIVATE-TOKEN'] = kwargs.get('token')
        return func(*args, **kwargs)
    return wrap


class RequestsMethod(object):

    @staticmethod
    def method(method, url, verify_ssl=False, headers=None, params=None):
        methods = {'get': requests.get,
                   'post': requests.post}

        if not params:
            params = dict()

        requests_method = methods.get(method)
        response = requests_method(
            url, headers=headers, params=params, verify=verify_ssl)

        if response.status_code:
            return response.json()

        return response.text


class GitlabRestClient(Action):

    def __init__(self, config):
        super(GitlabRestClient, self).__init__(config=config)
        self._api_ext = 'api/v4'
        self.url = self.config.get('url')
        self.token = self.config.get('token')
        self.verify_ssl = self.config.get('verify_ssl')

        self._headers = {'PRIVATE-TOKEN': self.token,
                         'Accept': 'application/json',
                         'Content-Type': 'application/json'}

    @override_token
    def _get(self, url, endpoint, headers, params=None, *args, **kwargs):
        api_url = '/'.join((url, self._api_ext, endpoint))
        return RequestsMethod.method('get', api_url, self.verify_ssl, headers, params)

    @override_token
    def _post(self, url, endpoint, headers, params=None, *args, **kwargs):
        api_url = '/'.join((url, self._api_ext, endpoint))
        return RequestsMethod.method('post', api_url, self.verify_ssl, headers, params)

    def get(self, *args, **kwargs):
        return self._get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._post(*args, **kwargs)


class GitlabProjectsAPI(GitlabRestClient):

    def __init__(self, config):
        super(GitlabProjectsAPI, self).__init__(config=config)
        self._api_endpoint = 'projects'

    def get(self, url, endpoint, **kwargs):
        real_endpoint = "{0}/{1}".format(self._api_endpoint,
                                         quote_plus(endpoint))
        return self._get(url, real_endpoint, token=self.token, headers=self._headers, **kwargs)


class GitlabIssuesAPI(GitlabRestClient):

    def __init__(self, config):
        super(GitlabIssuesAPI, self).__init__(config=config)
        self._api_endpoint = 'projects'
        self._api_sub_endpoint = 'issues'

    def get(self, url, endpoint, issue_id, **kwargs):
        real_endpoint = "{0}/{1}/{2}/{3}".format(
            self._api_endpoint, quote_plus(endpoint), self._api_sub_endpoint, issue_id)
        return self._get(url, real_endpoint, token=self.token, headers=self._headers, **kwargs)


class GitlabPipelineAPI(GitlabRestClient):

    def __init__(self, config):
        super(GitlabPipelineAPI, self).__init__(config=config)
        self._api_endpoint = 'projects'

    def get(self, url, endpoint, *args, **kwargs):
        real_endpoint = "{0}/{1}/pipelines".format(
            self._api_endpoint, quote_plus(endpoint))
        return self._get(url, real_endpoint, token=self.token, headers=self._headers, **kwargs)

    def post(self, url, project, ref, trigger_token, variables, *args, **kwargs):
        real_endpoint = "{0}/{1}/trigger/pipeline".format(
            self._api_endpoint, quote_plus(project))

        params = {"token": trigger_token,
                  "ref": ref}
        if variables:
            for key, val in variables.items():
                params.update({"variables[{}]".format(key): val})

        return self._post(url,
                          real_endpoint,
                          token=self.token,
                          headers=self._headers,
                          params=params,
                          **kwargs)
