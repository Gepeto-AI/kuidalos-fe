import streamlit as st
from inbound import *
from outbound import *
from duration_calls import *
from topics import *
import altair as alt

# Crear menú de selección de páginas
menu_options = ["Llamadas Inbound", "Llamadas Outbound", "Tiempos de llamadas", "Tiempos por temas"]
page_selection = st.sidebar.selectbox("Seleccione una página", menu_options)

# Configurar el contenido basado en la página seleccionada
if page_selection == "Llamadas Inbound":
    st.title("Métricas de Usuarios Inbound")

    inbound_users_by_day = get_inbound_calls_by_day()
    inbound_users_by_hour = get_inbound_calls_by_hour()
    inbound_users_by_gender = get_inbound_calls_by_gender()
    inbound_users_by_call_duration = get_inbound_calls_by_duration()
    inbound_users_by_age = get_inbound_calls_by_age()
    call_distribution_table = get_calls_distribution()

    st.header("Número de llamadas inbound por día de la semana")
    if inbound_users_by_day.empty:
        st.warning("No hay datos disponibles para mostrar en la métrica por día de la semana.")
    else:
        st.bar_chart(inbound_users_by_day)

    st.header("Número de llamadas inbound por hora del día (24 hrs)")
    if inbound_users_by_hour.empty:
        st.warning("No hay datos disponibles para mostrar en la métrica por hora del día.")
    else:
        st.bar_chart(inbound_users_by_hour)

    st.header("Número de llamadas inbound por género")
    if inbound_users_by_gender.empty:
        st.warning("No hay datos disponibles para mostrar en la métrica por género.")
    else:
        st.bar_chart(inbound_users_by_gender)

    st.header("Número de llamadas inbound por edad (rangos de 5 años desde 60 años)")
    if inbound_users_by_age.empty:
        st.warning("No hay datos disponibles para mostrar en la métrica por edad.")
    else:
        st.bar_chart(inbound_users_by_age)

    st.header("Número de llamadas inbound por duración de las llamadas (rangos de 5 minutos)")
    if inbound_users_by_call_duration.empty:
        st.warning("No hay datos disponibles para mostrar en la métrica por duración de llamadas.")
    else:
        st.bar_chart(inbound_users_by_call_duration)

    st.header("Número de llamadas inbound por número de llamadas totales en el mes")
    if call_distribution_table.empty:
        st.warning("No hay datos disponibles para mostrar en la tabla.")
    else:
        st.dataframe(call_distribution_table.style.set_caption("Distribución por género y rangos de edad"))

elif page_selection == "Llamadas Outbound":
    # Obtener métricas
    outbound_users_percentage_by_week = get_outbound_calls_by_week()
    outbound_calls_by_duration = get_outbound_calls_by_duration()
    outbound_calls_by_age = get_outbound_calls_by_age()
    outbound_calls_by_gender = get_outbound_calls_by_gender()

    # Visualización en Streamlit
    st.title("Métricas de Usuarios Outbound")

    st.header("Número de llamadas contactados outbound por semana")
    if outbound_users_percentage_by_week.empty:
        st.warning("No hay datos disponibles para mostrar en esta métrica.")
    else:
        st.bar_chart(outbound_users_percentage_by_week)

    st.header("Número de llamadas outbound por duración (rangos de 5 minutos)")
    if outbound_calls_by_duration.empty:
        st.warning("No hay datos disponibles para mostrar en esta métrica.")
    else:
        st.bar_chart(outbound_calls_by_duration)

    st.header("Número de llamadas outbound por edad (rangos de 5 años desde 60 años)")
    if outbound_calls_by_age.empty:
        st.warning("No hay datos disponibles para mostrar en esta métrica.")
    else:
        st.bar_chart(outbound_calls_by_age)

    st.header("Número de llamadas outbound por género")
    if outbound_calls_by_gender.empty:
        st.warning("No hay datos disponibles para mostrar en esta métrica.")
    else:
        st.bar_chart(outbound_calls_by_gender)

