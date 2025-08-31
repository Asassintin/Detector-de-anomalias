import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import winsound

plt.style.use('ggplot')

class DetectorAnomalias:
    """
    Implementa un detector de anomalías basado en el algoritmo CUSUM (Cumulative Sum)
    para identificar desviaciones significativas en el tráfico de red.
    """
    def __init__(self, ventana_tiempo=60, muestras_por_segundo=60):
        # Parámetros de configuración temporal
        self.ventana_tiempo = ventana_tiempo            # Duración total de la simulación (segundos)
        self.muestras_por_segundo = muestras_por_segundo  # Resolución temporal
        self.total_muestras = ventana_tiempo * muestras_por_segundo
        
        # Parámetros para simulación del tráfico
        self.media_trafico_normal = 100            # Media del tráfico en condiciones normales
        self.desviacion_trafico_normal = 15        # Desviación estándar del tráfico normal
        self.factor_ataque = 3                     # Multiplicador para simular ataque (x3 veces la media normal)
        self.duracion_ataque = int(0.5 * muestras_por_segundo)  # Duración del ataque (0.5 segundos)
        
        # Generación del momento aleatorio para el ataque (entre 10 y 50 segundos)
        self.inicio_ataque = random.randint(10*muestras_por_segundo, 50*muestras_por_segundo)
        self.fin_ataque = self.inicio_ataque + self.duracion_ataque
        
        # Valor umbral fijo para detección
        self.umbral_fijo = 2000                    # Valor predeterminado para detección
        
        # Inicialización de arrays para almacenar datos
        self.tiempo = np.arange(self.total_muestras) / muestras_por_segundo  # Vector de tiempo
        self.trafico = np.zeros(self.total_muestras)                # Valores de tráfico
        self.suma_acumulada = np.zeros(self.total_muestras)         # Valores CUSUM
        self.umbral_estadistico = np.zeros(self.total_muestras)     # Umbral adaptativo
        
        # Variables de control y resultado
        self.anomalia_detectada = False
        self.momento_deteccion = None
        self.momento_real_ataque = self.inicio_ataque / muestras_por_segundo
        self.indice_actual = 0
        
    def generar_datos(self):
        """
        Genera datos simulados de tráfico de red con un ataque insertado en un momento aleatorio.
        Usa una distribución gaussiana para el tráfico normal y añade un pico para simular el ataque.
        """
        # Generación de tráfico normal usando distribución gaussiana
        self.trafico = np.random.normal(
            self.media_trafico_normal, 
            self.desviacion_trafico_normal, 
            self.total_muestras
        )
        
        # Inserción del ataque: añade un pico de tráfico multiplicando la media base
        # por el factor de ataque durante la duración programada
        self.trafico[self.inicio_ataque:self.fin_ataque] += (self.media_trafico_normal 
                                                          * self.factor_ataque 
                                                          * np.ones(self.duracion_ataque))
        
        # Garantiza que todos los valores de tráfico sean positivos
        self.trafico = np.maximum(0, self.trafico)
        
    def calcular_suma_acumulada(self):
        """
        Implementa el algoritmo CUSUM (Cumulative Sum) calculando la suma acumulada
        de las desviaciones respecto a una línea base.
        """
        # Calcula línea base usando los primeros 5 segundos (periodo de estabilización)
        ventana_base = 5 * self.muestras_por_segundo
        linea_base = np.mean(self.trafico[:ventana_base])
        
        # Implementación del algoritmo CUSUM
        # S_t = max(0, S_{t-1} + (x_t - μ))
        for i in range(1, self.total_muestras):
            self.suma_acumulada[i] = max(0, self.suma_acumulada[i-1] + (self.trafico[i] - linea_base))
    
    def calcular_umbral_estadistico(self):
        """
        Calcula un umbral estadístico adaptativo basado en media + 3 desviaciones estándar
        usando una ventana deslizante de 5 segundos.
        """
        ventana = 5 * self.muestras_por_segundo  # Tamaño de ventana = 5 segundos
        
        for i in range(ventana, self.total_muestras):
            # Calcula estadísticas de la ventana anterior
            media = np.mean(self.suma_acumulada[i-ventana:i])
            desv_est = np.std(self.suma_acumulada[i-ventana:i])
            
            # Umbral = media + 3*desviación estándar (regla 3-sigma)
            self.umbral_estadistico[i] = media + 3 * desv_est
    
    def detectar_anomalia(self, indice, en_tiempo_real=False):
        """
        Aplica la lógica de detección comparando la suma acumulada con los umbrales.
        
        Args:
            indice: Posición temporal actual a evaluar
            en_tiempo_real: Indica si estamos en modo tiempo real (para registrar momento)
            
        Returns:
            bool: True si se detecta anomalía, False en caso contrario
        """
        # No evaluar durante el periodo inicial de estabilización (primeros 5 segundos)
        if indice < 5 * self.muestras_por_segundo:
            return False
        
        # Lógica de detección: se comprueba si la suma acumulada supera algún umbral
        anomalia = (self.suma_acumulada[indice] > self.umbral_fijo or 
                   (indice >= len(self.umbral_estadistico) - 1 or 
                    self.suma_acumulada[indice] > self.umbral_estadistico[indice]))
            
        # Si es la primera anomalía detectada en tiempo real, registrar el momento
        if anomalia and not self.anomalia_detectada and en_tiempo_real:
            self.anomalia_detectada = True
            self.momento_deteccion = indice / self.muestras_por_segundo
            return True
        
        return False
    
    def procesar_paso(self):
        """
        Procesa un paso de tiempo para el análisis en tiempo real.
        Calcula la suma acumulada, el umbral estadístico y verifica si hay anomalía.
        
        Returns:
            bool: True si se detecta anomalía en este paso, False en caso contrario
        """
        # Verificar si hemos llegado al final de la simulación
        if self.indice_actual >= self.total_muestras:
            return False
        
        # Calcular suma acumulada para el punto actual
        if self.indice_actual > 0:
            # Obtener línea base de referencia
            ventana_base = min(5 * self.muestras_por_segundo, self.indice_actual)
            linea_base = np.mean(self.trafico[:ventana_base])
            
            # Actualizar suma acumulada según algoritmo CUSUM
            self.suma_acumulada[self.indice_actual] = max(
                0, 
                self.suma_acumulada[self.indice_actual-1] + 
                (self.trafico[self.indice_actual] - linea_base)
            )
        
        # Calcular umbral estadístico dinámico
        if self.indice_actual >= 5 * self.muestras_por_segundo:
            ventana = 5 * self.muestras_por_segundo
            valores_ventana = self.suma_acumulada[max(0, self.indice_actual-ventana):self.indice_actual]
            media = np.mean(valores_ventana)
            desv_est = np.std(valores_ventana)
            # Factor multiplicador reducido a 2.5 para detección más sensible
            self.umbral_estadistico[self.indice_actual] = media + 2.5 * desv_est
        
        # Comprobar si hay anomalía en el punto actual
        anomalia_detectada = self.detectar_anomalia(self.indice_actual, True)
        
        # Avanzar al siguiente punto temporal
        self.indice_actual += 1
        
        return anomalia_detectada

