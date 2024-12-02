import streamlit as st
from inbound import *
# Se pueden importar otros módulos en el futuro, como 'outbound.py'

# Crear menú de selección de páginas
menu_options = ["Llamadas Inbound", "Llamadas Outbound", "Otra Página"]
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
    st.title("Métricas de Usuarios Outbound")
    st.write("Esta página estará dedicada a mostrar métricas relacionadas con llamadas outbound.")
    # Implementar métricas para llamadas outbound cuando se construyan las funciones correspondientes
    # Por ejemplo:
    # outbound_users_by_day = get_outbound_calls_by_day()
    # st.bar_chart(outbound_users_by_day)

elif page_selection == "Otra Página":
    st.title("Otra Página")
    st.write("Esta es otra página que puede contener cualquier contenido adicional en el futuro.")
