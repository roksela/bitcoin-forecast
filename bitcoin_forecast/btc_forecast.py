from bitcoin_forecast import GDAXRate

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
        assert (model_type == 'SVR'), "Model '{}' is not supported. " \
                                      "We support only SVR for now.".format(model_type)
        self.model_type = model_type
        self.model_params = BTCForecast.DEFAULT_SVR_MODEL_PARAMS

    def learn(self, rates):
        raise TypeError('This operation is not implemented yet.')

    def predict(self, number_of_steps=None):
        raise TypeError('This operation is not implemented yet.')
