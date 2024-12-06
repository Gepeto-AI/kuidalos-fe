import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import calendar
import numpy as np
from datetime import datetime
import pytz

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

def get_inbound_calls_by_day():
    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}}, 
        {"calls": 1}  # Solo necesitas el campo `calls`
    )

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "inbound":
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        # Convertir el tiempo de inicio de la llamada al formato datetime
                        call_start_time = datetime.fromisoformat(call_start_time.split(".")[0])
                        day_of_week = calendar.day_name[call_start_time.weekday()]
                        day_of_week_spanish = day_translation[day_of_week]
                        data.append({"day_of_week": day_of_week_spanish})
                    except Exception as e:
                        # Manejar errores de conversión de fecha
                        print(f"Error procesando la llamada: {e}")
                        continue

    if not data:
        # Si no hay datos, retornar una serie vacía
        return pd.Series(dtype=int)

    # Convertir la lista de datos a un DataFrame
    df = pd.DataFrame(data)

    # Contar llamadas por día de la semana
    inbound_calls_by_day = (
        df["day_of_week"]
        .value_counts()
        .reindex(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], fill_value=0)
    )

    # Asegurar el orden correcto de los días de la semana
    inbound_calls_by_day.index = pd.CategoricalIndex(
        inbound_calls_by_day.index,
        categories=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        ordered=True
    )

    return inbound_calls_by_day.sort_index()

def get_inbound_calls_by_hour():
    # Zona horaria de México Central
    mexico_city_tz = pytz.timezone("America/Mexico_City")
    utc_tz = pytz.utc

    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}}, 
        {"calls": 1}  # Solo necesitas el campo `calls`
    )

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "inbound":
                call_start_time = call.get("call_start_time")
                if call_start_time:
                    try:
                        # Convertir la hora en formato naive a UTC y luego a la hora local de México
                        utc_time = datetime.fromisoformat(call_start_time.split(".")[0]).replace(tzinfo=utc_tz)
                        local_time = utc_time.astimezone(mexico_city_tz)
                        hour_of_day = local_time.hour
                        data.append({"hour_of_day": hour_of_day})
                    except Exception as e:
                        # Manejar errores de conversión de fecha
                        print(f"Error procesando la llamada: {e}")
                        continue

    if not data:
        # Si no hay datos, retornar una serie vacía
        return pd.Series(dtype=int)

    # Convertir la lista de datos a un DataFrame
    df = pd.DataFrame(data)

    # Contar llamadas por hora
    inbound_calls_by_hour = (
        df["hour_of_day"]
        .value_counts()
        .reindex(range(24), fill_value=0)
        .sort_index()
    )

    return inbound_calls_by_hour

def get_inbound_calls_by_gender():
    inbound_calls = collection.find(
        {"calls.type_call": "inbound"}, 
        {"calls": 1, "user_gender": 1}  # Incluye solo los campos necesarios
    )

    data = []
    for record in inbound_calls:
        gender = record.get("user_gender")
        calls = record.get("calls", [])
        if gender and calls:
            # Itera a través de las llamadas para agregar una entrada por llamada
            for call in calls:
                if call.get("type_call") == "inbound":
                    data.append({"gender": gender})

    if not data:
        # Si no hay datos, retorna una serie vacía
        return pd.Series(dtype=int)

    # Convierte los datos en un DataFrame
    df = pd.DataFrame(data)

    # Cuenta las llamadas por género
    inbound_calls_by_gender = df["gender"].value_counts()

    return inbound_calls_by_gender

def get_inbound_calls_by_duration():
    inbound_calls = collection.find(
        {"calls.type_call": "inbound"}, 
        {"calls": 1}  # Incluye solo los campos necesarios
    )

    data = []
    for record in inbound_calls:
        for call in record.get("calls", []):
            if call.get("type_call") == "inbound":
                duration_seconds = call.get("call_duration", {}).get("original_total_time")  # Duración en segundos
                if duration_seconds is not None:
                    # Convierte la duración a minutos
                    duration_minutes = duration_seconds / 60
                    data.append({"call_duration": duration_minutes})

    if not data:
        # Si no hay datos, retorna una serie vacía
        return pd.Series(dtype=int)
    #st.write(f"Tamaño de los datos procesados: {len(data)}")

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

    # Reordena los resultados basados en los intervalos ordenados
    #grouped_data = grouped_data.sort_index()

    return grouped_data

