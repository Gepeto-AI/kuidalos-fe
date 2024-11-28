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

# Mapeo de días en inglés a español
day_translation = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

# Obtener datos de la colección
def get_inbound_users_by_day():
    # Filtrar solo las llamadas de tipo inbound usando $elemMatch
    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}}, 
        {"calls": 1, "user_id": 1}  # Proyección para incluir solo lo necesario
    )

    # Crear una lista para almacenar los datos
    data = []
    for record in inbound_calls:
        # Iterar sobre el campo "calls" que es un arreglo
        for call in record.get("calls", []):
            # Filtrar solo las llamadas de tipo "inbound"
            if call.get("type_call") == "inbound":
                # Validar que call_start_time exista
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        # Parsear la fecha y calcular el día de la semana
                        call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                        day_of_week = calendar.day_name[call_start_time.weekday()]  # Obtener el día de la semana en inglés
                        day_of_week_spanish = day_translation[day_of_week]  # Traducir al español
                        data.append({"user_id": record["user_id"], "day_of_week": day_of_week_spanish})
                    except Exception as e:
                        st.warning(f"Error al procesar la fecha: {call_start_time}, error: {e}")

    # Verificar si hay datos
    if not data:
        st.warning("No se encontraron llamadas inbound para procesar.")
        return pd.Series(dtype=int)  # Retornar una serie vacía para evitar errores

    # Convertir a DataFrame
    df = pd.DataFrame(data)

    # Contar usuarios únicos por día de la semana
    inbound_users_by_day = (
        df.groupby("day_of_week")["user_id"]
        .nunique()
        .reindex(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], fill_value=0)
    )

    # Asegurarse de que los días estén ordenados correctamente
    day_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    inbound_users_by_day.index = pd.CategoricalIndex(
        inbound_users_by_day.index, categories=day_order, ordered=True
    )
    inbound_users_by_day = inbound_users_by_day.sort_index()

    return inbound_users_by_day

# Llamar a la función para obtener los datos
inbound_users_by_day = get_inbound_users_by_day()

# Mostrar los datos en la aplicación de Streamlit
st.title("Número de usuarios inbound por día de la semana")

if inbound_users_by_day.empty:
    st.warning("No hay datos disponibles para mostrar.")
else:
    st.bar_chart(inbound_users_by_day)
