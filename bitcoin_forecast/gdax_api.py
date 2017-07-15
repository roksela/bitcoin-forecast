import requests


class GDAXApi(object):
    # TODO: document this class

    API_URL = "https://api.gdax.com"

    def __init__(self):
        pass

    def get_products(self):
        r = requests.get(self.API_URL + '/products')
        return r.json()