def get_inbound_calls_by_age():
    inbound_calls = collection.find({"calls.type_call": "inbound"}, {"calls": 1, "user_age": 1})

    data = []
    for record in inbound_calls:
        age = record.get("user_age")
        calls = record.get("calls", [])
        if age and age.isdigit() and int(age) >= 60:
            for call in calls:
                if call.get("type_call") == "inbound":
                    data.append({"call_id": call.get("call_id"), "age": int(age)})

    if not data:
        return pd.Series(dtype=int)

    df = pd.DataFrame(data)
    bins = np.arange(60, df["age"].max() + 5, 5)
    df["age_range"] = pd.cut(df["age"], bins=bins)
    df["age_range_str"] = pd.Categorical(
        df["age_range"].astype(str),
        categories=[str(interval) for interval in pd.IntervalIndex.from_breaks(bins)],
        ordered=True
    )

    grouped_data = df.groupby("age_range_str")["call_id"].count()
    return grouped_data

def get_calls_distribution():
    inbound_calls = collection.find(
        {"calls": {"$elemMatch": {"type_call": "inbound"}}},
        {"calls": 1, "user_id": 1, "user_gender": 1, "user_age": 1}
    )

    data = []
    for record in inbound_calls:
        user_id = record.get("user_id")
        user_gender = record.get("user_gender")
        user_age = int(record.get("user_age", 0)) if record.get("user_age") and record.get("user_age").isdigit() else None
        num_calls = len([call for call in record.get("calls", []) if call.get("type_call") == "inbound"])
        data.append({"user_id": user_id, "gender": user_gender, "age": user_age, "num_calls": num_calls})

    df = pd.DataFrame(data)
    call_bins = [0, 3, 4, 6, 8, float("inf")]
    call_labels = ["0-3", "4", "5-6", "7-8", "9 o más"]
    df["call_range"] = pd.cut(df["num_calls"], bins=call_bins, labels=call_labels, right=True)
    
    age_bins = [60, 65, 70, 75, 80, 85, 90, float("inf")]
    age_labels = ["60-65", "66-70", "71-75", "76-80", "81-85", "86-90", "90 o más"]
    df["age_range"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=True)

    summary_table = pd.pivot_table(
        df,
        values="user_id",
        index="call_range",
        columns=["gender", "age_range"],
        aggfunc="nunique",
        fill_value=0
    )
    summary_table = summary_table.apply(
        lambda x: x.astype(str) + "/" + x.groupby(level=0).sum().astype(str), axis=0
    )

    # Convertir el índice `call_range` en una columna
    summary_table.reset_index(inplace=True)

    # Renombrar la columna `call_range` como "# de llamadas"
    summary_table.rename(columns={"call_range": "# de llamadas"}, inplace=True)
    
    #Ajustar encabezados para agregar el título de la columna "# de llamadas"
    columns = [("# de llamadas", "")] + [(gender, age_range) for gender, age_range in summary_table.columns[1:]]

    # Filtrar las columnas para eliminar las no deseadas
    columns_to_keep = [("# de llamadas", "")] + [
        col for col in columns if col[0] in ["Female", "Male"]
    ]

    # Actualizar los encabezados con las columnas a mantener
    summary_table = summary_table[[col for col in summary_table.columns if col in columns_to_keep]]
    summary_table.columns = pd.MultiIndex.from_tuples(columns_to_keep)
    
    # Renombrar los géneros a español
    summary_table.columns = pd.MultiIndex.from_tuples(
        [("# de llamadas", "# de llamadas")] + 
        [("Mujer" if gender == "Female" else "Hombre", age_range) for gender, age_range in summary_table.columns[1:]]
    )

    return summary_table
