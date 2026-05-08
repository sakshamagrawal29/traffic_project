import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import joblib

# Load dataset
df = pd.read_csv("traffic_prediction_dataset.csv")

print(df.head())

# Label Encoding
le_city = LabelEncoder()
le_day = LabelEncoder()
le_weather = LabelEncoder()
le_road = LabelEncoder()
le_target = LabelEncoder()

df['city'] = le_city.fit_transform(df['city'])
df['day'] = le_day.fit_transform(df['day'])
df['weather_main'] = le_weather.fit_transform(df['weather_main'])
df['road_condition'] = le_road.fit_transform(df['road_condition'])

# Target encoding
df['congestion_level'] = le_target.fit_transform(df['congestion_level'])

# Features
X = df[[
    'city',
    'hour',
    'day',
    'weather_main',
    'road_condition',
    'vehicle_count',
    'avg_speed'
]]

# Target
y = df['congestion_level']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create model
model = XGBClassifier()

# Train model
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "traffic_model.pkl")

print("✅ Model Saved Successfully")