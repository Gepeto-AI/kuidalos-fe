import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import calendar
import numpy as np

# Conectar a MongoDB
MONGODB_URI = st.secrets["MONGODB_URI"]
DATABASE_NAME = st.secrets["MONGODB_DATABASE"]
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db["call_information"]

day_translation = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

def get_inbound_users_by_day():
    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}}, 
        {"calls": 1, "user_id": 1}
    )

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "inbound":
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                        day_of_week = calendar.day_name[call_start_time.weekday()]
                        day_of_week_spanish = day_translation[day_of_week]
                        data.append({"user_id": record["user_id"], "day_of_week": day_of_week_spanish})
                    except Exception as e:
                        st.warning(f"Error al procesar la fecha: {call_start_time}, error: {e}")

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    inbound_users_by_day = (
        df.groupby("day_of_week")["user_id"]
        .nunique()
        .reindex(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], fill_value=0)
    )

    inbound_users_by_day.index = pd.CategoricalIndex(
        inbound_users_by_day.index,
        categories=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        ordered=True
    )

    return inbound_users_by_day.sort_index()

def get_inbound_users_by_hour():
    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}}, 
        {"calls": 1, "user_id": 1}
    )

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "inbound":
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                        hour_of_day = call_start_time.hour
                        data.append({"user_id": record["user_id"], "hour_of_day": hour_of_day})
                    except Exception as e:
                        st.warning(f"Error al procesar la fecha: {call_start_time}, error: {e}")

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    inbound_users_by_hour = (
        df.groupby("hour_of_day")["user_id"]
        .nunique()
        .reindex(range(24), fill_value=0)
    )
    return inbound_users_by_hour

def get_inbound_users_by_gender():
    inbound_users = collection.find({"calls.type_call": "inbound"}, {"user_gender": 1, "user_id": 1})

    data = []
    for record in inbound_users:
        gender = record.get("user_gender")
        if gender:
            data.append({"user_id": record["user_id"], "gender": gender})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    return df.groupby("gender")["user_id"].nunique()

def get_inbound_users_by_call_duration():
    inbound_calls = collection.find({"calls.type_call": "inbound"}, {"calls.call_duration.human": 1, "user_id": 1})

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            duration = call.get("call_duration", {}).get("human")
            if duration is not None:
                data.append({"user_id": record["user_id"], "call_duration": duration})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    bins = np.arange(0, df["call_duration"].max() + 5, 5)  # Rango de 5 minutos
    df["duration_range"] = pd.cut(df["call_duration"], bins=bins)
    
    # Convertir los intervalos a cadenas
    df["duration_range_str"] = df["duration_range"].astype(str)

    grouped_data = df.groupby("duration_range_str")["user_id"].nunique()
    return grouped_data


def get_inbound_users_by_age():
    inbound_users = collection.find({"calls.type_call": "inbound"}, {"user_age": 1, "user_id": 1})

    data = []
    for record in inbound_users:
        age = record.get("user_age")
        if age and age.isdigit() and int(age) >= 60:
            data.append({"user_id": record["user_id"], "age": int(age)})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    bins = np.arange(60, df["age"].max() + 5, 5)  # Rango de 5 años desde 60
    df["age_range"] = pd.cut(df["age"], bins=bins)
    
    # Convertir los intervalos a cadenas
    df["age_range_str"] = df["age_range"].astype(str)

    grouped_data = df.groupby("age_range_str")["user_id"].nunique()
    return grouped_data


# Obtener los datos para las gráficas
inbound_users_by_day = get_inbound_users_by_day()
inbound_users_by_hour = get_inbound_users_by_hour()
inbound_users_by_gender = get_inbound_users_by_gender()
inbound_users_by_call_duration = get_inbound_users_by_call_duration()
inbound_users_by_age = get_inbound_users_by_age()

# Mostrar las gráficas en la aplicación de Streamlit
st.title("Métricas de Usuarios Inbound")

# Gráfica 1: Usuarios inbound por día de la semana
st.header("Número de usuarios inbound por día de la semana")
if inbound_users_by_day.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por día de la semana.")
else:
    st.bar_chart(inbound_users_by_day)

# Gráfica 2: Usuarios inbound por hora del día
st.header("Número de usuarios inbound por hora del día (24 hrs)")
if inbound_users_by_hour.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por hora del día.")
else:
    st.bar_chart(inbound_users_by_hour)

# Gráfica 3: Usuarios inbound por género
st.header("Número de usuarios inbound por género")
if inbound_users_by_gender.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por género.")
else:
    st.bar_chart(inbound_users_by_gender)

# Gráfica 4: Usuarios inbound por duración de llamadas
st.header("Número de usuarios inbound por duración de las llamadas (rangos de 5 minutos)")
if inbound_users_by_call_duration.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por duración de llamadas.")
else:
    st.bar_chart(inbound_users_by_call_duration)

# Gráfica 5: Usuarios inbound por edad
st.header("Número de usuarios inbound por edad (rangos de 5 años desde 60 años)")
if inbound_users_by_age.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por edad.")
else:
    st.bar_chart(inbound_users_by_age)
