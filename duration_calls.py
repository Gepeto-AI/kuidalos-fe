import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import calendar

# Configuración de MongoDB
MONGODB_URI = st.secrets["MONGODB_URI"]
DATABASE_NAME = st.secrets["MONGODB_DATABASE"]
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db["call_information"]

# Función para obtener la duración promedio total
def get_average_call_duration():
    calls = collection.find(
        {"calls.call_duration.original_total_time": {"$exists": True}},
        {"calls.call_duration.original_total_time": 1}
    )

    durations = []
    for record in calls:
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("original_total_time")
            if duration is not None:
                durations.append(duration)

    if not durations:
        return 0

    return round(np.mean(durations) / 60, 2)  # Convertir a minutos

# Función para obtener la duración promedio por género
def get_average_call_duration_by_gender():
    calls = collection.find(
        {"calls.call_duration.original_total_time": {"$exists": True}},
        {"user_gender": 1, "calls.call_duration.original_total_time": 1}
    )

    data = []
    for record in calls:
        gender = record.get("user_gender")
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("original_total_time")
            if duration is not None and gender:
                data.append({"gender": gender, "duration": duration / 60})  # Convertir a minutos

    if not data:
        return pd.Series(dtype=float)

    df = pd.DataFrame(data)
    return df.groupby("gender")["duration"].mean()

# Función para duración promedio por edad
def get_average_call_duration_by_age():
    calls = collection.find(
        {"calls.call_duration.original_total_time": {"$exists": True}},
        {"user_age": 1, "calls.call_duration.original_total_time": 1}
    )

    data = []
    for record in calls:
        age = record.get("user_age")
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("original_total_time")
            if duration is not None and age and age.isdigit() and int(age) >= 60:
                data.append({"age": int(age), "duration": duration / 60})  # Convertir a minutos

    if not data:
        return pd.Series(dtype=float)

    df = pd.DataFrame(data)
    bins = np.arange(60, 95, 5)  # Rangos de edad
    df["age_range"] = pd.cut(df["age"], bins=bins)

    # Convierte los intervalos a cadenas para visualización
    df["age_range_str"] = df["age_range"].astype(str)
    grouped_data = df.groupby("age_range_str")["duration"].mean()

    return grouped_data

# Función para duración promedio por día de la semana
def get_average_call_duration_by_day_of_week():
    calls = collection.find(
        {"calls.call_duration.original_total_time": {"$exists": True}},
        {"calls.call_duration.original_total_time": 1, "calls.call_start_time": 1}
    )

    data = []
    for record in calls:
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("original_total_time")
            call_start_time = call.get("call_start_time")
            if duration is not None and call_start_time:
                try:
                    # Intentar procesar call_start_time
                    call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                    day_of_week = calendar.day_name[call_start_time.weekday()]
                    data.append({"day_of_week": day_of_week, "duration": duration / 60})  # Convertir a minutos
                except Exception as e:
                    st.warning(f"Error procesando call_start_time '{call_start_time}': {e}")
                    continue

    if not data:
        return pd.Series(dtype=float)

    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Ordenar los días de la semana
    df["day_of_week"] = pd.Categorical(
        df["day_of_week"], 
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
        ordered=True
    )

    # Agrupar por día de la semana y calcular la media
    average_duration = df.groupby("day_of_week")["duration"].mean()

    return average_duration

# Función para duración promedio por hora del día
def get_average_call_duration_by_hour_of_day():
    calls = collection.find(
        {"calls.call_duration.original_total_time": {"$exists": True}},
        {"calls.call_duration.original_total_time": 1, "calls.call_start_time": 1}
    )

    data = []
    for record in calls:
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("original_total_time")
            call_start_time = call.get("call_start_time")
            if duration is not None and call_start_time:
                try:
                    # Procesar call_start_time
                    call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                    hour_of_day = call_start_time.hour
                    data.append({"hour_of_day": hour_of_day, "duration": duration / 60})  # Convertir a minutos
                except Exception as e:
                    st.warning(f"Error procesando call_start_time '{call_start_time}': {e}")
                    continue

    if not data:
        return pd.Series(dtype=float)

    # Crear DataFrame
    df = pd.DataFrame(data)
  
    # Calcular la duración promedio por hora del día
    average_duration_by_hour = (
        df.groupby("hour_of_day")["duration"]
        .mean()
        .reindex(range(24), fill_value=0)  # Asegura que todas las horas estén presentes
    )

    return average_duration_by_hour

# Función para porcentaje de conversación por género
def get_chatbot_vs_human_percentage_by_gender():
    calls = collection.find(
        {"calls.call_duration": {"$exists": True}},
        {"user_gender": 1, "calls.call_duration.human": 1, "calls.call_duration.bot": 1}
    )

    data = []
    for record in calls:
        gender = record.get("user_gender")
        for call in record.get("calls", []):
            human_time = call.get("call_duration", {}).get("human", 0)
            bot_time = call.get("call_duration", {}).get("bot", 0)
            total_time = human_time + bot_time
            if total_time > 0 and gender:
                human_percentage = (human_time / total_time) * 100
                bot_percentage = (bot_time / total_time) * 100
                data.append({"gender": gender, "human_percentage": human_percentage, "bot_percentage": bot_percentage})

    if not data:
        return pd.DataFrame(columns=["gender", "human_percentage", "bot_percentage"])

    df = pd.DataFrame(data)
    return df.groupby("gender")[["human_percentage", "bot_percentage"]].mean()

# Función para porcentaje de conversación por edad
def get_chatbot_vs_human_percentage_by_age():
    calls = collection.find(
        {"calls.call_duration": {"$exists": True}},
        {"user_age": 1, "calls.call_duration.human": 1, "calls.call_duration.bot": 1}
    )

    data = []
    for record in calls:
        age = record.get("user_age")
        for call in record.get("calls", []):
            human_time = call.get("call_duration", {}).get("human", 0)
            bot_time = call.get("call_duration", {}).get("bot", 0)
            total_time = human_time + bot_time
            if total_time > 0 and age and age.isdigit() and int(age) >= 60:
                human_percentage = (human_time / total_time) * 100
                bot_percentage = (bot_time / total_time) * 100
                data.append({"age": int(age), "human_percentage": human_percentage, "bot_percentage": bot_percentage})

    if not data:
        return pd.DataFrame(columns=["age_range", "human_percentage", "bot_percentage"])

    df = pd.DataFrame(data)
    bins = np.arange(60, 95, 5)  # Rangos de edad
    df["age_range"] = pd.cut(df["age"], bins=bins)

    # Convertir los intervalos a cadenas
    df["age_range_str"] = df["age_range"].astype(str)

    grouped_data = (
        df.groupby("age_range_str")[["human_percentage", "bot_percentage"]]
        .mean()
        .sort_index()
    )

    return grouped_data