elif page_selection == "Tiempos de llamadas":
    # Visualización en Streamlit
    st.title("Métricas de Llamadas")

    # Encabezados
    average_call_duration = get_average_call_duration()
    st.subheader(f"Duración de llamada promedio total: {average_call_duration} minutos")

    average_call_duration_by_gender = get_average_call_duration_by_gender()
    if average_call_duration_by_gender.empty:
        st.warning("No hay datos disponibles para la duración promedio por género.")
    else:
        st.subheader("Duración de llamada promedio por género")
        for gender, duration in average_call_duration_by_gender.items():
            st.write(f"{gender.capitalize()}: {duration:.3f} minutos")

    # Gráficas
    st.header("Duración promedio por edad (rangos de 5 años)")
    average_duration_by_age = get_average_call_duration_by_age()
    if average_duration_by_age.empty:
        st.warning("No hay datos disponibles para la duración promedio por edad.")
    else:
        st.bar_chart(average_duration_by_age)

    st.header("Duración promedio por día de la semana")
    average_duration_by_day = get_average_call_duration_by_day_of_week()
    if average_duration_by_day.empty:
        st.warning("No hay datos disponibles para la duración promedio por día de la semana.")
    else:
        st.bar_chart(average_duration_by_day)

    st.header("Duración promedio por hora del día")
    average_duration_by_hour = get_average_call_duration_by_hour_of_day()
    if average_duration_by_hour.empty:
        st.warning("No hay datos disponibles para la duración promedio por hora del día.")
    else:
        st.bar_chart(average_duration_by_hour)

    st.header("Porcentaje de conversación promedio: Chatbot vs Cliente por género")
    chatbot_vs_human_by_gender = get_chatbot_vs_human_percentage_by_gender()
    if chatbot_vs_human_by_gender.empty:
        st.warning("No hay datos disponibles para el porcentaje de conversación por género.")
    else:
        st.bar_chart(chatbot_vs_human_by_gender)

    st.header("Porcentaje de conversación promedio: Chatbot vs Cliente por edad")
    chatbot_vs_human_by_age = get_chatbot_vs_human_percentage_by_age()
    if chatbot_vs_human_by_age.empty:
        st.warning("No hay datos disponibles para el porcentaje de conversación por edad.")
    else:
        st.bar_chart(chatbot_vs_human_by_age)

elif page_selection == "Tiempos por temas":
    # Main Streamlit Visualization
    st.title("Análisis de Conversación por Tema")

    # Fetch data
    df = get_data_by_topic()

    if df.empty:
        st.warning("No hay datos disponibles para análisis.")
    else:
        # 1. Porcentaje de tiempo promedio del chatbot vs. cliente por tema
        st.header("Porcentaje de tiempo promedio del Chatbot vs Cliente por Tema")
        percentage_by_topic = get_percentage_time_by_topic(df)
        # Resetear el índice para trabajar con Altair
        percentage_by_topic_reset = percentage_by_topic.reset_index()

        # Convertir el DataFrame a formato largo
        percentage_by_topic_long = percentage_by_topic_reset.melt(
            id_vars=["topic"], 
            value_vars=["bot_percentage", "persona_percentage"],
            var_name="Type",
            value_name="Percentage"
        )

        # Crear un gráfico de barras con Altair
        chart = alt.Chart(percentage_by_topic_long).mark_bar().encode(
            x=alt.X("topic:N", sort=percentage_by_topic_reset["topic"].tolist(), title="Temas"),
            y=alt.Y("Percentage:Q", title="Porcentaje"),
            color=alt.Color("Type:N", legend=alt.Legend(title="Tipo")),
            tooltip=["topic", "Type", "Percentage"]
        ).properties(
            width=800,
            height=400,
            title="Porcentaje de tiempo promedio por tema"
        )

        # Mostrar el gráfico
        st.altair_chart(chart, use_container_width=True)

        # Mostrar la gráfica de torta
        st.header("Porcentaje de tiempo por tema")
        generate_pie_chart_by_topic(df)

        # Calcular los porcentajes por tema y rangos de edad
        percentage_by_age_ranges = get_percentage_time_by_age_ranges(df)

        # Mostrar la tabla resultante
        st.header("Porcentaje de tiempo por tema y rangos de edad")
        # Generar gráfico si hay datos disponibles
        if not percentage_by_age_ranges.empty:
            # Crear el gráfico de barras con Altair
            chart = alt.Chart(percentage_by_age_ranges).mark_bar().encode(
                x=alt.X("topic:N", sort=percentage_by_age_ranges["topic"].unique().tolist(), title="Temas"),
                y=alt.Y("percentage:Q", title="Porcentaje"),
                color=alt.Color("age_range:N", legend=alt.Legend(title="Rango de Edad")),
                tooltip=["topic", "age_range", "percentage"]
            ).properties(
                width=800,
                height=400,
                #title="Porcentaje de tiempo por tema y rangos de edad"
            )

            # Mostrar el gráfico
            #st.header("Porcentaje de tiempo por tema y rangos de edad")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para generar el gráfico.")

        #st.title("Análisis de tiempo por género")

        # Calcular los porcentajes por tema y género
        percentage_by_gender = get_percentage_time_by_gender(df)

        # Generar gráfico si hay datos disponibles
        if not percentage_by_gender.empty:
            # Crear el gráfico de barras con Altair
            chart = alt.Chart(percentage_by_gender).mark_bar().encode(
                x=alt.X("topic:N", sort=percentage_by_gender["topic"].unique().tolist(), title="Temas"),
                y=alt.Y("percentage:Q", title="Porcentaje"),
                color=alt.Color("user_gender:N", legend=alt.Legend(title="Género")),
                tooltip=["topic", "user_gender", "percentage"]
            ).properties(
                width=800,
                height=400,
                #title="Porcentaje de tiempo por tema y género"
            )

            # Mostrar el gráfico
            st.header("Porcentaje de tiempo por tema y género")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para generar el gráfico.")