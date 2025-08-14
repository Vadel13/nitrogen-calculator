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
    results = calculator.calculate(p_n2, purity, pressure)
    
    if results["warnings"]:
        for warning in results["warnings"]:
            st.warning(warning)
    
    st.subheader("Основные результаты")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Производительность азота", f"{results['p_n2']:.2f} Нм³/ч")
        st.metric("Чистота азота", f"{results['purity']:.2f} %")
        st.metric("Концентрация O₂", f"{results['o2_ppm']:.0f} ppm")
    with col2:
        st.metric("Коэффициент извлечения (η)", f"{results['eta'] * 100:.1f} %")
        st.metric("Требуемый расход воздуха", f"{results['q_air']:.1f} Нм³/ч")
        st.metric("Удельный расход воздуха", f"{results['specific_flow']:.2f} Нм³/Нм³ азота")
    
    if results.get("recommendations"):
        st.subheader("Рекомендации")
        for rec in results["recommendations"]:
            st.info(rec)
    
    if "compressor_model" in results:
        st.subheader("Подбор компрессоров")
        st.write(f"**Рекомендуемая модель:** {results['compressor_model']}")
        st.write(f"**Количество:** {results['compressor_count']} шт.")
        st.write(f"**Производительность одного компрессора:** {results['flow_per_unit']:.1f} м³/мин")
        st.write(f"**Суммарная производительность:** {results['total_flow']:.1f} м³/мин")
        st.write(f"**Избыток производительности:** {results['excess']:.2f} м³/мин")
        
        if results.get("alternatives"):
            st.subheader("Альтернативные варианты")
            for alt in results["alternatives"]:
                st.write(f"- **Модель {alt[0]}**: {alt[1]} шт. (производительность: {alt[2]} м³/мин)")
    
    st.subheader("Зависимость расхода воздуха от чистоты азота")
    fig, ax = plt.subplots()
    
    purities = np.linspace(95, 99.999, 50)
    air_flows = []
    
    for p in purities:
        purities_sorted = sorted(NitrogenCalculator.PURITY_DATA.keys())
        lower = max([p_val for p_val in purities_sorted if p_val <= p], default=95.0)
        upper = min([p_val for p_val in purities_sorted if p_val >= p], default=99.999)
        
        if p in NitrogenCalculator.PURITY_DATA:
            eta = NitrogenCalculator.PURITY_DATA[p]["eta"]
        else:
            eta_lower = NitrogenCalculator.PURITY_DATA[lower]["eta"]
            eta_upper = NitrogenCalculator.PURITY_DATA[upper]["eta"]
            eta = eta_lower + (eta_upper - eta_lower) * ((p - lower) / (upper - lower))
        
        q_air = p_n2 / (eta * calculator.C_N2)
        air_flows.append(q_air)
    
    ax.plot(purities, air_flows, 'b-', linewidth=2)
    ax.plot(results["purity"], results["q_air"], 'ro', markersize=8)
    ax.annotate(
        f'Текущий расчет\n({results["purity"]}%, {results["q_air"]:.1f} Нм³/ч)',
        xy=(results["purity"], results["q_air"]),
        xytext=(results["purity"] - 1, results["q_air"] + 50),
        arrowprops=dict(facecolor='black', shrink=0.05)
    )
    
    ax.set_xlabel("Чистота азота (%)")
    ax.set_ylabel("Расход воздуха (Нм³/ч)")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    st.pyplot(fig)
else:
    st.info("ℹ️ Введите параметры в левой панели и нажмите кнопку 'Рассчитать'")