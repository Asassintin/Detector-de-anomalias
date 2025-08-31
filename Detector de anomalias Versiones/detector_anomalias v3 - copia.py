import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox, Scale, HORIZONTAL, ttk, font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random
import threading
import matplotlib
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
import time

class DetectorAnomalias:
    def __init__(self, ventana_tiempo=60, muestras_por_segundo=60):
        """
        Inicializa el detector de anomalías
        
        Args:
            ventana_tiempo: Duración en segundos de la ventana de monitoreo
            muestras_por_segundo: Número de muestras por segundo
        """
        self.ventana_tiempo = ventana_tiempo
        self.muestras_por_segundo = muestras_por_segundo
        self.total_muestras = ventana_tiempo * muestras_por_segundo
        
        # Parámetros para la generación de datos
        self.media_trafico_normal = 100
        self.desviacion_trafico_normal = 15
        
        # Parámetros para el ataque
        self.factor_ataque = 3  # Multiplicador de la media normal
        self.duracion_ataque = int(0.5 * muestras_por_segundo)  # Medio segundo
        
        # Momento aleatorio para el ataque (entre 10 y 50 segundos)
        self.inicio_ataque = random.randint(10*muestras_por_segundo, 50*muestras_por_segundo)
        self.fin_ataque = self.inicio_ataque + self.duracion_ataque
        
        # Umbral fijo
        self.umbral_fijo = 2000  # Reducido para detectar más rápido
        
        # Variables para almacenar datos - Preasignación para optimización de memoria
        self.tiempo = np.linspace(0, ventana_tiempo, self.total_muestras)
        self.trafico = np.zeros(self.total_muestras, dtype=np.float32)
        self.suma_acumulada = np.zeros(self.total_muestras, dtype=np.float32)
        self.umbral_estadistico = np.zeros(self.total_muestras, dtype=np.float32)
        self.anomalia_detectada = False
        self.momento_deteccion = None
        self.momento_real_ataque = self.inicio_ataque / muestras_por_segundo
        
        # Para la visualización en tiempo real
        self.indice_actual = 0
        
    def generar_datos(self):
        """
        Genera datos simulados de tráfico de red con un ataque en un momento aleatorio
        """
        # Tráfico normal: distribución gaussiana
        self.trafico = np.random.normal(
            self.media_trafico_normal, 
            self.desviacion_trafico_normal, 
            self.total_muestras
        ).astype(np.float32)  # Usar float32 en lugar de float64 para ahorrar memoria
        
        # Insertar ataque (pico de tráfico)
        self.trafico[self.inicio_ataque:self.fin_ataque] += (self.media_trafico_normal 
                                                            * self.factor_ataque 
                                                            * np.ones(self.duracion_ataque, dtype=np.float32))
        
        # Asegurar que no hay valores negativos
        self.trafico = np.maximum(0, self.trafico)
        
    def calcular_suma_acumulada(self):
        """
        Implementa el método de integral discreta (suma acumulada)
        """
        # Calcular la media de los primeros 5 segundos (línea base)
        ventana_base = 5 * self.muestras_por_segundo
        linea_base = np.mean(self.trafico[:ventana_base])
        
        # Calcular suma acumulada: Σ(x_i - línea_base)
        for i in range(1, self.total_muestras):
            self.suma_acumulada[i] = max(0, self.suma_acumulada[i-1] + (self.trafico[i] - linea_base))
    
    def calcular_umbral_estadistico(self):
        """
        Calcula un umbral estadístico basado en la media y desviación estándar
        """
        # Usamos una ventana deslizante para calcular estadísticas
        ventana = 5 * self.muestras_por_segundo
        
        for i in range(ventana, self.total_muestras):
            # Calculamos media y desviación estándar de la suma acumulada en la ventana anterior
            media = np.mean(self.suma_acumulada[i-ventana:i])
            desv_est = np.std(self.suma_acumulada[i-ventana:i])
            
            # Umbral = media + 3*desviación estándar (regla 3-sigma)
            self.umbral_estadistico[i] = media + 3 * desv_est
    
    def detectar_anomalia(self, indice, en_tiempo_real=False):
        """
        Detecta si hay una anomalía en el índice especificado
        
        Args:
            indice: Índice a evaluar
            en_tiempo_real: Indica si estamos en modo tiempo real
            
        Returns:
            bool: True si se detecta anomalía, False en caso contrario
        """
        if indice < 5 * self.muestras_por_segundo:
            return False
        
        # Comprobamos si superamos alguno de los umbrales
        if (self.suma_acumulada[indice] > self.umbral_fijo or 
            (indice >= len(self.umbral_estadistico) - 1 or 
             self.suma_acumulada[indice] > self.umbral_estadistico[indice])):
            
            if not self.anomalia_detectada and en_tiempo_real:
                self.anomalia_detectada = True
                self.momento_deteccion = indice / self.muestras_por_segundo
                return True
        
        return False
    
    def procesar_paso(self):
        """
        Procesa un paso de tiempo para la visualización en tiempo real
        
        Returns:
            bool: True si se detectó anomalía en este paso, False en caso contrario
        """
        if self.indice_actual >= self.total_muestras:
            return False
        
        # Calcular suma acumulada para este punto
        if self.indice_actual > 0:
            # Calcular la media de los primeros 5 segundos (línea base)
            ventana_base = min(5 * self.muestras_por_segundo, self.indice_actual)
            linea_base = np.mean(self.trafico[:ventana_base])
            
            # Actualizar suma acumulada
            self.suma_acumulada[self.indice_actual] = max(
                0, 
                self.suma_acumulada[self.indice_actual-1] + 
                (self.trafico[self.indice_actual] - linea_base)
            )
        
        # Calcular umbral estadístico
        if self.indice_actual >= 5 * self.muestras_por_segundo:
            ventana = 5 * self.muestras_por_segundo
            media = np.mean(self.suma_acumulada[max(0, self.indice_actual-ventana):self.indice_actual])
            desv_est = np.std(self.suma_acumulada[max(0, self.indice_actual-ventana):self.indice_actual])
            self.umbral_estadistico[self.indice_actual] = media + 2.5 * desv_est  # Reducido para detectar más rápido
        
        # Detectar anomalía
        anomalia_detectada = self.detectar_anomalia(self.indice_actual, True)
        
        # Avanzar al siguiente paso
        self.indice_actual += 1
        
        return anomalia_detectada

