import unittest
import logging
import sys
from bitcoin_forecast import GDAXRateLog, BTCForecast


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

        self.assertGreater(score, 0.9)

if __name__ == '__main__':
    unittest.main()
