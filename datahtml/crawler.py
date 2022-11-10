import httpx


class HTTP:

    def __init__(self, client=httpx.Client()):
        self.client = client