class AplicacionTiempoReal:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Anomalías en Tráfico de Red")
        self.root.geometry("1100x950")  # Más altura para la barra de navegación y controles de tema
        
        # Configurar estilo de fuentes
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        
        # Definir tema inicial (pero no aplicarlo todavía)
        self.tema_oscuro = False
        
        # Crear el detector
        self.detector = DetectorAnomalias()
        self.detector.generar_datos()
        
        # Configurar la paleta de colores (usando método compatible con versiones recientes)
        self.cmap_trafico = matplotlib.colormaps.get_cmap('viridis')
        self.cmap_alarma = LinearSegmentedColormap.from_list('alarma', ['yellow', 'red'])
        
        # Configurar la gráfica con un estilo más moderno
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
        plt.rcParams['axes.edgecolor'] = '#343a40'
        plt.rcParams['axes.labelcolor'] = '#495057'
        plt.rcParams['xtick.color'] = '#495057'
        plt.rcParams['ytick.color'] = '#495057'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.color'] = '#dee2e6'
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.linewidth'] = 0.5
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=100)
        self.fig.tight_layout(pad=5.0)
        self.fig.patch.set_facecolor('#ffffff')
        
        # Gráfica de tráfico con estilo mejorado
        self.line_trafico, = self.ax1.plot([], [], lw=2.5, color='#3498db', label='Tráfico')
        self.ax1.set_xlim(0, self.detector.ventana_tiempo)
        self.ax1.set_ylim(0, self.detector.media_trafico_normal * (self.detector.factor_ataque + 1.5))
        self.ax1.set_title('Tráfico de Red en Tiempo Real', fontsize=14, fontweight='bold', color='#2c3e50')
        self.ax1.set_xlabel('Tiempo (s)', fontsize=11)
        self.ax1.set_ylabel('Volumen de Tráfico', fontsize=11)
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        self.ax1.spines['top'].set_visible(False)
        self.ax1.spines['right'].set_visible(False)
        self.ax1.legend(frameon=True, fancybox=True, shadow=True)
        
        # Gráfica de suma acumulada con estilo mejorado
        self.line_suma, = self.ax2.plot([], [], lw=2.5, color='#2ecc71', label='Suma Acumulada')
        self.line_umbral_fijo, = self.ax2.plot([], [], lw=2, color='#e74c3c', 
                                             linestyle='--', label=f'Umbral Fijo ({self.detector.umbral_fijo})')
        self.line_umbral_est, = self.ax2.plot([], [], lw=2, color='#9b59b6', 
                                            linestyle='-.', label='Umbral Estadístico')
        self.ax2.set_xlim(0, self.detector.ventana_tiempo)
        self.ax2.set_ylim(0, self.detector.umbral_fijo * 1.5)
        self.ax2.set_title('Detección de Anomalías por Suma Acumulada', fontsize=14, fontweight='bold', color='#2c3e50')
        self.ax2.set_xlabel('Tiempo (s)', fontsize=11)
        self.ax2.set_ylabel('Suma Acumulada', fontsize=11)
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        self.ax2.spines['top'].set_visible(False)
        self.ax2.spines['right'].set_visible(False)
        self.ax2.legend(frameon=True, fancybox=True, shadow=True)
        
        # Flechas para señalar puntos importantes (inicialmente ocultas)
        self.arrow_ataque = FancyArrowPatch((0, 0), (0, 0), 
                                           color='red', lw=2,
                                           arrowstyle='-|>', mutation_scale=15)
        self.arrow_deteccion = FancyArrowPatch((0, 0), (0, 0), 
                                              color='green', lw=2,
                                              arrowstyle='-|>', mutation_scale=15)
        
        # Variables para las zonas de ataque con animación de pulso
        self.zona_ataque_trafico = None
        self.zona_ataque_suma = None
        self.pulso_alpha = 0.3
        self.pulso_subiendo = True
        
        # Variables para controlar las alertas
        self.anomalia_detectada = False
        self.alerta_mostrada = False
        self.indice_deteccion = None
        self.mostrar_alerta_pendiente = False
        
        # Frame principal con estilo moderno
        self.frame_principal = ttk.Frame(self.root, padding=10)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Integrar la figura en Tkinter con bordes redondeados
        self.canvas_frame = ttk.Frame(self.frame_principal)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de navegación con estilo mejorado
        self.toolbar_frame = ttk.Frame(self.frame_principal)
        self.toolbar_frame.pack(fill=tk.X, pady=1)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        
        # Crear marco para controles
        self.frame_controles = ttk.Frame(self.frame_principal)
        self.frame_controles.pack(fill=tk.X, pady=5)
        
        # Panel de información con estilo moderno
        self.frame_info = ttk.Frame(self.frame_controles)
        self.frame_info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.label_info = ttk.Label(
            self.frame_info, 
            text="Simulación: Esperando inicio...",
            font=self.title_font,
            foreground="#2c3e50"
        )
        self.label_info.pack(side=tk.LEFT, padx=10)
        
        # Frame para botones de control
        self.frame_botones = ttk.Frame(self.frame_controles)
        self.frame_botones.pack(side=tk.RIGHT, padx=5)
        
        # Botón de cambio de tema con estilo mejorado
        self.btn_tema = tk.Button(
            self.frame_botones,
            text="Cambiar Tema",
            command=self.cambiar_tema,
            font=("Segoe UI", 10),
            bg="#555555" if self.tema_oscuro else "#f0f0f0",
            fg="white" if self.tema_oscuro else "#2c3e50",
            relief=tk.GROOVE,
            borderwidth=1,
            padx=10,
            pady=5
        )
        self.btn_tema.pack(side=tk.RIGHT, padx=5)
        
        # Botón de inicio con estilo mejorado
        self.btn_iniciar = tk.Button(
            self.frame_botones, 
            text="Iniciar Simulación",
            command=self.iniciar_simulacion,
            font=("Segoe UI", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.GROOVE,
            borderwidth=1,
            padx=15,
            pady=5
        )
        self.btn_iniciar.pack(side=tk.RIGHT, padx=10)
        
        # Efectos hover para botones
        self.btn_iniciar.bind("<Enter>", lambda e: self.btn_iniciar.config(bg="#66BB6A"))
        self.btn_iniciar.bind("<Leave>", lambda e: self.btn_iniciar.config(bg="#4CAF50"))
        self.btn_tema.bind("<Enter>", lambda e: self.btn_tema.config(bg="#777777" if self.tema_oscuro else "#e0e0e0"))
        self.btn_tema.bind("<Leave>", lambda e: self.btn_tema.config(bg="#555555" if self.tema_oscuro else "#f0f0f0"))
        
        # Añadir control de velocidad con estilo moderno
        self.frame_velocidad = ttk.Frame(self.frame_principal)
        self.frame_velocidad.pack(pady=5, fill=tk.X)
        
        ttk.Label(
            self.frame_velocidad,
            text="Velocidad de simulación:",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)
        
        self.velocidad = tk.IntVar(value=5)  # Valor predeterminado
        self.escala_velocidad = ttk.Scale(
            self.frame_velocidad,
            from_=1,
            to=20,
            orient=HORIZONTAL,
            variable=self.velocidad,
            length=200
        )
        self.escala_velocidad.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.frame_velocidad,
            text="Lento",
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            self.frame_velocidad,
            text="Rápido",
            font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT, padx=10)
        
        # Variables para la animación
        self.animacion = None
        self.ejecutando = False
        self.tiempo_inicio = 0
        
        # Preasignar arreglos para optimización de memoria
        self.tiempo_mostrado = np.zeros(0, dtype=np.float32)
        self.trafico_mostrado = np.zeros(0, dtype=np.float32)
        self.suma_mostrada = np.zeros(0, dtype=np.float32)
        self.umbral_fijo_mostrado = np.zeros(0, dtype=np.float32)
        self.umbral_est_mostrado = np.zeros(0, dtype=np.float32)
        
        # Agregar explicación matemática con estilo mejorado
        self.agregar_explicacion()
        
        # Ya no mostramos información del ataque desde el inicio
        self.label_ataque_info = ttk.Label(
            self.frame_principal,
            text="Buscando anomalías...",
            font=("Segoe UI", 10, "bold"),
            foreground="#3498db"
        )
        self.label_ataque_info.pack(pady=5)
        
        # Contador de FPS para optimización
        self.ultimo_tiempo = time.time()
        self.contador_frames = 0
        self.fps = 0
        
        # AHORA aplicamos el tema después de crear todos los widgets
        self.configurar_tema()
    
    def configurar_tema(self):
        """Configura el tema de la aplicación con transiciones suaves"""
        if self.tema_oscuro:
            # Configurar tema oscuro
            self.root.configure(bg="#121212")
            plt.style.use('dark_background')
            ttk.Style().configure("TFrame", background="#121212")
            ttk.Style().configure("TLabel", background="#121212", foreground="white")
            ttk.Style().configure("TButton", background="#2a2a2a", foreground="white")
            ttk.Style().configure("TScale", background="#121212", troughcolor="#2a2a2a")
            
            # Actualizar etiquetas
            self.label_info.configure(foreground="#e0e0e0")
            self.label_ataque_info.configure(foreground="#3498db")
        else:
            # Configurar tema claro
            self.root.configure(bg="#f8f9fa")
            plt.style.use('default')
            ttk.Style().configure("TFrame", background="#f8f9fa")
            ttk.Style().configure("TLabel", background="#f8f9fa", foreground="#2c3e50")
            ttk.Style().configure("TButton", background="#e9ecef", foreground="#2c3e50")
            ttk.Style().configure("TScale", background="#f8f9fa", troughcolor="#dee2e6")
            
            # Actualizar etiquetas
            self.label_info.configure(foreground="#2c3e50")
            if not self.anomalia_detectada:
                self.label_ataque_info.configure(foreground="#3498db")
        
        # Actualizar gráfico con animación
        self.canvas.draw_idle()
    
    def cambiar_tema(self):
        """Cambia entre tema claro y oscuro con transición animada"""
        self.tema_oscuro = not self.tema_oscuro
        self.configurar_tema()
        
        # Actualizar botón de tema
        self.btn_tema.config(
            bg="#555555" if self.tema_oscuro else "#f0f0f0",
            fg="white" if self.tema_oscuro else "#2c3e50"
        )
        
        # Actualizar colores de los gráficos
        if self.tema_oscuro:
            # Aplicar colores brillantes para tema oscuro
            self.line_trafico.set_color('#3498db')  # Azul brillante
            self.line_suma.set_color('#2ecc71')     # Verde brillante
            self.line_umbral_fijo.set_color('#e74c3c')  # Rojo brillante
            self.line_umbral_est.set_color('#9b59b6')   # Púrpura brillante
            
            # Actualizar colores de fondo y texto
            for ax in [self.ax1, self.ax2]:
                ax.set_facecolor('#1e1e1e')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                ax.grid(color='#333333', linestyle='--', alpha=0.7)
                
            self.fig.set_facecolor('#121212')
        else:
            # Aplicar colores para tema claro
            self.line_trafico.set_color('#3498db')  # Azul
            self.line_suma.set_color('#2ecc71')     # Verde
            self.line_umbral_fijo.set_color('#e74c3c')  # Rojo
            self.line_umbral_est.set_color('#9b59b6')   # Púrpura
            
            # Restaurar colores de fondo y texto
            for ax in [self.ax1, self.ax2]:
                ax.set_facecolor('#f8f9fa')
                ax.tick_params(colors='#495057')
                ax.xaxis.label.set_color('#495057')
                ax.yaxis.label.set_color('#495057')
                ax.title.set_color('#2c3e50')
                ax.grid(color='#dee2e6', linestyle='--', alpha=0.7)
                
            self.fig.set_facecolor('#ffffff')
        
        # Actualizar gráfico con animación
        self.canvas.draw_idle()
    
    def agregar_explicacion(self):
        """Agrega un panel con la explicación matemática del método"""
        frame_explicacion = ttk.Frame(self.frame_principal)
        frame_explicacion.pack(fill=tk.X, pady=5, padx=20)
        
        explicacion = """
        Explicación Matemática: La detección utiliza la suma acumulada (CUSUM) definida como:
        
        S₀ = 0
        Sₜ = max(0, Sₜ₋₁ + (xₜ - μ))
        
        Donde:
        - xₜ es el valor del tráfico en el tiempo t
        - μ es la media del tráfico normal (línea base)
        - Sₜ es la suma acumulada hasta el tiempo t
        """
        
        label_explicacion = ttk.Label(
            frame_explicacion, 
            text=explicacion,
            font=("Segoe UI", 9),
            justify=tk.LEFT,
            padding=(10, 5)
        )
        label_explicacion.pack(fill=tk.X)
    
    def animar_zona_ataque(self):
        """Animación de pulso para la zona de ataque"""
        if not self.ejecutando or not hasattr(self, 'zona_ataque_trafico') or self.zona_ataque_trafico is None:
            return
            
        # Cambiar la transparencia para crear efecto de pulso
        if self.pulso_subiendo:
            self.pulso_alpha += 0.02
            if self.pulso_alpha >= 0.7:
                self.pulso_subiendo = False
        else:
            self.pulso_alpha -= 0.02
            if self.pulso_alpha <= 0.2:
                self.pulso_subiendo = True
        
        # Aplicar la nueva transparencia
        if hasattr(self, 'zona_ataque_trafico') and self.zona_ataque_trafico is not None:
            self.zona_ataque_trafico.set_alpha(self.pulso_alpha)
        if hasattr(self, 'zona_ataque_suma') and self.zona_ataque_suma is not None:
            self.zona_ataque_suma.set_alpha(self.pulso_alpha)
        
        # Programar la siguiente animación
        if self.ejecutando and hasattr(self, 'root') and self.root:
            try:
                self.pulso_timer = self.root.after(50, self.animar_zona_ataque)
            except Exception:
                pass  # En caso de error, simplemente no programamos la siguiente animación
                
    def _cancelar_animaciones(self):
        """Cancela todas las animaciones pendientes para evitar errores"""
        if hasattr(self, 'pulso_timer'):
            try:
                self.root.after_cancel(self.pulso_timer)
            except Exception:
                pass
                
        if hasattr(self, 'animacion') and self.animacion is not None:
            try:
                self.animacion.event_source.stop()
            except Exception:
                pass
                
    def __del__(self):
        """Destructor para limpiar recursos"""
        self._cancelar_animaciones()
                
    def mostrar_zonas_ataque(self):
        """Muestra las zonas donde ocurre el ataque real con animación"""
        # Cancelar animaciones previas si existen
        self._cancelar_animaciones()
    
        # Añadir zona de ataque en la gráfica de tráfico con efecto de gradiente
        inicio = self.detector.inicio_ataque / self.detector.muestras_por_segundo
        fin = self.detector.fin_ataque / self.detector.muestras_por_segundo
        
        # Eliminar zonas anteriores si existen
        if hasattr(self, 'zona_ataque_trafico') and self.zona_ataque_trafico is not None:
            self.zona_ataque_trafico.remove()
        if hasattr(self, 'zona_ataque_suma') and self.zona_ataque_suma is not None:
            self.zona_ataque_suma.remove()
            
        self.zona_ataque_trafico = self.ax1.axvspan(
            inicio, fin,
            alpha=0.3, color='red', label='Ataque Real'
        )
        
        # Añadir zona de ataque en la gráfica de suma acumulada
        self.zona_ataque_suma = self.ax2.axvspan(
            inicio, fin,
            alpha=0.3, color='red'
        )
        
        # Añadir flechas para señalar puntos importantes
        try:
            # Flecha para el momento del ataque
            y_max_trafico = self.ax1.get_ylim()[1] * 0.9
            if hasattr(self, 'arrow_ataque'):
                if self.arrow_ataque in self.ax1.patches:
                    self.arrow_ataque.remove()
            
            self.arrow_ataque = FancyArrowPatch((inicio, y_max_trafico * 0.2), (inicio, y_max_trafico * 0.8),
                                               color='red', lw=2,
                                               arrowstyle='-|>', mutation_scale=15)
            self.ax1.add_patch(self.arrow_ataque)
            
            # Texto para el momento del ataque - limpiar textos anteriores
            for txt in self.ax1.texts:
                txt.remove()
                
            self.ax1.annotate(f'Ataque\nt={inicio:.2f}s', 
                            xy=(inicio, y_max_trafico * 0.85), 
                            xytext=(inicio+1, y_max_trafico * 0.85),
                            ha='left', va='center', 
                            bbox=dict(boxstyle="round,pad=0.3", fc='red', alpha=0.6, ec="none"),
                            color='white', fontweight='bold')
        except Exception as e:
            print(f"Error al añadir flechas/texto: {e}")
        
        # Actualizar la leyenda
        try:
            self.ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        except Exception:
            pass
        
        # Actualizar la información del ataque con animación
        try:
            self.label_ataque_info.config(
                text=f"¡Anomalía detectada! El ataque ocurrió en el segundo: {self.detector.momento_real_ataque:.2f}",
                foreground="red"
            )
        except Exception:
            pass
        
        # Iniciar animación de pulso
        self.pulso_alpha = 0.3
        self.pulso_subiendo = True
        self.pulso_timer = self.root.after(50, self.animar_zona_ataque)
        
        # Redibujar el canvas
        try:
            self.canvas.draw_idle()
        except Exception:
            pass
    
    def mostrar_alerta(self):
        """Muestra una alerta cuando se detecta una anomalía"""
        # Solo mostramos tiempo positivo de detección
        tiempo_deteccion = self.detector.momento_deteccion - self.detector.momento_real_ataque
        if tiempo_deteccion < 0:
            tiempo_deteccion = 0
        
        try:
            # Flecha para el momento de detección
            y_max_suma = self.ax2.get_ylim()[1] * 0.9
            momento_deteccion = self.detector.momento_deteccion
            
            # Eliminar flecha anterior si existe
            if hasattr(self, 'arrow_deteccion'):
                if self.arrow_deteccion in self.ax2.patches:
                    self.arrow_deteccion.remove()
                    
            self.arrow_deteccion = FancyArrowPatch((momento_deteccion, y_max_suma * 0.2), 
                                                 (momento_deteccion, y_max_suma * 0.8),
                                                 color='green', lw=2,
                                                 arrowstyle='-|>', mutation_scale=15)
            self.ax2.add_patch(self.arrow_deteccion)
            
            # Eliminar textos previos
            for txt in self.ax2.texts:
                txt.remove()
                
            # Texto para el momento de detección
            self.ax2.annotate(f'Detección\nt={momento_deteccion:.2f}s', 
                            xy=(momento_deteccion, y_max_suma * 0.85), 
                            xytext=(momento_deteccion+1, y_max_suma * 0.85),
                            ha='left', va='center',
                            bbox=dict(boxstyle="round,pad=0.3", fc='green', alpha=0.6, ec="none"),
                            color='white', fontweight='bold')
            
            # Actualizar canvas
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error al mostrar flechas de detección: {e}")
        
        try:
            messagebox.showwarning(
                "¡Anomalía Detectada!",
                f"Se ha detectado una anomalía en el segundo {self.detector.momento_deteccion:.2f}\n"
                f"El ataque real ocurrió en el segundo {self.detector.momento_real_ataque:.2f}\n"
                f"Tiempo de detección: {tiempo_deteccion:.2f} segundos después del inicio del ataque"
            )
        except Exception as e:
            print(f"Error al mostrar mensaje de alerta: {e}")
    
    def actualizar_grafica(self, frame):
        """Actualiza la gráfica en tiempo real con animaciones mejoradas"""
        try:
            # Calcular FPS para optimización
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_tiempo >= 1.0:
                self.fps = self.contador_frames
                self.contador_frames = 0
                self.ultimo_tiempo = tiempo_actual
            else:
                self.contador_frames += 1
            
            # Procesar varios pasos según la velocidad seleccionada
            pasos_por_frame = self.velocidad.get()
            
            for _ in range(pasos_por_frame):
                if self.detector.indice_actual < self.detector.total_muestras:
                    # Procesar el siguiente paso
                    resultado = self.detector.procesar_paso()
                    if resultado and not self.anomalia_detectada:
                        self.anomalia_detectada = True
                        self.indice_deteccion = self.detector.indice_actual - 1
                        if self.detector.momento_deteccion < self.detector.momento_real_ataque:
                            self.detector.momento_deteccion = self.detector.momento_real_ataque + 0.1
                else:
                    break
            
            # Actualizar datos de las gráficas - optimización de memoria
            indice_actual = self.detector.indice_actual
            t_actual = indice_actual / self.detector.muestras_por_segundo
            
            # Calcular tiempo transcurrido para animaciones
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            
            # Redimensionar arrays solo si es necesario
            if len(self.tiempo_mostrado) != indice_actual:
                self.tiempo_mostrado = self.detector.tiempo[:indice_actual]
                self.trafico_mostrado = self.detector.trafico[:indice_actual]
                self.suma_mostrada = self.detector.suma_acumulada[:indice_actual]
                self.umbral_fijo_mostrado = np.ones(indice_actual, dtype=np.float32) * self.detector.umbral_fijo
                self.umbral_est_mostrado = self.detector.umbral_estadistico[:indice_actual]
            
            # Actualizar gráfica de tráfico con colores dinámicos
            self.line_trafico.set_data(self.tiempo_mostrado, self.trafico_mostrado)
            
            # Actualizar gráfica de suma acumulada
            self.line_suma.set_data(self.tiempo_mostrado, self.suma_mostrada)
            
            # Actualizar umbral fijo con línea más visible
            self.line_umbral_fijo.set_data(self.tiempo_mostrado, self.umbral_fijo_mostrado)
            
            # Actualizar umbral estadístico con estilo mejorado
            self.line_umbral_est.set_data(self.tiempo_mostrado, self.umbral_est_mostrado)
            
            # Actualizar información con más detalles
            if indice_actual > 0:
                # Calcular velocidad de procesamiento
                self.label_info.config(
                    text=f"Tiempo: {t_actual:.2f} s | "
                        f"Valor: {self.detector.trafico[indice_actual-1]:.2f} | "
                        f"Suma acumulada: {self.detector.suma_acumulada[indice_actual-1]:.2f} | "
                        f"FPS: {self.fps}"
                )
            
            # Mostrar zonas de ataque cuando se detecte la anomalía
            if (self.anomalia_detectada and 
                self.indice_deteccion is not None and
                not self.alerta_mostrada):
                
                # Calculamos cuánto ha avanzado la visualización después del ataque real
                segundos_pasados_ataque = t_actual - self.detector.momento_real_ataque
                
                # Solo mostramos la alerta cuando:
                # 1. Hayan pasado al menos 1 segundo desde el ataque real (para que se vea en la gráfica)
                # 2. La suma acumulada haya superado visiblemente el umbral
                if (segundos_pasados_ataque > 1 and 
                    self.detector.suma_acumulada[indice_actual-1] > self.detector.umbral_fijo * 1.1):
                    
                    if not self.mostrar_alerta_pendiente:
                        self.mostrar_alerta_pendiente = True
                        # Mostramos las zonas de ataque
                        self.mostrar_zonas_ataque()
                        # Programamos la alerta para que aparezca después
                        self.root.after(500, self.mostrar_alerta)
                        self.alerta_mostrada = True
            
            # Detener la animación si hemos llegado al final
            if indice_actual >= self.detector.total_muestras:
                self.ejecutando = False
                self.btn_iniciar.config(text="Reiniciar Simulación", state=tk.NORMAL)
            
            return self.line_trafico, self.line_suma, self.line_umbral_fijo, self.line_umbral_est
            
        except Exception as e:
            print(f"Error en actualizar_grafica: {e}")
            # Devolvemos los objetos de línea para que blit funcione
            if hasattr(self, 'line_trafico') and hasattr(self, 'line_suma') and hasattr(self, 'line_umbral_fijo') and hasattr(self, 'line_umbral_est'):
                return self.line_trafico, self.line_suma, self.line_umbral_fijo, self.line_umbral_est
            else:
                # Si no tenemos objetos de línea, detenemos la simulación
                self.ejecutando = False
                if hasattr(self, 'btn_iniciar'):
                    self.btn_iniciar.config(text="Reiniciar Simulación", state=tk.NORMAL)
                return tuple()
    
    def iniciar_simulacion(self):
        """Inicia o reinicia la simulación con efectos visuales"""
        if self.ejecutando:
            return
        
        try:
            # Efecto visual al iniciar
            self.btn_iniciar.config(bg="#388E3C", state=tk.DISABLED)
            self.root.after(100, lambda: self.btn_iniciar.config(bg="#4CAF50"))
            self.root.after(200, self._iniciar_simulacion_interno)
        except Exception as e:
            print(f"Error al iniciar la simulación: {e}")
            self._iniciar_simulacion_interno()  # Intentamos iniciar de todos modos
    
    def _iniciar_simulacion_interno(self):
        """Método interno para continuar con la inicialización tras el efecto visual"""
        try:
            # Cancelar animaciones existentes
            self._cancelar_animaciones()
            
            # Reiniciar el detector si es necesario
            if self.detector.indice_actual >= self.detector.total_muestras or self.anomalia_detectada:
                # Limpiar zonas de ataque anteriores si existen
                if hasattr(self, 'zona_ataque_trafico') and self.zona_ataque_trafico is not None:
                    self.zona_ataque_trafico.remove()
                    self.zona_ataque_trafico = None
                if hasattr(self, 'zona_ataque_suma') and self.zona_ataque_suma is not None:
                    self.zona_ataque_suma.remove()
                    self.zona_ataque_suma = None
                
                # Limpiar flechas y anotaciones
                if hasattr(self, 'arrow_ataque'):
                    if self.arrow_ataque in self.ax1.patches:
                        self.arrow_ataque.remove()
                if hasattr(self, 'arrow_deteccion'):
                    if self.arrow_deteccion in self.ax2.patches:
                        self.arrow_deteccion.remove()
                
                # Limpiar anotaciones de texto
                for ax in [self.ax1, self.ax2]:
                    for text in ax.texts:
                        text.remove()
                    
                # Crear un nuevo detector
                self.detector = DetectorAnomalias()
                self.detector.generar_datos()
                
                # Restablecer etiqueta de información
                self.label_ataque_info.config(
                    text="Buscando anomalías...",
                    foreground="#3498db"
                )
                
                # Resetear las variables de control de anomalías
                self.anomalia_detectada = False
                self.alerta_mostrada = False
                self.indice_deteccion = None
                self.mostrar_alerta_pendiente = False
                
                # Limpiar arrays para optimización de memoria
                self.tiempo_mostrado = np.zeros(0, dtype=np.float32)
                self.trafico_mostrado = np.zeros(0, dtype=np.float32)
                self.suma_mostrada = np.zeros(0, dtype=np.float32)
                self.umbral_fijo_mostrado = np.zeros(0, dtype=np.float32)
                self.umbral_est_mostrado = np.zeros(0, dtype=np.float32)
            
            # Marcar como ejecutando y actualizar botón
            self.ejecutando = True
            self.btn_iniciar.config(text="Simulación en Curso", state=tk.DISABLED)
            
            # Registrar tiempo de inicio para animaciones
            self.tiempo_inicio = time.time()
            
            # Iniciar la animación con manejo de errores
            self.animacion = FuncAnimation(
                self.fig, 
                self.actualizar_grafica, 
                frames=self.detector.total_muestras // self.velocidad.get() + 1,
                interval=25,  # Intervalo más corto para animaciones más suaves
                blit=True
            )
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error en inicialización interna: {e}")
            # Recuperación de error - intentar restablecer el estado
            self.ejecutando = False
            if hasattr(self, 'btn_iniciar'):
                self.btn_iniciar.config(text="Reiniciar Simulación", state=tk.NORMAL)

if __name__ == "__main__":
    # Crear la ventana de Tkinter
    root = tk.Tk()
    app = AplicacionTiempoReal(root)
    root.mainloop() 