import math

class NitrogenCalculator:
    PURITY_DATA = {
        95.0: {"o2_ppm": 50000, "eta": 0.60, "range": (0.55, 0.65)},
        99.0: {"o2_ppm": 10000, "eta": 0.50, "range": (0.45, 0.55)},
        99.5: {"o2_ppm": 5000, "eta": 0.45, "range": (0.40, 0.48)},
        99.8: {"o2_ppm": 2000, "eta": 0.42, "range": (0.38, 0.45)},
        99.9: {"o2_ppm": 1000, "eta": 0.38, "range": (0.35, 0.42)},
        99.95: {"o2_ppm": 500, "eta": 0.35, "range": (0.32, 0.38)},
        99.99: {"o2_ppm": 100, "eta": 0.32, "range": (0.28, 0.35)},
        99.999: {"o2_ppm": 10, "eta": 0.25, "range": (0.20, 0.30)}
    }
    
    COMPRESSORS_10BAR = [
        ("UDT355A-10", 67.7), ("UDT315A-10", 53), ("UDT280A-10", 50),
        ("UDT250A-10", 46), ("UDT250A-10B", 46), ("UDT220A-10", 41),
        ("UDT220A-10B", 41), ("UDT200A-10", 37), ("UDT200A-10B", 37),
        ("UDT160A-10", 27), ("UDT132A-10", 23), ("UDT110A-10", 20.3),
        ("UDT90A-10", 15.2), ("UDT75A-10", 13.3)
    ]

    def __init__(self):
        self.C_N2 = 0.781
        self.compressors = sorted(self.COMPRESSORS_10BAR, key=lambda x: x[1], reverse=True)
    
    def calculate(self, p_n2, purity, pressure):
        results = {"warnings": []}
        
        if purity < 95 or purity > 100:
            results["warnings"].append("⚠️ Чистота вне типичного диапазона (95-99.999%)")
        if pressure > 9.5:
            results["warnings"].append("⚠️ Для давления > 9.5 бар требуется специальное оборудование")
        
        # Находим ближайшие значения для интерполяции
        purities = sorted(self.PURITY_DATA.keys())
        lower = max([p for p in purities if p <= purity], default=95.0)
        upper = min([p for p in purities if p >= purity], default=99.999)
        
        # Берем готовое значение или интерполируем
        if purity in self.PURITY_DATA:
            eta = self.PURITY_DATA[purity]["eta"]
        else:
            eta_lower = self.PURITY_DATA[lower]["eta"]
            eta_upper = self.PURITY_DATA[upper]["eta"]
            eta = eta_lower + (eta_upper - eta_lower) * ((purity - lower) / (upper - lower))
        
        # Основные расчеты
        q_air = p_n2 / (eta * self.C_N2)
        specific_flow = q_air / p_n2
        
        # Сохраняем результаты
        results.update({
            "p_n2": p_n2,
            "purity": purity,
            "pressure": pressure,
            "o2_ppm": 10000 * (100 - purity),
            "eta": eta,
            "q_air": q_air,
            "specific_flow": specific_flow
        })
        
        # Подбор компрессоров (только для давления <= 9.5 бар)
        if pressure <= 9.5:
            compressors_result = self._select_compressors(q_air)
            results.update(compressors_result)
        
        # Формируем рекомендации
        recommendations = []
        if purity >= 99.95:
            recommendations.append("• Для сверхвысокой чистоты рассмотрите криогенные технологии")
        elif purity >= 99.9:
            recommendations.append("• Используйте двухступенчатую систему PSA для экономии энергии")
        else:
            recommendations.append("• Оптимальная конфигурация: стандартный генератор PSA")
        
        if pressure < 7:
            recommendations.append("• Увеличьте давление до 7-9.5 бар для повышения эффективности")
        elif pressure > 9.5:
            recommendations.append("• Для давления > 9.5 бар требуется компрессор высокого давления")
        
        results["recommendations"] = recommendations
        return results
    
    def _select_compressors(self, q_air):
        q_air_m3_min = q_air / 60  # Переводим в м³/мин
        
        # Ищем лучший вариант компрессора
        best_model, best_count, best_flow = None, None, None
        min_excess = float('inf')  # Ставим очень большое число
        
        # Перебираем все компрессоры
        for model, flow in self.compressors:
            # Сколько нужно таких компрессоров
            count = math.ceil(q_air_m3_min / flow)
            # Общая производительность
            total_flow = count * flow
            # На сколько больше, чем нужно
            excess = total_flow - q_air_m3_min
            
            # Ищем вариант с минимальным избытком
            if excess < min_excess:
                best_model = model
                best_count = count
                best_flow = flow
                min_excess = excess
        
        # Ищем альтернативные варианты (с меньшим количеством)
        alternatives = []
        for model, flow in self.compressors:
            if flow <= best_flow:  # Пропускаем менее мощные
                continue
            new_count = math.ceil(q_air_m3_min / flow)
            if new_count < best_count:  # Если количество меньше
                alternatives.append((model, new_count, flow))
        
        return {
            "compressor_model": best_model,
            "compressor_count": best_count,
            "flow_per_unit": best_flow,
            "total_flow": best_count * best_flow,
            "excess": min_excess,
            "alternatives": alternatives
        }