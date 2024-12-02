import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime, timedelta

# Configuración de MongoDB
MONGODB_URI = st.secrets["MONGODB_URI"]
DATABASE_NAME = st.secrets["MONGODB_DATABASE"]
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db["call_information"]

def get_outbound_calls_by_week():
    outbound_calls = collection.find(
        {"calls.type_call": "outbound"},
        {"calls": 1}
    )

    data = []
    for record in outbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "outbound":
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                        week_start = call_start_time - timedelta(days=call_start_time.weekday())
                        week_end = week_start + timedelta(days=6)
                        week_interval = f"{week_start.strftime('%d/%m/%y')} - {week_end.strftime('%d/%m/%y')}"
                        data.append({"week_interval": week_interval})
                    except Exception as e:
                        pass

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
   
    # Agrupa las llamadas por intervalo semanal
    weekly_calls = df.groupby("week_interval").value_counts()

    # Ordena las semanas por fecha
    weekly_calls = weekly_calls.sort_index(key=lambda x: pd.to_datetime([interval.split(" - ")[0] for interval in x]))

    return weekly_calls

def get_outbound_calls_by_duration():
    outbound_calls = collection.find(
        {"calls.type_call": "outbound"}, 
        {"calls": 1}  # Incluye solo los campos necesarios
    )
    
    data = []
    for record in outbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "outbound":
                duration_seconds = call.get("call_duration", {}).get("original_total_time")  # Duración en segundos
                if duration_seconds is not None:
                    # Convierte la duración a minutos
                    duration_minutes = duration_seconds / 60
                    data.append({"call_duration": duration_minutes})

    if not data:
        # Si no hay datos, retorna una serie vacía
        return pd.Series(dtype=int)

    # Convierte los datos a un DataFrame
    df = pd.DataFrame(data)

    # Define los intervalos en minutos (rango de 5 minutos)
    max_duration = df["call_duration"].max()
    bins = np.arange(0, max_duration + 5, 5)
    # Incrementar el último límite para incluir valores exactos al máximo
    bins[-1] += 0.1  # Asegura que el límite superior sea inclusivo
    df["duration_range"] = pd.cut(df["call_duration"], bins=bins, right=False, include_lowest=True)


    # Asegura el orden correcto de los intervalos y convierte a strings para el eje X
    ordered_intervals = pd.IntervalIndex([pd.Interval(bins[i], bins[i + 1], closed='left') for i in range(len(bins) - 1)])

    # Asegura que los datos respeten este orden
    df["duration_range_str"] = pd.Categorical(
        df["duration_range"].astype(str),
        categories=[str(interval) for interval in ordered_intervals],
        ordered=True
    )

    # Cuenta las llamadas por rango de duración
    grouped_data = df["duration_range_str"].value_counts().sort_index()
    
    return grouped_data

def get_outbound_calls_by_age():
    outbound_calls = collection.find(
        {"calls.type_call": "outbound"}, 
        {"user_age": 1, "user_id": 1}
    )

    data = []
    for record in outbound_calls:
        age = record.get("user_age")
        if age and age.isdigit() and int(age) >= 60:
            data.append({"user_id": record["user_id"], "age": int(age)})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    bins = np.arange(60, df["age"].max() + 5, 5)
    df["age_range"] = pd.cut(df["age"], bins=bins)
    df["age_range_str"] = df["age_range"].astype(str)

    grouped_data = df.groupby("age_range_str")["user_id"].nunique()
    return grouped_data.sort_index()

def get_outbound_calls_by_gender():
    outbound_calls = collection.find(
        {"calls.type_call": "outbound"}, 
        {"user_gender": 1, "user_id": 1}
    )

    data = []
    for record in outbound_calls:
        gender = record.get("user_gender")
        if gender:
            data.append({"user_id": record["user_id"], "gender": gender})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    grouped_data = df.groupby("gender")["user_id"].nunique()
    return grouped_data