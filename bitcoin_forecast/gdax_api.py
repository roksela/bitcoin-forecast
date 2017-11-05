import requests
import logging
import csv
import os
from datetime import datetime
from operator import itemgetter


class GDAXApi(object):
    """
    GDAX public API client.

    The Market Data API is an unauthenticated set of endpoints for retrieving market data.
    These endpoints provide snapshots of market data.

    """

    API_URL = 'https://api.gdax.com'
    MAX_NUM_DATA_POINTS_PER_PAGE = 200

    def get_products(self):
        """
        Get a list of available currency pairs for trading.

        :return: list of products e.g. BTC-USD
        """
        response = requests.get(self.API_URL + '/products')
        products = response.json()

        logging.getLogger('GDAXApi').debug('products={}'.format(products))
        return [product['id'] for product in products]

    def get_historic_rates(self, product_id, start, end, granularity=60*60):
        """
        Historic rates for a product.

        This method paginates automatically over period from start to end, making sure the maximum
        number of data points is not exceeded.

        :param product_id: product e.g. BTC-USD
        :param start: Start time in ISO 8601
        :param end: End time in ISO 8601
        :param granularity: Desired timeslice in seconds (defaults to 1 hour)
        :return: a list of GDAXRate objects
        """

        periods = self._get_data_point_ranges(start, end, granularity)
        logging.getLogger('GDAXApi').debug('starting pagination | periods={}'.format(periods))

        historic_rates = []
        for range_start, range_end in periods:
            raw_partial_rates = self._get_raw_partial_rates(product_id, range_start, range_end, granularity)
            sorted_raw_partial_rates = sorted(raw_partial_rates, key=itemgetter(0))

            partial_rates = [self._convert_to_rate(raw_rate, granularity) for raw_rate in sorted_raw_partial_rates]
            historic_rates += partial_rates

        return historic_rates

    def _get_data_point_ranges(self, start, end, granularity):
        """
        Divides entire period into smaller time ranges.

        Each time range cannot have more than 200 data points.
        This is limited by GDAX API. See get_candles().

        :param start: Start time in ISO 8601
        :param end: End time in ISO 8601
        :param granularity: Desired timeslice in seconds
        :return: 2 lists: a list of start dates, a list of end dates (according to current API limitations)
        """
        start_timestamp = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        end_timestamp = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        page_size = self.MAX_NUM_DATA_POINTS_PER_PAGE * granularity

        page_starts = list(range(int(start_timestamp), int(end_timestamp), page_size))
        # last page can be shorter
        page_ends = [min(page_start + page_size, int(end_timestamp)) for page_start in page_starts]

        page_starts_dates = [datetime.fromtimestamp(page_start).strftime('%Y-%m-%d %H:%M:%S') for page_start in
                             page_starts]
        page_ends_dates = [datetime.fromtimestamp(page_end).strftime('%Y-%m-%d %H:%M:%S') for page_end in
                           page_ends]

        periods = [(start_date, end_date) for start_date, end_date in zip(page_starts_dates, page_ends_dates)]

        return periods

    def _get_raw_partial_rates(self, product_id, start, end, granularity):
        """
        Historic rates for a product. Rates are returned in grouped buckets based on requested granularity.

        The maximum number of data points for a single request is 200 candles.
        If your selection of start/end time and granularity will result in more
        than 200 data points, your request will be rejected.

        If you wish to retrieve fine granularity data over a larger time range,
        you will need to make multiple requests with new start/end ranges.

        :param product_id: product e.g. BTC-USD
        :param start: Start time in ISO 8601
        :param end: End time in ISO 8601
        :param granularity: Desired timeslice in seconds
        :return: list of rates in format [[time, low, high, open, close, volume],...]
        """
        params = {'start': start, 'end': end, 'granularity': granularity}
        logging.getLogger('GDAXApi').debug('_get_raw_partial_rates | start={}, end={}, granularity={}'.format(start, end, granularity))

        response = requests.get('{}/products/{}/candles'.format(self.API_URL, product_id), params=params)
        raw_partial_rates = response.json()

        logging.getLogger('GDAXApi').debug('response code: {}'.format(response.status_code))
        logging.getLogger('GDAXApi').debug('raw_partial_rates.count={}'.format(len(raw_partial_rates)))
        logging.getLogger('GDAXApi').debug('raw_partial_rates={}'.format(raw_partial_rates))

        if response.status_code != 200:
            logging.getLogger('GDAXApi').error('error code: {}'.format(response.status_code))
            if 'message' in raw_partial_rates:
                logging.getLogger('GDAXApi').error('error message: {}'.format(raw_partial_rates.message))

        return raw_partial_rates

    def _convert_to_rate(self, raw_rate, granularity):
        """
        Converts raw rate to proper transfer object.

        :param raw_rate: a list in format [ time, low, high, open, close, volume ]
        :param granularity: Desired timeslice in seconds
        :return: GDAXRate object
        """
        return GDAXRate(raw_rate[0], raw_rate[0] + granularity,
                        raw_rate[1], raw_rate[2], raw_rate[3], raw_rate[4], raw_rate[5])


class GDAXRate(object):
    """
    Transfer object for retrieving rates from GDAX public API.
    """

    def __init__(self, start_time, end_time, lowest_price, highest_price, opening_price, closing_price,
                 volume_of_trading):
        self.start_time = datetime.utcfromtimestamp(start_time)
        self.end_time = datetime.utcfromtimestamp(end_time)
        self.lowest_price = lowest_price
        self.highest_price = highest_price
        self.opening_price = opening_price
        self.closing_price = closing_price
        self.volume_of_trading = volume_of_trading

    def __repr__(self):
        return "<GDAXRate %s>" % self.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def get_field_names():
        return ['start_time', 'end_time', 'lowest_price', 'highest_price',
                'opening_price', 'closing_price', 'volume_of_trading']


class GDAXRateLog(object):
    """
    CSV Log File for storing historical rates.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def append(self, gdax_rates):
        """
        Append rates to the CSV log. File is created if it doesn't exist.

        :param gdax_rates: a list of GDAXRate objects
        """
        is_existing_file = os.path.isfile(self.file_path)
        field_names = GDAXRate.get_field_names()

        mode = 'a' if is_existing_file else 'w'

        with open(self.file_path, mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            if not is_existing_file:
                writer.writeheader()
            for rate in gdax_rates:
                writer.writerow(rate.__dict__)
