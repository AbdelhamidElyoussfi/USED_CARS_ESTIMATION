import joblib
import pandas as pd
import numpy as np

# Load the model, scaler, and encoding dictionaries
scaler = joblib.load("models/scaler.joblib")
model = joblib.load("models/ml_model.joblib")
encoding_dicts = joblib.load("models/encoding_dicts.joblib")

# Load the car dataset to get unique values for dropdowns
cars_data = pd.read_csv("cars_dataframe_v4.csv")

def predict_car_price(
      Brand, Model, Year, Condition, Mileage, Gearbox,
      Fiscal_Power, Fuel, Number_of_Doors, Origin, First_Owner,
      Rear_Camera, Air_Conditioning, Sunroof,
      CD_MP3_Bluetooth, Speed_Limiter, ESP, Leather_Seats,
      Alloy_Wheels, Cruise_Control, Central_Locking, Electric_Windows,
      ABS, Navigation_System_GPS, Onboard_Computer, Airbags, scaler, ml_model, encoding_dicts
):
    """
    Predict the price of a car based on the provided input data.
    """
    # Prepare the feature dictionary with the exact same feature names as during training
    sample_data = {
        'Brand': encoding_dicts['Brand'][Brand],
        'Model': encoding_dicts['Model'][Model],
        'Condition': encoding_dicts['Condition'][Condition],
        'Mileage': Mileage,
        'Gearbox': encoding_dicts['Gearbox'][Gearbox],
        'Fiscal Power': Fiscal_Power,
        'Fuel': encoding_dicts['Fuel'][Fuel],
        'Number of Doors' : Number_of_Doors,
        'Origin': encoding_dicts['Origin'][Origin],
        'First Owner': encoding_dicts['First Owner'][First_Owner],
        'Rear Camera': Rear_Camera,
        'Air Conditioning': Air_Conditioning,
        'Sunroof': Sunroof,
        'CD/MP3/Bluetooth': CD_MP3_Bluetooth,
        'Speed Limiter': Speed_Limiter,
        'ESP': ESP,
        'Leather Seats': Leather_Seats,
        'Alloy Wheels': Alloy_Wheels,
        'Cruise Control': Cruise_Control,
        'Central Locking': Central_Locking,
        'Electric Windows': Electric_Windows,
        'ABS': ABS,
        'Navigation System/GPS': Navigation_System_GPS,
        'Onboard Computer': Onboard_Computer,
        'Airbags': Airbags,
        'Age': 2025 - Year,
        'Power_Age': Fiscal_Power * (2025 - Year),
        'Mileage_Age': Mileage * (2025 - Year),
        'Age_Fiscal_Power': (2025 - Year) * Fiscal_Power,
        'Age_Gearbox': (2025 - Year) * encoding_dicts['Gearbox'][Gearbox],
        'Performance_Ratio': Fiscal_Power / (Mileage + 1),
        'Brand_Model': encoding_dicts['Brand'][Brand] * encoding_dicts['Model'][Model],
        'Fuel_Efficiency': Fiscal_Power / (encoding_dicts['Fuel'][Fuel] + 1),
        'Important_Features_Sum': encoding_dicts['Gearbox'][Gearbox] + (2025 - Year) + Fiscal_Power + encoding_dicts['Fuel'][Fuel] + Cruise_Control + (Fiscal_Power * (2025 - Year)) + encoding_dicts['Origin'][Origin] + Sunroof + encoding_dicts['Brand'][Brand] + encoding_dicts['Model'][Model],
        'Gearbox_Origin': encoding_dicts['Gearbox'][Gearbox] * encoding_dicts['Origin'][Origin],
        'Price_Sensitivity': ((2025 - Year) * Cruise_Control) / (Mileage + 1),
        'Brand_Condition': encoding_dicts['Brand'][Brand] * encoding_dicts['Condition'][Condition],
        'Top_Feature_Interaction': encoding_dicts['Gearbox'][Gearbox] * (2025 - Year) * Fiscal_Power * encoding_dicts['Fuel'][Fuel],
        'Luxury_Features': Leather_Seats + Sunroof + Navigation_System_GPS,
        'Safety_Features': ESP + ABS + Airbags,
        'Comfort_Features': Air_Conditioning + Cruise_Control + Electric_Windows,
    }

    # Convert to DataFrame
    sample_df = pd.DataFrame([sample_data])

    # Scale numerical columns
    sample_df_scaled = scaler.transform(sample_df)

    # Predict the price
    predicted_price = ml_model.predict(sample_df_scaled)[0]

    return predicted_price

predicted_price = predict_car_price(
    Brand="Ford",
    Model="Fiesta",
    Year=2023,
    Condition="Good",
    Mileage=40000,
    Gearbox="Manual",
    Fiscal_Power=6,
    Fuel="Diesel",
    Number_of_Doors=5,
    Origin="WW in Morocco",
    First_Owner="Yes",
    Rear_Camera=1,
    Air_Conditioning=1,
    Sunroof=1,
    CD_MP3_Bluetooth=1,
    Speed_Limiter=1,
    ESP=1,
    Leather_Seats=1,
    Alloy_Wheels=1,
    Cruise_Control=1,
    Central_Locking=1,
    Electric_Windows=1,
    ABS=1,
    Navigation_System_GPS=1,
    Onboard_Computer=1,
    Airbags=1,
    scaler=scaler,
    ml_model=model,
    encoding_dicts=encoding_dicts
)

print(predicted_price)
