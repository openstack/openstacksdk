class KeystoneAuth(object):
    def __init__(self, authurl, username, password):
        self._authurl = authurl
        self._username = username
        self._password = password

    def connect(self):
        return KeystoneTransport(self)


class KeystoneTransport(object):
    def __init__(self, auth_info):
        # Set ourselves up:
        # * Open HTTP session
        # * Get a token
        # * Configure session to raise on HTTP error
        self.auth_info = auth_info

    def make_http_request(method):
        def inner(self, *args, **kwargs):
            # get_session() will make sure that the token is valid.
            return self.get_session().request(method, *args, **kwargs)
        return inner

    get = make_http_request("GET")
    post = make_http_request("POST")
    patch = make_http_request("PATCH")
    delete = make_http_request("DELETE")



# In reality this would not live inside the main package because it would be
# vendor agnostic, but for the purpose of demonstrating that other auth
# strategies work fine, it goes here.
class RackspaceAuth(object):
    def __init__(self, username, api_key):
        self._username = username
        self._api_key = api_key

    def connect(self):
        # ...
