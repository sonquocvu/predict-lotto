from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import LSTM, Bidirectional, Dropout, Dense
import pandas as pd
import numpy as np
import logging
import os


class PredictVietlottNumbers:

    def __init__(self, Input, Type):
        self.Input = Input
        self.Type = Type

        logPath = os.getcwd() + "\log"
        file = logPath + "\predict-{}.log".format(self.Type)
        # try:
        #     if Path(file).is_file():
        #         os.remove(file)
        # except PermissionError:
        #     pass

        formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
        HandlerDebug = logging.FileHandler(file)
        HandlerDebug.setLevel(logging.DEBUG)
        HandlerDebug.setFormatter(formatter)

        self.logger = logging.getLogger('__main__.' + __name__)
        self.logger.addHandler(HandlerDebug)
        self.logger.addHandler(HandlerDebug)
        self.logger.setLevel(logging.DEBUG)

    def Start(self):
        # Create metric data for predicting
        df = pd.DataFrame(np.array(self.Input), columns=list('ABCDEF'))

        # Normalize data
        scaler = StandardScaler().fit(df.values)
        transformedDataSet = scaler.transform(df.values)
        transformedDf = pd.DataFrame(data=transformedDataSet, index=df.index)

        # Define hyper params of or model
        numberOfRows = df.values.shape[0]
        windowsLength = 7
        numberOfFeature = df.values.shape[1]

        # Create train dataset and labels for each row. It should have format for Keras LSTM model (rows, window size, balls)
        train = np.empty([numberOfRows - windowsLength, windowsLength, numberOfFeature], dtype=float)
        label = np.empty([numberOfRows - windowsLength, numberOfFeature], dtype=float)
        windowsLength = 7

        for i in range(0, numberOfRows - windowsLength):
            train[i] = transformedDf.iloc[i: i + windowsLength, 0: numberOfFeature]
            label[i] = transformedDf.iloc[i + windowsLength: i + windowsLength + 1, 0: numberOfFeature]

        # for i in range(0, 6):
        # LSTM Model
        model = Sequential()
        model.add(Bidirectional(LSTM(240,
                                     input_shape=(windowsLength, numberOfFeature),
                                     return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(240,
                                     input_shape=(windowsLength, numberOfFeature),
                                     return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(240,
                                     input_shape=(windowsLength, numberOfFeature),
                                     return_sequences=True)))
        model.add(Bidirectional(LSTM(240,
                                     input_shape=(windowsLength, numberOfFeature),
                                     return_sequences=False)))
        model.add(Dense(59))
        model.add(Dense(numberOfFeature))
        model.compile(loss='mse', optimizer='rmsprop', metrics=['accuracy'])
        model.fit(train, label, batch_size=100, epochs=300)

        # Conclusion
        toPredict = np.array(self.Input)
        scaledToPredict = scaler.transform(toPredict)

        scaledToPredictOutput = model.predict(np.array([scaledToPredict]))
        res = scaler.inverse_transform(scaledToPredictOutput).astype(int)[0]
        self.logger.info("The result is: {}".format(res))
        return res
