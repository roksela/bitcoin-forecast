from bitcoin_forecast import GDAXRate
from sklearn.svm import SVR
from sklearn import preprocessing
from sklearn.pipeline import make_pipeline
import numpy as np
import logging

class BTCForecast(object):
    """
    Forecasting with Machine Learning Techniques.

    Disclaimer:
    This is another just-for-fun project.
    Please don't trade currencies based on this forecast.
    The risk of loss in trading or holding Digital Currency can be substantial.

    Current implementation uses Support Vector Regression (SVR).
    """

    DEFAULT_MODEL_TYPE = 'SVR'
    DEFAULT_SVR_MODEL_PARAMS = {'kernel': 'rbf', 'epsilon': 0.01, 'c': 100, 'gamma': 100}

    def __init__(self, model_type=DEFAULT_MODEL_TYPE):
        """
        Set ups model and pipeline for learning and predicting.

        :param model_type: only 'SVR' model is supported for now
        """
        assert (model_type == 'SVR'), "Model '{}' is not supported. " \
                                      "We support only SVR for now.".format(model_type)
        self._model_type = model_type
        self._model_params = BTCForecast.DEFAULT_SVR_MODEL_PARAMS

        # set up SVR pipeline
        self._scaler = preprocessing.StandardScaler(copy=True, with_mean=True, with_std=True)
        self._model = SVR(kernel=self._model_params['kernel'],
                          epsilon=self._model_params['epsilon'],
                          C=self._model_params['c'],
                          gamma=self._model_params['gamma'])
        self._pipeline = make_pipeline(self._scaler, self._model)
        self.has_learned = False

    def _transform_training_set(self, gdax_rates):
        """
        Transform input for learning

        :param gdax_rates: list of GDAXRate's
        :return: x,y training vectors
        """
        rates = [gdax_rate.closing_price for gdax_rate in gdax_rates]
        timestamps = [gdax_rate.end_time.timestamp() for gdax_rate in gdax_rates]

        x_train = np.reshape(timestamps, (len(timestamps), 1))
        y_train = rates

        return x_train, y_train

    def learn(self, gdax_rates):
        """
        Learns based on past rates.

        :param gdax_rates: list of GDAXRate's
        :return: current score after training
        """
        logging.getLogger('BTCForecast').debug('learning...')
        x_train, y_train = self._transform_training_set(gdax_rates)

        # LEARN!
        self._pipeline.fit(x_train, y_train)
        score = self._pipeline.score(x_train, y_train)
        self.has_learned = True

        logging.getLogger('BTCForecast').debug('score: {}'.format(score))
        return score

    def predict(self, timestamps):
        """
        Predicts a value for each timestamp.

        :param timestamps: a list of timestamps
        :return: a list or predictions
        """
        if not self.has_learned:
            raise TypeError('Learning is required before any predictions')

        x_test = np.reshape(timestamps, (len(timestamps), 1))
        return self._pipeline.predict(x_test)
