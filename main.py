import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from calculator import NitrogenCalculator

st.set_page_config(
    page_title="Расчет установки генерации азота",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Расчет параметров генератора азота (PSA)")

with st.sidebar:
    st.header("Входные параметры")
    p_n2 = st.number_input("Производительность азота (Нм³/ч)", min_value=0.1, value=100.0, step=10.0)
    purity = st.number_input("Чистота азота (%)", min_value=95.0, max_value=100.0, value=99.5, step=0.1)
    pressure = st.number_input("Рабочее давление (бар)", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
    calculate_btn = st.button("Рассчитать")

calculator = NitrogenCalculator()

if calculate_btn:
    # ... остальной код из app.py ...