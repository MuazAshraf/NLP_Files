#Load and validate time series for training.
import pandas as pd
s_train = pd.read_csv("./training.csv", index_col="Datetime", parse_dates=True, squeeze=True)
from adtk.data import validate_series
s_train = validate_series(s_train)
print(s_train)

#2Visualize training time series.
from adtk.visualization import plot
plot(s_train)


#3 Detect violation of seasonal pattern.
from adtk.detector import SeasonalAD
seasonal_ad = SeasonalAD()
anomalies = seasonal_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")

#4 If known anomalies are available, cross check with detection results.
known_anomalies = pd.read_csv("./known_anomalies.csv", index_col="Datetime", parse_dates=True, squeeze=True)
from adtk.data import to_events
known_anomalies = to_events(known_anomalies)
print(known_anomalies)
plot(s_train,
         anomaly={"Known": known_anomalies, "Model": anomalies},
         anomaly_tag={"Known": "span", "Model": "marker"},
         anomaly_color={"Known": "orange", "Model": "red"})

#5 Apply the trained model to new data.
s_test = pd.read_csv("./testing.csv", index_col="Datetime", parse_dates=True, squeeze=True)
s_test = validate_series(s_test)
print(s_test)
anomalies_pred = seasonal_ad.detect(s_test)
plot(s_test, anomaly=anomalies_pred,
         ts_linewidth=1, anomaly_color='red', anomaly_tag="marker")