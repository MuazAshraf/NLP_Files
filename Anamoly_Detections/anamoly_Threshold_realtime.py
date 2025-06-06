import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from adtk.data import validate_series
from adtk.detector import ThresholdAD
import time

# Initialize the anomaly detector
detector = ThresholdAD(high=3, low=-3)  # Set high and low thresholds

# Initialize variables
data_stream = []
time_index = pd.date_range(start='2023-01-01', periods=1, freq='D')

# Set up the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(12, 6))

# Simulate a continuous data stream
for i in range(100):  # Simulate 100 data points
    # Generate new data point
    new_data_point = np.random.normal(loc=0, scale=1)
    
    # Inject anomalies occasionally
    if i == 50:
        new_data_point += 10  # Inject an anomaly
    elif i == 70:
        new_data_point -= 5   # Inject another anomaly

    # Update the data stream
    data_stream.append(new_data_point)
    time_index = time_index.append(pd.date_range(start=time_index[-1] + pd.Timedelta(days=1), periods=1))

    # Validate the series
    series = validate_series(pd.Series(data_stream, index=time_index[:len(data_stream)]))

    # Detect anomalies
    anomalies = detector.detect(series)

    # Clear the plot and redraw
    ax.clear()
    ax.plot(series, label='Data Stream')
    
    # Extract the anomaly indices and values
    anomaly_indices = anomalies[anomalies].index
    anomaly_values = series[anomalies]

    ax.scatter(anomaly_indices, anomaly_values, color='red', label='Anomalies')
    ax.legend()
    plt.pause(0.1)  # Pause to update the plot

plt.ioff()  # Turn off interactive mode
plt.show()
