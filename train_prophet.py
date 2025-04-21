# train_prophet.py
import pandas as pd
from prophet import Prophet
import joblib

df = pd.read_csv("e_waste_data.csv")
df = df[df["state"] == "Karnataka"]  # Train per state
df = df.groupby("year")[["e_waste_quantity"]].sum().reset_index()
df.rename(columns={"year": "ds", "e_waste_quantity": "y"}, inplace=True)

df["ds"] = pd.to_datetime(df["ds"], format="%Y")  # Prophet needs datetime
model = Prophet()
model.fit(df)

joblib.dump(model, "prophet_karnataka.pkl")