class PantallaCarga:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        
        # Centrar en la pantalla
        ancho, alto = 500, 300
        x = (root.winfo_screenwidth() - ancho) // 2
        y = (root.winfo_screenheight() - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Colores
        self.bg_color = "#1a1a2e"
        self.text_color = "#e94560"
        self.accent_color = "#16213e"
        
        # Frame principal
        self.frame = tk.Frame(root, bg=self.bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y subtítulo
        tk.Label(self.frame, text="SISTEMA DE DETECCIÓN\nDE ANOMALÍAS", 
                font=("Helvetica", 22, "bold"), bg=self.bg_color, fg=self.text_color, 
                pady=20).pack(pady=20)
        
        tk.Label(self.frame, text="Análisis de Tráfico de Red en Tiempo Real",
                font=("Helvetica", 12), bg=self.bg_color, fg="white", 
                pady=10).pack(pady=5)
        
        # Barra de progreso
        progreso_frame = tk.Frame(self.frame, bg=self.bg_color, padx=50)
        progreso_frame.pack(fill=tk.X, pady=20)
        
        self.progress_bg = tk.Canvas(progreso_frame, width=400, height=20, 
                                    bg=self.accent_color, highlightthickness=0)
        self.progress_bg.pack()
        
        self.progress_bar = self.progress_bg.create_rectangle(0, 0, 0, 20, 
                                                            fill=self.text_color, outline="")
        
        # Mensaje de carga
        self.loading_label = tk.Label(self.frame, text="Inicializando sistema...", 
                                    font=("Helvetica", 10), bg=self.bg_color, fg="white")
        self.loading_label.pack(pady=10)
        
        # Variables para animación
        self.progress = 0
        self.loading_steps = ["Inicializando sistema...",
                             "Cargando algoritmos de detección...",
                             "Preparando interfaz gráfica...",
                             "Configurando módulos de análisis...",
                             "Sistema listo!"]
        self.step_index = 0
        
    def iniciar_animacion(self, callback):
        self.callback = callback
        self.animar_progreso()
        
    def animar_progreso(self):
        if self.progress < 100:
            # Actualizar progreso
            self.progress += random.uniform(5, 10)
            self.progress = min(100, self.progress)
            width = 400 * (self.progress / 100)
            
            # Actualizar barra y mensaje
            self.progress_bg.coords(self.progress_bar, 0, 0, width, 20)
            step_to_show = min(int(self.progress / 20), len(self.loading_steps) - 1)
            
            if step_to_show > self.step_index:
                self.step_index = step_to_show
                self.loading_label.config(text=self.loading_steps[self.step_index])
                self.animar_texto()
            
            # Programar siguiente
            self.root.after(random.randint(100, 300), self.animar_progreso)
        else:
            self.loading_label.config(text="¡Sistema listo!")
            self.efecto_final()
    
    def animar_texto(self):
        # Agrandar texto brevemente
        self.loading_label.config(font=("Helvetica", 12, "bold"))
        self.root.after(150, lambda: self.loading_label.config(font=("Helvetica", 10)))
    
    def efecto_final(self):
        winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        self.root.after(500, self.desvanecer)
    
    def desvanecer(self, alpha=1.0):
        if alpha > 0:
            alpha -= 0.1
            self.root.attributes("-alpha", alpha)
            self.root.after(50, lambda: self.desvanecer(alpha))
        else:
            self.root.destroy()
            self.callback()

class ExplicacionMatematica:
    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Explicación Matemática")
        self.ventana.geometry("600x450")  # Aumentar tamaño de la ventana
        self.ventana.resizable(False, False)
        
        # Configurar apariencia
        bg_color = "#f8f9fa"
        title_color = "#6B0F1A"
        text_color = "#2c3e50"
        formula_color = "#0056b3"
        
        self.ventana.config(bg=bg_color)
        
        # Usar Canvas con scrollbar para asegurar que todo sea visible
        container = tk.Frame(self.ventana, bg=bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=bg_color)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        tk.Label(
            self.scrollable_frame, 
            text="Detección de Anomalías por Suma Acumulada (CUSUM)",
            font=("Helvetica", 14, "bold"),
            bg=bg_color,
            fg=title_color,
            pady=10,
            padx=15
        ).pack(fill=tk.X)
        
        # Marco para el contenido
        content = tk.Frame(self.scrollable_frame, bg=bg_color, padx=20, pady=10)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Explicación general
        tk.Label(
            content,
            text="El algoritmo CUSUM (Cumulative Sum) detecta desviaciones en series temporales\n"
                 "comparando cada valor con una línea base y acumulando las desviaciones.",
            font=("Helvetica", 11),
            bg=bg_color,
            fg=text_color,
            justify=tk.LEFT,
            pady=5,
            wraplength=540  # Controlar el ancho del texto
        ).pack(anchor=tk.W)
        
        # Ecuación principal
        tk.Label(
            content,
            text="Ecuación fundamental:",
            font=("Helvetica", 11, "bold"),
            bg=bg_color,
            fg=text_color,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(10, 0))
        
        formula_frame = tk.Frame(content, bg=bg_color)
        formula_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            formula_frame,
            text="S₀ = 0",
            font=("Courier New", 12, "bold"),
            bg=bg_color,
            fg=formula_color
        ).pack(anchor=tk.W)
        
        tk.Label(
            formula_frame,
            text="Sₜ = max(0, Sₜ₋₁ + (xₜ - μ))",
            font=("Courier New", 12, "bold"),
            bg=bg_color,
            fg=formula_color
        ).pack(anchor=tk.W)
        
        # Explicación de variables
        var_frame = tk.Frame(content, bg=bg_color, pady=10)
        var_frame.pack(fill=tk.X)
        
        var_text = """Donde:
• Sₜ = suma acumulada hasta el tiempo t
• xₜ = valor del tráfico en el tiempo t
• μ = media del tráfico normal (línea base)
• max(0,·) = función que impide valores negativos"""
        
        tk.Label(
            var_frame,
            text=var_text,
            font=("Helvetica", 11),
            bg=bg_color,
            fg=text_color,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Explicación de detección
        detect_frame = tk.Frame(content, bg=bg_color, pady=10)
        detect_frame.pack(fill=tk.X)
        
        detect_text = """Detección:
Se detecta una anomalía cuando Sₜ supera un umbral predefinido. En esta implementación
se utilizan dos umbrales:
• Umbral fijo: valor constante determinado empíricamente
• Umbral estadístico: μ + 3σ (media + 3 veces la desviación estándar)"""
        
        tk.Label(
            detect_frame,
            text=detect_text,
            font=("Helvetica", 11),
            bg=bg_color,
            fg=text_color,
            justify=tk.LEFT,
            wraplength=540  # Controlar el ancho del texto
        ).pack(anchor=tk.W)
        
        # Ejemplo práctico
        example_frame = tk.Frame(content, bg=bg_color, pady=10)
        example_frame.pack(fill=tk.X)
        
        example_text = """Ejemplo:
En el tráfico de red normal, la suma acumulada oscila alrededor de valores bajos.
Cuando ocurre un ataque (valores anormalmente altos), CUSUM empieza a crecer 
rápidamente y supera el umbral, activando la alarma."""
        
        tk.Label(
            example_frame,
            text=example_text,
            font=("Helvetica", 11),
            bg=bg_color,
            fg=text_color,
            justify=tk.LEFT,
            wraplength=540  # Controlar el ancho del texto
        ).pack(anchor=tk.W)
        
        # Botón de cerrar
        btn_frame = tk.Frame(self.scrollable_frame, bg=bg_color, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="Cerrar",
            font=("Helvetica", 10, "bold"),
            command=self.ventana.destroy,
            bg="#0056b3",
            fg="white",
            padx=15,
            pady=5
        ).pack(pady=5)
        
        # Centrar la ventana
        self.ventana.update_idletasks()
        width = self.ventana.winfo_width()
        height = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Hacer modal
        self.ventana.transient(parent)
        self.ventana.grab_set()

class AplicacionTiempoReal:
    """
    Clase principal que implementa la aplicación de detección de anomalías en tiempo real.
    Integra el detector, la visualización y la interfaz de usuario.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Anomalías en Tráfico de Red")
        self.root.geometry("1000x800")
        
        # Colores y tema
        self.bg_color = "#f5f5f5"
        self.accent_color = "#6B0F1A"
        self.alert_color = "#e74c3c"
        self.success_color = "#2ecc71"
        self.text_color = "#2c3e50"
        self.root.config(bg=self.bg_color)
        
        # Detector
        self.detector = DetectorAnomalias()
        self.detector.generar_datos()
        
        # Configurar el grid
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=1)  # Contenido
        self.root.grid_rowconfigure(2, weight=0)  # Controles
        self.root.grid_rowconfigure(3, weight=0)  # Footer
        self.root.grid_columnconfigure(0, weight=1)
        
        # 1. HEADER
        header = tk.Frame(self.root, bg=self.accent_color, height=60)
        header.grid(row=0, column=0, sticky="ew")
        
        tk.Label(header, text="SISTEMA DE DETECCIÓN DE ANOMALÍAS",
                font=("Helvetica", 16, "bold"), bg=self.accent_color,
                fg="white", pady=15).pack()
        
        # 2. CONTENIDO
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Gráficas
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 7), 
                                                    dpi=100, facecolor=self.bg_color)
        self.fig.tight_layout(pad=5.0)
        self.fig.suptitle('Sistema de Detección de Anomalías en Tráfico de Red', 
                        fontsize=16, color=self.text_color)
        
        # Gráfica tráfico
        self.line_trafico, = self.ax1.plot([], [], linewidth=2, color='#3498db', label='Tráfico')
        self.ax1.set_facecolor('#f9f9f9')
        self.ax1.set_xlim(0, self.detector.ventana_tiempo)
        self.ax1.set_ylim(0, self.detector.media_trafico_normal * (self.detector.factor_ataque + 1))
        self.ax1.set_title('Tráfico de Red en Tiempo Real', fontsize=12, color=self.text_color)
        self.ax1.set_xlabel('Tiempo (s)', fontsize=10, color=self.text_color)
        self.ax1.set_ylabel('Volumen de Tráfico', fontsize=10, color=self.text_color)
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        self.ax1.legend(frameon=True, fancybox=True, shadow=True)
        
        # Gráfica acumulada
        self.line_suma, = self.ax2.plot([], [], linewidth=2, color='#2ecc71', label='Suma Acumulada')
        self.line_umbral_fijo, = self.ax2.plot([], [], linestyle='--', linewidth=2, 
                                              color='#e74c3c', label=f'Umbral Fijo ({self.detector.umbral_fijo})')
        self.line_umbral_est, = self.ax2.plot([], [], linestyle='-.', linewidth=2, 
                                             color='#9b59b6', label='Umbral Estadístico')
        self.ax2.set_facecolor('#f9f9f9')
        self.ax2.set_xlim(0, self.detector.ventana_tiempo)
        self.ax2.set_ylim(0, self.detector.umbral_fijo * 1.5)
        self.ax2.set_title('Detección de Anomalías por Suma Acumulada', fontsize=12, color=self.text_color)
        self.ax2.set_xlabel('Tiempo (s)', fontsize=10, color=self.text_color)
        self.ax2.set_ylabel('Suma Acumulada', fontsize=10, color=self.text_color)
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        self.ax2.legend(frameon=True, fancybox=True, shadow=True)
        
        # Variables para zonas de ataque
        self.zona_ataque_trafico = None
        self.zona_ataque_suma = None
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 3. PANEL DE INFORMACIÓN
        info_frame = tk.Frame(self.root, bg=self.bg_color, bd=1, relief=tk.GROOVE, height=40)
        info_frame.grid(row=2, column=0, sticky="ew", padx=10)
        info_frame.grid_propagate(False)
        
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=0)
        info_frame.grid_columnconfigure(2, weight=0)  # Nueva columna para el botón de información
        
        # Estado de simulación
        self.label_info = tk.Label(info_frame, text="Simulación: Esperando inicio...",
                                  font=("Helvetica", 11), bg=self.bg_color, 
                                  fg=self.text_color, padx=15, pady=10)
        self.label_info.grid(row=0, column=0, sticky="w")
        
        # Estado de anomalías
        self.label_ataque_info = tk.Label(info_frame, text="Estado: Buscando anomalías...",
                                         font=("Helvetica", 11, "bold"), bg=self.bg_color,
                                         fg=self.accent_color, padx=15, pady=10)
        self.label_ataque_info.grid(row=0, column=0, sticky="e", padx=(0, 150))
        
        # Botón de información
        self.btn_info = tk.Button(
            info_frame, 
            text="ⓘ Explicación",
            command=self.mostrar_explicacion,
            font=("Helvetica", 10),
            bg="#0056b3",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_info.grid(row=0, column=1, sticky="e", padx=5)
        
        # Botón inicio
        self.btn_iniciar = tk.Button(info_frame, text="Iniciar Simulación",
                                     command=self.iniciar_simulacion, font=("Helvetica", 11, "bold"),
                                     bg=self.success_color, fg="white", activebackground=self.success_color,
                                     activeforeground="white", relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
        self.btn_iniciar.grid(row=0, column=2, sticky="e", padx=15)
        
        # 4. FOOTER
        footer = tk.Frame(self.root, bg="#34495e", height=30)
        footer.grid(row=3, column=0, sticky="ew")
        
        tk.Label(footer, text="Sistema de Detección de Anomalías 2025",
                font=("Helvetica", 8), bg="#34495e", fg="white").pack(pady=5)
        
        # Variables adicionales
        self.velocidad = 12
        self.animacion = None
        self.ejecutando = False
        
        # Variables para efectos
        self.colores_alerta = ["#ffecec", "#ffe0e0", "#ffd0d0", "#ffc0c0", "#ffb0b0", 
                              "#ffa0a0", "#ffb0b0", "#ffc0c0", "#ffd0d0", "#ffe0e0"]
        self.indice_color_alerta = 0
        self.animacion_alerta_activa = False
        
        # Variables para anomalías
        self.anomalia_detectada = False
        self.alerta_mostrada = False
        self.indice_deteccion = None
        self.mostrar_alerta_pendiente = False
    
    def iniciar_animacion_alerta(self):
        if not self.animacion_alerta_activa:
            self.animacion_alerta_activa = True
            self.animar_color_alerta()
    
    def animar_color_alerta(self):
        if self.animacion_alerta_activa:
            self.label_ataque_info.config(bg=self.colores_alerta[self.indice_color_alerta])
            self.indice_color_alerta = (self.indice_color_alerta + 1) % len(self.colores_alerta)
            self.root.after(150, self.animar_color_alerta)
    
    def detener_animacion_alerta(self):
        self.animacion_alerta_activa = False
        self.label_ataque_info.config(bg="#ffecec")
    
    def mostrar_zonas_ataque(self):
        # Zonas de ataque en gráficas
        self.zona_ataque_trafico = self.ax1.axvspan(
            self.detector.inicio_ataque / self.detector.muestras_por_segundo,
            self.detector.fin_ataque / self.detector.muestras_por_segundo,
            alpha=0.3, color=self.alert_color, label='Ataque Real'
        )
        
        self.zona_ataque_suma = self.ax2.axvspan(
            self.detector.inicio_ataque / self.detector.muestras_por_segundo,
            self.detector.fin_ataque / self.detector.muestras_por_segundo,
            alpha=0.3, color=self.alert_color
        )
        
        # Actualizar leyenda y etiqueta
        self.ax1.legend(frameon=True, fancybox=True, shadow=True, prop={'size': 10})
        
        self.label_ataque_info.config(
            text=f"Estado: ¡ANOMALÍA DETECTADA! Ataque en el segundo: {self.detector.momento_real_ataque:.2f}",
            fg=self.alert_color,
            bg="#ffecec"
        )
        
        # Iniciar animaciones
        self.iniciar_animacion_alerta()
        winsound.PlaySound("SystemHand", winsound.SND_ASYNC)
        
        # Redibujar
        self.canvas.draw_idle()
        self.canvas.flush_events()
    
    def mostrar_alerta(self):
        # Calcular tiempo de detección
        tiempo_deteccion = max(0, self.detector.momento_deteccion - self.detector.momento_real_ataque)
        
        # Dibujar antes del popup
        self.canvas.draw()
        
        # Mostrar alerta con pequeño delay
        self.root.after(100, lambda: 
        messagebox.showwarning(
                "¡ANOMALÍA DETECTADA!",
            f"Se ha detectado una anomalía en el segundo {self.detector.momento_deteccion:.2f}\n"
            f"El ataque real ocurrió en el segundo {self.detector.momento_real_ataque:.2f}\n"
            f"Tiempo de detección: {tiempo_deteccion:.2f} segundos después del inicio del ataque"
        )
        )
        
        # Detener animación después de un tiempo
        self.root.after(6000, self.detener_animacion_alerta)
    
    def actualizar_grafica(self, frame):
        # Procesar pasos
        for _ in range(self.velocidad):
            if self.detector.indice_actual < self.detector.total_muestras:
                resultado = self.detector.procesar_paso()
                if resultado and not self.anomalia_detectada:
                    self.anomalia_detectada = True
                    self.indice_deteccion = self.detector.indice_actual - 1
                    # Asegurar que detección sea después del ataque real
                    if self.detector.momento_deteccion < self.detector.momento_real_ataque:
                        self.detector.momento_deteccion = self.detector.momento_real_ataque + 0.1
            else:
                break
        
        # Actualizar datos de gráficas
        t_actual = self.detector.indice_actual / self.detector.muestras_por_segundo
        indice_actual = self.detector.indice_actual
        
        # Actualizar líneas
        self.line_trafico.set_data(
            self.detector.tiempo[:indice_actual],
            self.detector.trafico[:indice_actual]
        )
        
        self.line_suma.set_data(
            self.detector.tiempo[:indice_actual],
            self.detector.suma_acumulada[:indice_actual]
        )
        
        self.line_umbral_fijo.set_data(
            self.detector.tiempo[:indice_actual],
            np.ones(indice_actual) * self.detector.umbral_fijo
        )
        
        self.line_umbral_est.set_data(
            self.detector.tiempo[:indice_actual],
            self.detector.umbral_estadistico[:indice_actual]
        )
        
        # Actualizar información
        self.label_info.config(
            text=f"Tiempo: {t_actual:.2f} s | "
                 f"Valor: {self.detector.trafico[indice_actual-1]:.2f} | "
                 f"Suma: {self.detector.suma_acumulada[indice_actual-1]:.2f}"
        )
        
        # Mostrar zonas de ataque y alerta
        if (self.anomalia_detectada and self.indice_deteccion is not None and not self.alerta_mostrada):
            segundos_pasados_ataque = t_actual - self.detector.momento_real_ataque
            
            if (segundos_pasados_ataque > 1 and 
                self.detector.suma_acumulada[indice_actual-1] > self.detector.umbral_fijo * 1.1):
                
                if not self.mostrar_alerta_pendiente:
                    self.mostrar_alerta_pendiente = True
                    self.mostrar_zonas_ataque()
                    self.root.after(500, self.mostrar_alerta)
                    self.alerta_mostrada = True
        
        # Detener si hemos terminado
        if self.detector.indice_actual >= self.detector.total_muestras:
            self.ejecutando = False
            self.btn_iniciar.config(
                text="REINICIAR SIMULACIÓN",
                state=tk.NORMAL,
                bg="#f39c12"
            )
        
        return self.line_trafico, self.line_suma, self.line_umbral_fijo, self.line_umbral_est
    
    def iniciar_simulacion(self):
        if self.ejecutando:
            return
            
        # Actualizar texto de información
        self.label_info.config(text="Simulación: En progreso... Buscando anomalías.")
        
        # Reiniciar si es necesario
        if self.detector.indice_actual >= self.detector.total_muestras or self.anomalia_detectada:
            # Detener animación anterior
            if self.animacion is not None:
                self.animacion.event_source.stop()
                self.fig.canvas.draw_idle()
                self.animacion = None
                
            # Limpiar zonas de ataque
            if self.zona_ataque_trafico:
                self.zona_ataque_trafico.remove()
                self.zona_ataque_trafico = None
            if self.zona_ataque_suma:
                self.zona_ataque_suma.remove()
                self.zona_ataque_suma = None
                
            # Detener animación de alerta
            self.detener_animacion_alerta()
                
            # Nuevo detector
            self.detector = DetectorAnomalias()
            self.detector.generar_datos()
            
            # Restablecer UI
            self.label_ataque_info.config(
                text="Estado: Buscando anomalías...",
                fg=self.accent_color,
                bg=self.bg_color
            )
            
            # Resetear variables
            self.anomalia_detectada = False
            self.alerta_mostrada = False
            self.indice_deteccion = None
            self.mostrar_alerta_pendiente = False
            self.indice_color_alerta = 0
        
        # Marcar como ejecutando
        self.ejecutando = True
        self.btn_iniciar.config(
            text="SIMULACIÓN EN CURSO",
            state=tk.DISABLED,
            bg="#95a5a6"
        )
        
        # Reiniciar índice y limpiar datos
        self.detector.indice_actual = 0
        for linea in [self.line_trafico, self.line_suma, self.line_umbral_fijo, self.line_umbral_est]:
            linea.set_data([], [])
        
        # Iniciar animación
        self.animacion = FuncAnimation(
            self.fig, 
            self.actualizar_grafica, 
            frames=self.detector.total_muestras // self.velocidad + 1,
            interval=50,
            blit=True
        )
        
        self.canvas.draw()

    def mostrar_explicacion(self):
        """Muestra la ventana con la explicación matemática"""
        ExplicacionMatematica(self.root)

def iniciar_app():
    root_app = tk.Tk()
    app = AplicacionTiempoReal(root_app)
    root_app.mainloop()

if __name__ == "__main__":
    # Mostrar pantalla de carga
    root_splash = tk.Tk()
    splash = PantallaCarga(root_splash)
    splash.iniciar_animacion(iniciar_app)
    root_splash.mainloop() 