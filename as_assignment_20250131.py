# -*- coding: utf-8 -*-
"""AS_ASSIGNMENT_20250131

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YN9cwqCPKtMZXQCVr9vBtYirww6gxWSg

# **Environment Setup**
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

"""# **Load the Dataset**"""

# Load dataset from specified file path
file_path = '/content/Air Quality.xlsx'
data = pd.read_excel(file_path)

# Display the first few rows
data.head()

"""# **Data Preprocessing**"""

# Ensure 'Date' and 'Time' columns are strings before concatenation
data['Date'] = data['Date'].astype(str)
data['Time'] = data['Time'].astype(str)

print(data[['Date', 'Time']].head())

data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], errors='coerce')

print(data[data['DateTime'].isna()])

# Combine 'Date' and 'Time' columns into a single 'DateTime' column
try:
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
except Exception as e:
    print(f"Error parsing datetime: {e}")

# Drop 'Date' and 'Time' columns
data = data.drop(['Date', 'Time'], axis=1)

# Sort by 'DateTime'
data = data.sort_values(by='DateTime').reset_index(drop=True)

# Display the first few rows to verify
print(data.head())

"""# **Exploratory Data Analysis (EDA)**"""

# Summary statistics
data.describe()

# Check for correlations
plt.figure(figsize=(12, 8))
correlation_matrix = data.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# Plot target variable trends over time
plt.figure(figsize=(12, 6))
plt.plot(data['DateTime'], data['CO(GT)'], label='CO Concentration (mg/m^3)')
plt.title('CO Concentration Over Time')
plt.xlabel('Time')
plt.ylabel('CO Concentration')
plt.legend()
plt.show()

"""# **Feature Selection and Preparation**"""

# Define target and features
target = 'CO(GT)'
features = ['PT08.S1(CO)', 'PT08.S2(NMHC)', 'PT08.S3(NOx)', 'PT08.S4(NO2)', 'PT08.S5(O3)',
            'T', 'RH', 'AH']

X = data[features]
y = data[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""# **Machine Learning Model - Random Forest Regressor**"""

# Initialize Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predict and evaluate
rf_predictions = rf_model.predict(X_test)
rf_mse = mean_squared_error(y_test, rf_predictions)
rf_r2 = r2_score(y_test, rf_predictions)

print("Random Forest Mean Squared Error:", rf_mse)
print("Random Forest R^2 Score:", rf_r2)

"""# **Deep Learning Model - LSTM**"""

# Scale the data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data[features + [target]])

# Prepare data for LSTM
generator = TimeseriesGenerator(scaled_data[:, :-1], scaled_data[:, -1], length=24, batch_size=32)

# Build the LSTM model
lstm_model = Sequential([
    LSTM(50, activation='relu', input_shape=(24, len(features))),
    Dense(1)
])

lstm_model.compile(optimizer='adam', loss='mse')

# Train the model
lstm_model.fit(generator, epochs=3)

# Predict using the LSTM model
lstm_predictions = lstm_model.predict(generator)
lstm_mse = mean_squared_error(scaled_data[24:, -1], lstm_predictions)
lstm_r2 = r2_score(scaled_data[24:, -1], lstm_predictions)

print("LSTM Mean Squared Error:", lstm_mse)
print("LSTM R^2 Score:", lstm_r2)

"""# **Visualization of Predictions**"""

# Compare predictions to actual values for Random Forest
plt.figure(figsize=(12, 6))
plt.plot(y_test.values, label='Actual', alpha=0.7)
plt.plot(rf_predictions, label='Random Forest Predictions', alpha=0.7)
plt.title('Random Forest Predictions vs Actual Values')
plt.legend()
plt.show()

# Visualization for LSTM predictions
plt.figure(figsize=(12, 6))
plt.plot(scaled_data[24:, -1], label='Actual', alpha=0.7)
plt.plot(lstm_predictions, label='LSTM Predictions', alpha=0.7)
plt.title('LSTM Predictions vs Actual Values')
plt.legend()
plt.show()

"""# **Save Cleaned Dataset and Model Outputs**"""

# Save cleaned dataset
cleaned_file_path = '/content/cleaned_air_quality.csv'
data.to_csv(cleaned_file_path, index=False)
print(f"Cleaned dataset saved to {cleaned_file_path}")

# Save model predictions
predictions_file_path = '/content/predictions.csv'
predictions_df = pd.DataFrame({
    'Actual': y_test,
    'Random Forest Predictions': rf_predictions
})
predictions_df.to_csv(predictions_file_path, index=False)
print(f"Predictions saved to {predictions_file_path}")