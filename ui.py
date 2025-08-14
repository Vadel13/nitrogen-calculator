from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTabWidget, QStatusBar,
    QFormLayout, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from calculator import NitrogenCalculator

class CalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчет установки генерации азота")
        self.setWindowIcon(QIcon("nitrogen.png"))  # Можно добавить иконку позже
        self.resize(900, 700)
        self.setup_ui()
        
    def setup_ui(self):
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("Расчет параметров генератора азота (PSA)")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px;
        """)
        main_layout.addWidget(title)
        
        # Поля ввода
        input_group = QGroupBox("Входные параметры")
        input_layout = QGridLayout(input_group)
        
        # Создаем поля для ввода
        self.p_n2_input = QLineEdit()
        self.purity_input = QLineEdit()
        self.pressure_input = QLineEdit()
        
        # Добавляем подписи
        input_layout.addWidget(QLabel("Производительность азота (Нм³/ч):"), 0, 0)
        input_layout.addWidget(self.p_n2_input, 0, 1)
        
        input_layout.addWidget(QLabel("Чистота азота (%):"), 1, 0)
        input_layout.addWidget(self.purity_input, 1, 1)
        
        input_layout.addWidget(QLabel("Рабочее давление (бар):"), 2, 0)
        input_layout.addWidget(self.pressure_input, 2, 1)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Рассчитать")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        calc_btn.clicked.connect(self.calculate)
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_form)
        
        btn_layout.addWidget(calc_btn)
        btn_layout.addWidget(clear_btn)
        input_layout.addLayout(btn_layout, 3, 0, 1, 2)
        
        main_layout.addWidget(input_group)
        
        # Вкладки для результатов
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Создаем вкладки
        self.setup_summary_tab()
        self.setup_compressors_tab()
        self.setup_graph_tab()
        
        # Статус бар внизу окна
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Применяем стили
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 12px;
                background-color: #f5f7fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cbd2d9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cbd2d9;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QTabWidget::pane {
                border: 1px solid #cbd2d9;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #e4e7eb;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QLabel {
                padding: 3px;
            }
        """)
    
    def setup_summary_tab(self):
        """Вкладка с основными результатами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Предупреждения
        self.warnings_group = QGroupBox("Предупреждения")
        self.warnings_layout = QVBoxLayout(self.warnings_group)
        layout.addWidget(self.warnings_group)
        
        # Основные результаты
        results_group = QGroupBox("Результаты расчета")
        results_layout = QFormLayout(results_group)
        results_layout.setVerticalSpacing(10)
        
        self.result_labels = {
            "p_n2": QLabel("-"),
            "purity": QLabel("-"),
            "o2_ppm": QLabel("-"),
            "eta": QLabel("-"),
            "q_air": QLabel("-"),
            "specific_flow": QLabel("-")
        }
        
        # Делаем текст жирным
        for label in self.result_labels.values():
            label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        results_layout.addRow("Производительность азота:", self.result_labels["p_n2"])
        results_layout.addRow(QLabel("Нм³/ч"))
        
        results_layout.addRow("Чистота азота:", self.result_labels["purity"])
        results_layout.addRow(QLabel("%"))
        
        results_layout.addRow("Концентрация O₂:", self.result_labels["o2_ppm"])
        results_layout.addRow(QLabel("ppm"))
        
        results_layout.addRow("Коэффициент извлечения (η):", self.result_labels["eta"])
        results_layout.addRow(QLabel("%"))
        
        results_layout.addRow("Требуемый расход воздуха:", self.result_labels["q_air"])
        results_layout.addRow(QLabel("Нм³/ч"))
        
        results_layout.addRow("Удельный расход воздуха:", self.result_labels["specific_flow"])
        results_layout.addRow(QLabel("Нм³/Нм³ азота"))
        
        layout.addWidget(results_group)
        
        # Рекомендации
        self.recommendations_group = QGroupBox("Рекомендации")
        self.recommendations_layout = QVBoxLayout(self.recommendations_group)
        layout.addWidget(self.recommendations_group)
        
        self.tabs.addTab(tab, "Основные результаты")
    
    def setup_compressors_tab(self):
        """Вкладка с подбором компрессоров"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Результаты подбора
        self.compressors_group = QGroupBox("Подбор компрессоров")
        compressors_layout = QFormLayout(self.compressors_group)
        
        self.compressor_labels = {
            "model": QLabel("-"),
            "count": QLabel("-"),
            "flow": QLabel("-"),
            "total_flow": QLabel("-"),
            "excess": QLabel("-")
        }
        
        for label in self.compressor_labels.values():
            label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        compressors_layout.addRow("Рекомендуемая модель:", self.compressor_labels["model"])
        compressors_layout.addRow("Количество:", self.compressor_labels["count"])
        compressors_layout.addRow("Производительность одного:", self.compressor_labels["flow"])
        compressors_layout.addRow("Суммарная производительность:", self.compressor_labels["total_flow"])
        compressors_layout.addRow("Избыток производительности:", self.compressor_labels["excess"])
        
        layout.addWidget(self.compressors_group)
        
        # Альтернативные варианты
        self.alternatives_group = QGroupBox("Альтернативные варианты")
        self.alternatives_layout = QVBoxLayout(self.alternatives_group)
        layout.addWidget(self.alternatives_group)
        
        self.tabs.addTab(tab, "Оборудование")
    
    def setup_graph_tab(self):
        """Вкладка с графиком"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Создаем область для графика
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.tabs.addTab(tab, "Графики")
    
    def calculate(self):
        """Обработка нажатия кнопки Рассчитать"""
        try:
            # Получаем значения из полей ввода
            p_n2 = float(self.p_n2_input.text())
            purity = float(self.purity_input.text())
            pressure = float(self.pressure_input.text())
            
            # Выполняем расчет
            calculator = NitrogenCalculator()
            self.results = calculator.calculate(p_n2, purity, pressure)
            
            # Обновляем интерфейс
            self.update_ui()
            
            self.status_bar.showMessage("Расчет выполнен успешно", 3000)
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректные числовые значения")
            self.status_bar.showMessage("Ошибка ввода данных", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_bar.showMessage(f"Ошибка: {str(e)}", 5000)
    
    def update_ui(self):
        """Обновление интерфейса на основе результатов расчета"""
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Выводим предупреждения
        for warning in self.results["warnings"]:
            label = QLabel(warning)
            label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.warnings_layout.addWidget(label)
        
        # Обновляем основные результаты
        self.result_labels["p_n2"].setText(f"{self.results['p_n2']:.2f}")
        self.result_labels["purity"].setText(f"{self.results['purity']:.2f}")
        self.result_labels["o2_ppm"].setText(f"{self.results['o2_ppm']:.0f}")
        self.result_labels["eta"].setText(f"{self.results['eta'] * 100:.1f}")
        self.result_labels["q_air"].setText(f"{self.results['q_air']:.1f}")
        self.result_labels["specific_flow"].setText(f"{self.results['specific_flow']:.2f}")
        
        # Выводим рекомендации
        for recommendation in self.results.get("recommendations", []):
            label = QLabel(recommendation)
            label.setStyleSheet("padding: 5px;")
            self.recommendations_layout.addWidget(label)
        
        # Обновляем данные по компрессорам (если есть)
        if "compressor_model" in self.results:
            self.compressor_labels["model"].setText(self.results["compressor_model"])
            self.compressor_labels["count"].setText(f"{self.results['compressor_count']} шт.")
            self.compressor_labels["flow"].setText(f"{self.results['flow_per_unit']:.1f} м³/мин")
            self.compressor_labels["total_flow"].setText(f"{self.results['total_flow']:.1f} м³/мин")
            self.compressor_labels["excess"].setText(f"{self.results['excess']:.2f} м³/мин")
            
            # Выводим альтернативы
            for alt in self.results.get("alternatives", []):
                text = f"Модель {alt[0]}: {alt[1]} шт. (производительность: {alt[2]} м³/мин)"
                label = QLabel(text)
                self.alternatives_layout.addWidget(label)
        
        # Обновляем график
        self.update_graph()
    
    def update_graph(self):
        """Обновление графика зависимости расхода от чистоты"""
        # Очищаем предыдущий график
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Готовим данные для графика
        purities = np.linspace(95, 99.999, 50)
        air_flows = []
        
        # Для каждой чистоты рассчитываем расход
        for purity in purities:
            # Используем ту же логику, что и в основном расчете
            purities_sorted = sorted(NitrogenCalculator.PURITY_DATA.keys())
            lower = max([p for p in purities_sorted if p <= purity], default=95.0)
            upper = min([p for p in purities_sorted if p >= purity], default=99.999)
            
            if purity in NitrogenCalculator.PURITY_DATA:
                eta = NitrogenCalculator.PURITY_DATA[purity]["eta"]
            else:
                eta_lower = NitrogenCalculator.PURITY_DATA[lower]["eta"]
                eta_upper = NitrogenCalculator.PURITY_DATA[upper]["eta"]
                eta = eta_lower + (eta_upper - eta_lower) * ((purity - lower) / (upper - lower))
            
            q_air = self.results["p_n2"] / (eta * NitrogenCalculator().C_N2)
            air_flows.append(q_air)
        
        # Строим график
        ax.plot(purities, air_flows, 'b-', linewidth=2)
        
        # Отмечаем точку текущего расчета
        ax.plot(self.results["purity"], self.results["q_air"], 'ro', markersize=8)
        ax.annotate(
            f'Текущий расчет\n({self.results["purity"]}%, {self.results["q_air"]:.1f} Нм³/ч)',
            xy=(self.results["purity"], self.results["q_air"]),
            xytext=(self.results["purity"] - 1, self.results["q_air"] + 50),
            arrowprops=dict(facecolor='black', shrink=0.05)
        )
        
        # Настройки графика
        ax.set_title("Зависимость расхода воздуха от чистоты азота", fontsize=14)
        ax.set_xlabel("Чистота азота (%)", fontsize=12)
        ax.set_ylabel("Расход воздуха (Нм³/ч)", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Обновляем холст
        self.canvas.draw()
    
    def clear_form(self):
        """Очистка формы"""
        self.p_n2_input.clear()
        self.purity_input.clear()
        self.pressure_input.clear()
        self.clear_results()
        self.status_bar.showMessage("Поля очищены", 2000)
    
    def clear_results(self):
        """Очистка результатов"""
        # Очищаем предупреждения
        for i in reversed(range(self.warnings_layout.count())): 
            self.warnings_layout.itemAt(i).widget().deleteLater()
        
        # Сбрасываем значения результатов
        for label in self.result_labels.values():
            label.setText("-")
        
        # Очищаем рекомендации
        for i in reversed(range(self.recommendations_layout.count())): 
            self.recommendations_layout.itemAt(i).widget().deleteLater()
        
        # Сбрасываем значения компрессоров
        for label in self.compressor_labels.values():
            label.setText("-")
        
        # Очищаем альтернативы
        for i in reversed(range(self.alternatives_layout.count())): 
            self.alternatives_layout.itemAt(i).widget().deleteLater()
        
        # Очищаем график
        self.figure.clear()
        self.canvas.draw()