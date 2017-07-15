import unittest
from bitcoin_forecast import GDAXApi


class TestGDAXApi(unittest.TestCase):

    def test_get_products(self):
        api = GDAXApi()
        products = api.get_products()
        print(products)

if __name__ == '__main__':
    unittest.main()
