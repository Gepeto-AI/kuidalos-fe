import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import calendar

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

inbound_users_by_day = get_inbound_users_by_day()
inbound_users_by_hour = get_inbound_users_by_hour()

st.title("Métricas de Usuarios Inbound")

st.header("Número de usuarios inbound por día de la semana")
if inbound_users_by_day.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por día de la semana.")
else:
    st.bar_chart(inbound_users_by_day)

st.header("Número de usuarios inbound por hora del día (24 hrs)")
if inbound_users_by_hour.empty:
    st.warning("No hay datos disponibles para mostrar en la métrica por hora del día.")
else:
    st.bar_chart(inbound_users_by_hour)
