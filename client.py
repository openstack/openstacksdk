class OpenStackClient(object):
    def __init__(self, auth):
        self._transport = auth.connect()
        self._auth = auth

    @property
    def compute(self):
        return ComputeClient(self._transport)

    @property
    def object_storage(self):
        return ObjectStorageClient(self._transport)
