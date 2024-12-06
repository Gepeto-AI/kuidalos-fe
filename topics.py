import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from pymongo import MongoClient
import matplotlib.pyplot as plt

# Conectar a MongoDB
MONGODB_URI = st.secrets["MONGODB_URI"]
DATABASE_NAME = st.secrets["MONGODB_DATABASE"]
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db["call_information"]

def get_data_by_topic():
    calls = collection.find(
        {"calls.analysis.times_by_subject": {"$exists": True}},
        {"user_age": 1, "user_gender": 1, "calls.analysis.times_by_subject": 1}
    )

    data = []
    for record in calls:
        user_age = record.get("user_age")
        user_gender = record.get("user_gender")
        for call in record.get("calls", []):
            times_by_subject = call.get("analysis", {}).get("times_by_subject", {})
            for topic, times in times_by_subject.items():
                bot_time = times.get("bot", 0)
                persona_time = times.get("persona", 0)
                total_time = bot_time + persona_time
                if user_age and user_age.isdigit() and int(user_age) >= 60 and total_time > 0:
                    data.append({
                        "topic": topic,
                        "user_age": int(user_age),
                        "user_gender": user_gender,
                        "bot_time": bot_time,
                        "persona_time": persona_time,
                        "total_time": total_time
                    })

    return pd.DataFrame(data)


def get_percentage_time_by_topic(df):
    """
    Calcula el porcentaje de tiempo promedio del chatbot y del cliente por tema,
    asegurando que el tema 'Otros' se muestre al final.
    """
    if df.empty:
        return pd.DataFrame(columns=["bot_percentage", "persona_percentage"])

    # Agrupación por tema y cálculo de totales
    grouped = df.groupby("topic")[["bot_time", "persona_time"]].sum()
    grouped["total_time"] = grouped["bot_time"] + grouped["persona_time"]

    # Cálculo de porcentajes
    grouped["bot_percentage"] = (grouped["bot_time"] / grouped["total_time"]) * 100
    grouped["persona_percentage"] = (grouped["persona_time"] / grouped["total_time"]) * 100

    # Asegurar que "Otros" esté al final
    if "Otros" in grouped.index:
        # Reordenar el índice manualmente para poner "Otros" al final
        other_row = grouped.loc["Otros"]
        grouped = grouped.drop("Otros")
        grouped = pd.concat([grouped, pd.DataFrame({"topic": ["Otros"], **other_row.to_dict()}).set_index("topic")])

    return grouped[["bot_percentage", "persona_percentage"]]


def generate_pie_chart_by_topic(df):
    """
    Genera una gráfica de torta para mostrar el porcentaje de tiempo total dedicado a cada tema.
    """
    if df.empty:
        st.warning("No hay datos disponibles para generar la gráfica.")
        return

    # Agrupar datos por tema y calcular el tiempo total por tema
    grouped = df.groupby("topic")["total_time"].sum()

    # Configurar el gráfico de torta
    plt.figure(figsize=(8, 8))
    plt.pie(
        grouped,
        labels=grouped.index,
        autopct='%1.1f%%',
        startangle=140
    )
    plt.title("Distribución de tiempo por tema")
    plt.axis('equal')  # Asegurar que la gráfica sea circular
    st.pyplot(plt)


def get_total_time_by_topic_age_gender(df):
    grouped = df.groupby(["topic", "user_age", "user_gender"])["total_time"].sum().unstack()
    return grouped


def get_average_time_per_call_by_topic_age_gender(df):
    grouped = df.groupby(["topic", "user_age", "user_gender"])["total_time"].mean().unstack()
    return grouped