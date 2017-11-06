import unittest
import logging
import sys
from bitcoin_forecast import GDAXRateLog, BTCForecast, GDAXRate
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class TestBTCForecast(unittest.TestCase):

    EXISTING_RATE_LOG_FILE_PATH = '../bitcoin_forecast/resources/test_rate_log_2017_sep.csv'

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                            level=logging.DEBUG, stream=sys.stdout)

        log = GDAXRateLog(TestBTCForecast.EXISTING_RATE_LOG_FILE_PATH)
        TestBTCForecast.rates = log.read()

        # use 90% of rates to train the model
        row = int(round(0.9 * len(TestBTCForecast.rates)))
        TestBTCForecast.rates_train = TestBTCForecast.rates[:row]
        TestBTCForecast.rates_test = TestBTCForecast.rates[row:]

    @classmethod
    def tearDownClass(cls):
        pass

    def test_setup(self):
        self.assertEqual(694, len(TestBTCForecast.rates))
        self.assertEqual(625, len(TestBTCForecast.rates_train))
        self.assertEqual(69, len(TestBTCForecast.rates_test))

        forecast = BTCForecast('SVR')
        # forecast.learn(TestBTCForecast.rates_train)
        self.assertFalse(forecast.has_learned)

    def test_predict_without_learn(self):
        forecast = BTCForecast('SVR')

        with self.assertRaises(TypeError):
            forecast.predict()

    def test_learn(self):
        forecast = BTCForecast()
        score = forecast.learn(TestBTCForecast.rates_train)

        # we expect accuracy over 90%
        self.assertGreater(score, 0.9)

        # learning set values shouldn't be modified
        log = GDAXRateLog(TestBTCForecast.EXISTING_RATE_LOG_FILE_PATH)
        fresh_rates = log.read()
        self.assertListEqual(fresh_rates, TestBTCForecast.rates)

    def test_predict(self):
        forecast = BTCForecast()
        score = forecast.learn(TestBTCForecast.rates_train)

        timestamps = GDAXRate.to_timestamps(TestBTCForecast.rates_train)
        result = forecast.predict(timestamps)

        self.assertEqual(625, len(result))

        simple_rates = GDAXRate.to_prices(TestBTCForecast.rates_train)

        logging.getLogger('TestBTCForecast').debug('result: {}'.format(result))
        logging.getLogger('TestBTCForecast').debug('actual rates: {}'.format(simple_rates))

        dates = GDAXRate.to_dates(TestBTCForecast.rates_train)
        # TestBTCForecast._plot_simple_rates(dates, simple_rates, result)

    @staticmethod
    def _plot_simple_rates(dates, rates, predicted_rates):
        fig, ax = plt.subplots(nrows=1, sharex=True)
        fig.autofmt_xdate()

        plt.plot(dates, rates, label='rates')
        plt.plot(dates, predicted_rates, label='forecast')

        xfmt = mdates.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)

        plt.legend(loc='upper left')
        plt.show()

if __name__ == '__main__':
    unittest.main()
