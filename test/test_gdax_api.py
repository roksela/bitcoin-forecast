import unittest
from bitcoin_forecast import GDAXApi
from datetime import datetime


class TestGDAXApi(unittest.TestCase):

    PRODUCTS = ['LTC-EUR', 'LTC-BTC', 'BTC-GBP', 'BTC-EUR', 'ETH-EUR', 'ETH-BTC', 'LTC-USD', 'BTC-USD', 'ETH-USD']
    PERIODS = [('2017-05-01 00:00:00', '2017-05-09 08:00:00'), ('2017-05-09 08:00:00', '2017-05-17 16:00:00'),
               ('2017-05-17 16:00:00', '2017-05-26 00:00:00'), ('2017-05-26 00:00:00', '2017-06-01 00:00:00')]

    FIRST_RATE_IN_RANGE = {'start_time': datetime(2017, 5, 1, 0, 0),
                           'end_time': datetime(2017, 5, 1, 1, 0), 'lowest_price': 1370.98,
                           'highest_price': 1397.9, 'opening_price': 1384.55, 'closing_price': 1382.96,
                           'volume_of_trading': 1071.6502117499967}
    LAST_RATE_IN_RANGE = {'start_time': datetime(2017, 5, 31, 23, 0),
                          'end_time': datetime(2017, 6, 1, 0, 0), 'lowest_price': 2295.23,
                          'highest_price': 2316.91, 'opening_price': 2304.06, 'closing_price': 2303.29,
                          'volume_of_trading': 508.03418288999904}

    def test_get_products(self):
        api = GDAXApi()
        products = set(api.get_products())
        self.assertTrue(products.issubset(set(self.PRODUCTS)))

    def test_get_data_point_ranges(self):
        start = '2017-05-01T00:00:00.000Z'
        end = '2017-06-01T00:00:00.000Z'
        granularity = 60 * 60

        api = GDAXApi()
        r = api._get_data_point_ranges(start, end, granularity)
        self.assertListEqual(r, self.PERIODS)

    def test_get_historic_rates(self):
        product_id = 'BTC-USD'
        start = '2017-05-01T00:00:00.000Z'
        end = '2017-06-01T00:00:00.000Z'
        granularity = 60 * 60
        num_of_periods = 31 * 24

        api = GDAXApi()
        rates = api.get_historic_rates(product_id, start, end, granularity)

        self.assertEqual(num_of_periods, len(rates))
        self.assertEqual(self.FIRST_RATE_IN_RANGE, rates[0].__dict__)
        self.assertEqual(self.LAST_RATE_IN_RANGE, rates[num_of_periods - 1].__dict__)


if __name__ == '__main__':
    unittest.main()
