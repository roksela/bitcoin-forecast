import unittest
import logging
import sys
import csv
import os
from bitcoin_forecast import GDAXApi, GDAXRate, GDAXRateLog
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

    RATE_LOG_HOURLY_FILE_PATH_1 = 'test_rate_log_2017_05_hourly_1.csv'
    RATE_LOG_HOURLY_FILE_PATH_2 = 'test_rate_log_2017_06_hourly_2.csv'
    LOG_HEADERS = ['start_time', 'end_time', 'lowest_price', 'highest_price',
                   'opening_price', 'closing_price', 'volume_of_trading']
    RATE_LOG_DAILY_FILE_PATH = 'test_rate_log_2017_05_daily.csv'

    EXISTING_RATE_LOG_FILE_PATH = '../bitcoin_forecast/resources/test_rate_log_2017_sep.csv'

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                            level=logging.DEBUG, stream=sys.stdout)

    @classmethod
    def tearDownClass(cls):
        # clean after failed tests
        if os.path.isfile(TestGDAXApi.RATE_LOG_HOURLY_FILE_PATH_1):
            os.remove(TestGDAXApi.RATE_LOG_HOURLY_FILE_PATH_1)
        if os.path.isfile(TestGDAXApi.RATE_LOG_HOURLY_FILE_PATH_2):
            os.remove(TestGDAXApi.RATE_LOG_HOURLY_FILE_PATH_2)
        if os.path.isfile(TestGDAXApi.RATE_LOG_DAILY_FILE_PATH):
            os.remove(TestGDAXApi.RATE_LOG_DAILY_FILE_PATH)

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

    def test_gdax_rate_log_create(self):
        product_id = 'BTC-USD'
        start = '2017-05-01T00:00:00.000Z'
        end = '2017-06-01T00:00:00.000Z'
        granularity = 60 * 60
        num_of_periods = 31 * 24

        api = GDAXApi()
        rates = api.get_historic_rates(product_id, start, end, granularity)

        log = GDAXRateLog(self.RATE_LOG_HOURLY_FILE_PATH_1)
        log.append(rates)

        with open(self.RATE_LOG_HOURLY_FILE_PATH_1, "r") as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            row_count = sum(1 for row in csv_file)

        self.assertListEqual(headers, self.LOG_HEADERS)
        self.assertEqual(num_of_periods, row_count)

        os.remove(self.RATE_LOG_HOURLY_FILE_PATH_1)

    def test_gdax_rate_log_append(self):
        product_id = 'BTC-USD'
        start = '2017-06-01T00:00:00.000Z'
        end = '2017-07-01T00:00:00.000Z'
        granularity = 60 * 60
        num_of_periods = 30 * 24

        api = GDAXApi()
        rates = api.get_historic_rates(product_id, start, end, granularity)

        log = GDAXRateLog(self.RATE_LOG_HOURLY_FILE_PATH_2)
        log.append(rates)
        log.append(rates)

        with open(self.RATE_LOG_HOURLY_FILE_PATH_2, "r") as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            row_count = sum(1 for row in csv_file)

        self.assertListEqual(headers, self.LOG_HEADERS)
        self.assertEqual(2 * num_of_periods, row_count)

        os.remove(self.RATE_LOG_HOURLY_FILE_PATH_2)

    def test_gdax_rate_log_daily(self):
        product_id = 'BTC-USD'
        start = '2017-05-01T00:00:00.000Z'
        end = '2017-06-01T00:00:00.000Z'
        granularity = 60 * 60 * 24
        num_of_periods = 31

        api = GDAXApi()
        rates = api.get_historic_rates(product_id, start, end, granularity)

        log = GDAXRateLog(self.RATE_LOG_DAILY_FILE_PATH)
        log.append(rates)

        with open(self.RATE_LOG_DAILY_FILE_PATH, "r") as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            row_count = sum(1 for row in csv_file)

        self.assertListEqual(headers, self.LOG_HEADERS)
        self.assertEqual(num_of_periods, row_count)

        os.remove(self.RATE_LOG_DAILY_FILE_PATH)

    def test_read_gdax_tate_log(self):
        num_of_periods = 694

        log = GDAXRateLog(self.EXISTING_RATE_LOG_FILE_PATH)
        rates = log.read()

        self.assertEqual(num_of_periods, len(rates))

        # 2017-09-01 00:00:00,2017-09-01 01:00:00,4743.93,4765.49,4743.94,4765.49,532.0765854100013
        rate_begin = GDAXRate('2017-09-01 00:00:00', '2017-09-01 01:00:00',
                              4743.93, 4765.49, 4743.94, 4765.49, 532.0765854100013)

        self.assertEqual(rate_begin, rates[0])

        # 2017-09-29 23:00:00,2017-09-30 00:00:00,4135,4160.72,4160.03,4156.99,263.30476701999953
        rate_end = GDAXRate('2017-09-29 23:00:00', '2017-09-30 00:00:00',
                            4135, 4160.72, 4160.03, 4156.99, 263.30476701999953)

        self.assertEqual(rate_end, rates[693])

if __name__ == '__main__':
    unittest.main()
