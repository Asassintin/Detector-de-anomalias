import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox, Scale, HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Detector de Anomalías basado en Suma Acumulada (CUSUM)
# Este sistema detecta anomalías en tráfico de red utilizando el algoritmo CUSUM,
# que acumula las desviaciones de un valor sobre un nivel esperado.
class DetectorAnomalias:
    def __init__(self, ventana_tiempo=60, muestras_por_segundo=60):
        """
        Inicializa el detector de anomalías con parámetros configurables
        """
        # Parámetros de tiempo y muestreo
        self.ventana_tiempo = ventana_tiempo  # Duración total en segundos
        self.muestras_por_segundo = muestras_por_segundo
        self.total_muestras = ventana_tiempo * muestras_por_segundo
        
        # Parámetros para generación de datos normales
        self.media_trafico_normal = 100
        self.desviacion_trafico_normal = 15
        
        # Parámetros para la simulación de ataque
        self.factor_ataque = 3  # Incremento durante el ataque (x veces la media normal)
        self.duracion_ataque = int(0.5 * muestras_por_segundo)  # Medio segundo de duración
        self.inicio_ataque = random.randint(10*muestras_por_segundo, 50*muestras_por_segundo)
        self.fin_ataque = self.inicio_ataque + self.duracion_ataque
        
        # Parámetros de detección
        self.umbral_fijo = 2000  # Umbral para detección de anomalías
        
        # Arreglos de datos
        self.tiempo = np.arange(self.total_muestras) / muestras_por_segundo
        self.trafico = np.zeros(self.total_muestras)
        self.suma_acumulada = np.zeros(self.total_muestras)
        self.umbral_estadistico = np.zeros(self.total_muestras)
        
        # Variables de estado
        self.anomalia_detectada = False
        self.momento_deteccion = None
        self.momento_real_ataque = self.inicio_ataque / muestras_por_segundo
        self.indice_actual = 0
        
    def generar_datos(self):
        """
        Genera datos simulados con un patrón normal y un ataque en un punto aleatorio
        """
        # Generar tráfico normal con distribución gaussiana
        self.trafico = np.random.normal(
            self.media_trafico_normal, 
            self.desviacion_trafico_normal, 
            self.total_muestras
        )
        
        # Insertar ataque como un pico de tráfico
        self.trafico[self.inicio_ataque:self.fin_ataque] += (self.media_trafico_normal 
                                                          * self.factor_ataque 
                                                          * np.ones(self.duracion_ataque))
        
        # Asegurar que no hay valores negativos
        self.trafico = np.maximum(0, self.trafico)
    
    def detectar_anomalia(self, indice, en_tiempo_real=False):
        """
        Evalúa si existe una anomalía en el punto actual basado en los umbrales
        """
        # No detectamos en los primeros 5 segundos (período de establecimiento)
        if indice < 5 * self.muestras_por_segundo:
            return False
            
        # Comprobamos si superamos alguno de los umbrales
        if (self.suma_acumulada[indice] > self.umbral_fijo or 
            (indice >= len(self.umbral_estadistico) - 1 or 
             self.suma_acumulada[indice] > self.umbral_estadistico[indice])):
            
            # Solo registramos la primera detección en tiempo real
            if not self.anomalia_detectada and en_tiempo_real:
                self.anomalia_detectada = True
                self.momento_deteccion = indice / self.muestras_por_segundo
                return True
                
        return False
    
    def procesar_paso(self):
        """
        Procesa un paso de tiempo en la simulación, calculando la suma acumulada
        y evaluando la presencia de anomalías
        """
        # Verificar si hemos llegado al final de la simulación
        if self.indice_actual >= self.total_muestras:
            return False
        
        # Calcular la suma acumulada usando el algoritmo CUSUM
        # S_t = max(0, S_{t-1} + (x_t - μ))
        if self.indice_actual > 0:
            # Calcular la línea base (media del tráfico normal)
            ventana_base = min(5 * self.muestras_por_segundo, self.indice_actual)
            linea_base = np.mean(self.trafico[:ventana_base])
            
            # Aplicar fórmula CUSUM
            self.suma_acumulada[self.indice_actual] = max(
                0, 
                self.suma_acumulada[self.indice_actual-1] + 
                (self.trafico[self.indice_actual] - linea_base)
            )
        
        # Calcular umbral estadístico adaptativo
        if self.indice_actual >= 5 * self.muestras_por_segundo:
            ventana = 5 * self.muestras_por_segundo
            media = np.mean(self.suma_acumulada[max(0, self.indice_actual-ventana):self.indice_actual])
            desv_est = np.std(self.suma_acumulada[max(0, self.indice_actual-ventana):self.indice_actual])
            # Umbral = media + 2.5*desviación estándar (regla adaptada de 3-sigma)
            self.umbral_estadistico[self.indice_actual] = media + 2.5 * desv_est
        
        # Detectar anomalía en este punto
        anomalia_detectada = self.detectar_anomalia(self.indice_actual, True)
        
        # Avanzar al siguiente paso
        self.indice_actual += 1
        
        return anomalia_detectada

# Interfaz gráfica para visualizar la detección de anomalías en tiempo real
class AplicacionTiempoReal:
    def __init__(self, root):
        """
        Inicializa la interfaz gráfica de la aplicación
        """
        # Configuración de la ventana principal
        self.root = root
        self.root.title("Detector de Anomalías en Tráfico de Red")
        self.root.geometry("1000x850")
        
        # Inicializar el detector y generar datos
        self.detector = DetectorAnomalias()
        self.detector.generar_datos()
        
        # Configurar las gráficas
        self.configurar_graficas()
        
        # Variables para control de la visualización
        self.zona_ataque_trafico = None
        self.zona_ataque_suma = None
        self.anomalia_detectada = False
        self.alerta_mostrada = False
        self.indice_deteccion = None
        self.mostrar_alerta_pendiente = False
        
        # Crear widgets de la interfaz
        self.crear_interfaz()
        
        # Variables para la animación
        self.animacion = None
        self.ejecutando = False
    
    def configurar_graficas(self):
        """Configura las gráficas de visualización"""
        # Crear figura con dos subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=5.0)
        
        # Configurar gráfica superior (tráfico)
        self.line_trafico, = self.ax1.plot([], [], 'b-', label='Tráfico')
        self.ax1.set_xlim(0, self.detector.ventana_tiempo)
        self.ax1.set_ylim(0, self.detector.media_trafico_normal * (self.detector.factor_ataque + 1))
        self.ax1.set_title('Tráfico de Red en Tiempo Real')
        self.ax1.set_xlabel('Tiempo (s)')
        self.ax1.set_ylabel('Volumen de Tráfico')
        self.ax1.grid(True)
        self.ax1.legend()
        
        # Configurar gráfica inferior (suma acumulada)
        self.line_suma, = self.ax2.plot([], [], 'g-', label='Suma Acumulada')
        self.line_umbral_fijo, = self.ax2.plot([], [], 'r--', label=f'Umbral Fijo ({self.detector.umbral_fijo})')
        self.line_umbral_est, = self.ax2.plot([], [], 'm--', label='Umbral Estadístico')
        self.ax2.set_xlim(0, self.detector.ventana_tiempo)
        self.ax2.set_ylim(0, self.detector.umbral_fijo * 1.5)
        self.ax2.set_title('Detección de Anomalías por Suma Acumulada')
        self.ax2.set_xlabel('Tiempo (s)')
        self.ax2.set_ylabel('Suma Acumulada')
        self.ax2.grid(True)
        self.ax2.legend()
        
        # Integrar la figura en Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def crear_interfaz(self):
        """Crea los widgets de la interfaz de usuario"""
        # Panel de información
        self.frame_info = tk.Frame(self.root)
        self.frame_info.pack(pady=5, fill=tk.X)
        self.label_info = tk.Label(self.frame_info, text="Simulación: Esperando inicio...", font=("Arial", 12))
        self.label_info.pack(side=tk.LEFT, padx=10)
        
        # Control de velocidad
        self.frame_velocidad = tk.Frame(self.root)
        self.frame_velocidad.pack(pady=5, fill=tk.X)
        tk.Label(self.frame_velocidad, text="Velocidad de simulación:", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        self.velocidad = tk.IntVar(value=5)
        self.escala_velocidad = Scale(self.frame_velocidad, from_=1, to=20, orient=HORIZONTAL, 
                                     variable=self.velocidad, length=200)
        self.escala_velocidad.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.frame_velocidad, text="Lento", font=("Arial", 8)).pack(side=tk.LEFT)
        tk.Label(self.frame_velocidad, text="Rápido", font=("Arial", 8)).pack(side=tk.RIGHT, padx=10)
        
        # Botón de inicio
        self.btn_iniciar = tk.Button(self.frame_info, text="Iniciar Simulación", command=self.iniciar_simulacion,
                                    font=("Arial", 12), bg="#4CAF50", fg="white", padx=10)
        self.btn_iniciar.pack(side=tk.RIGHT, padx=10)
        
        # Explicación matemática
        self.agregar_explicacion()
        
        # Etiqueta de información de ataque
        self.label_ataque_info = tk.Label(self.root, text="Buscando anomalías...", 
                                         font=("Arial", 10, "bold"), fg="blue")
        self.label_ataque_info.pack(pady=5)
        
    def agregar_explicacion(self):
        """Agrega un panel con la explicación matemática del algoritmo CUSUM"""
        frame_explicacion = tk.Frame(self.root)
        frame_explicacion.pack(fill=tk.X, pady=5, padx=20)
        
        # Explicación matemática del algoritmo CUSUM y su aplicación
        explicacion = """
        Explicación Matemática: Este detector utiliza el algoritmo CUSUM (suma acumulada) definido como:
        
        S_0 = 0
        S_t = max(0, S_{t-1} + (x_t - μ))
        
        Donde:
        - x_t: valor del tráfico en el tiempo t
        - μ: media del tráfico normal (línea base)
        - S_t: suma acumulada hasta el tiempo t
        
        Cuando S_t supera un umbral (fijo o estadístico), se detecta una anomalía. El algoritmo es
        especialmente sensible a desviaciones sostenidas sobre la media.
        """
        
        label_explicacion = tk.Label(frame_explicacion, text=explicacion, font=("Arial", 9),
                                   justify=tk.LEFT, bg="#f0f0f0", padx=10, pady=5)
        label_explicacion.pack(fill=tk.X)
    
    def mostrar_zonas_ataque(self):
        """Resalta visualmente las zonas donde ocurrió el ataque real"""
        # Añadir zona de ataque en la gráfica de tráfico
        self.zona_ataque_trafico = self.ax1.axvspan(
            self.detector.inicio_ataque / self.detector.muestras_por_segundo,
            self.detector.fin_ataque / self.detector.muestras_por_segundo,
            alpha=0.3, color='red', label='Ataque Real'
        )
        
        # Añadir zona de ataque en la gráfica de suma acumulada
        self.zona_ataque_suma = self.ax2.axvspan(
            self.detector.inicio_ataque / self.detector.muestras_por_segundo,
            self.detector.fin_ataque / self.detector.muestras_por_segundo,
            alpha=0.3, color='red'
        )
        
        # Actualizar leyenda e información
        self.ax1.legend()
        self.label_ataque_info.config(
            text=f"¡Anomalía detectada! El ataque ocurrió en el segundo: {self.detector.momento_real_ataque:.2f}",
            fg="red"
        )
        self.canvas.draw_idle()
    
    def mostrar_alerta(self):
        """Muestra una alerta con información sobre la detección"""
        # Calcular tiempo de detección relativo al inicio del ataque
        tiempo_deteccion = self.detector.momento_deteccion - self.detector.momento_real_ataque
        if tiempo_deteccion < 0:
            tiempo_deteccion = 0
            
        # Mostrar ventana de alerta
        messagebox.showwarning(
            "¡Anomalía Detectada!",
            f"Se ha detectado una anomalía en el segundo {self.detector.momento_deteccion:.2f}\n"
            f"El ataque real ocurrió en el segundo {self.detector.momento_real_ataque:.2f}\n"
            f"Tiempo de detección: {tiempo_deteccion:.2f} segundos después del inicio del ataque"
        )
    
    def actualizar_grafica(self, frame):
        """Actualiza las gráficas en cada paso de la animación"""
        # Procesar varios pasos según la velocidad seleccionada
        pasos_por_frame = self.velocidad.get()
        
        # Procesar pasos de la simulación
        for _ in range(pasos_por_frame):
            if self.detector.indice_actual < self.detector.total_muestras:
                # Procesar siguiente paso y verificar si hay anomalía
                resultado = self.detector.procesar_paso()
                if resultado and not self.anomalia_detectada:
                    self.anomalia_detectada = True
                    self.indice_deteccion = self.detector.indice_actual - 1
                    # Asegurar que el momento de detección no sea antes del ataque real
                    if self.detector.momento_deteccion < self.detector.momento_real_ataque:
                        self.detector.momento_deteccion = self.detector.momento_real_ataque + 0.1
            else:
                break
        
        # Tiempo actual en la simulación
        t_actual = self.detector.indice_actual / self.detector.muestras_por_segundo
        
        # Actualizar datos en las gráficas
        self.actualizar_datos_graficas(t_actual)
        
        # Verificar si debemos mostrar la alerta de detección
        self.verificar_alerta(t_actual)
        
        # Verificar si hemos llegado al final de la simulación
        if self.detector.indice_actual >= self.detector.total_muestras:
            self.ejecutando = False
            self.btn_iniciar.config(text="Reiniciar Simulación", state=tk.NORMAL)
        
        # Retornar líneas actualizadas para animación con blit=True
        return self.line_trafico, self.line_suma, self.line_umbral_fijo, self.line_umbral_est
    
    def actualizar_datos_graficas(self, t_actual):
        """Actualiza los datos visualizados en las gráficas"""
        # Actualizar gráfica de tráfico
        self.line_trafico.set_data(
            self.detector.tiempo[:self.detector.indice_actual],
            self.detector.trafico[:self.detector.indice_actual]
        )
        
        # Actualizar gráfica de suma acumulada
        self.line_suma.set_data(
            self.detector.tiempo[:self.detector.indice_actual],
            self.detector.suma_acumulada[:self.detector.indice_actual]
        )
        
        # Actualizar umbral fijo
        self.line_umbral_fijo.set_data(
            self.detector.tiempo[:self.detector.indice_actual],
            np.ones(self.detector.indice_actual) * self.detector.umbral_fijo
        )
        
        # Actualizar umbral estadístico
        self.line_umbral_est.set_data(
            self.detector.tiempo[:self.detector.indice_actual],
            self.detector.umbral_estadistico[:self.detector.indice_actual]
        )
        
        # Actualizar información textual
        idx = max(0, self.detector.indice_actual-1)
        self.label_info.config(
            text=f"Tiempo: {t_actual:.2f} s | "
                 f"Valor actual: {self.detector.trafico[idx]:.2f} | "
                 f"Suma acumulada: {self.detector.suma_acumulada[idx]:.2f}"
        )
    
    def verificar_alerta(self, t_actual):
        """Verifica si debe mostrarse la alerta de detección"""
        if (self.anomalia_detectada and self.indice_deteccion is not None and not self.alerta_mostrada):
            # Calculamos cuánto ha avanzado la visualización después del ataque real
            segundos_pasados_ataque = t_actual - self.detector.momento_real_ataque
            
            # Mostrar alerta cuando hay evidencia clara de la anomalía
            if (segundos_pasados_ataque > 1 and 
                self.detector.suma_acumulada[self.detector.indice_actual-1] > self.detector.umbral_fijo * 1.1):
                
                if not self.mostrar_alerta_pendiente:
                    self.mostrar_alerta_pendiente = True
                    self.mostrar_zonas_ataque()
                    # Mostrar la alerta después de un pequeño retraso
                    self.root.after(500, self.mostrar_alerta)
                    self.alerta_mostrada = True
    
    def iniciar_simulacion(self):
        """Inicia o reinicia la simulación"""
        if self.ejecutando:
            return
        
        # Reiniciar si es necesario
        if self.detector.indice_actual >= self.detector.total_muestras or self.anomalia_detectada:
            self.reiniciar_simulacion()
        
        # Iniciar simulación
        self.ejecutando = True
        self.btn_iniciar.config(text="Simulación en Curso", state=tk.DISABLED)
        
        # Configurar la animación
        self.animacion = FuncAnimation(
            self.fig, 
            self.actualizar_grafica, 
            frames=self.detector.total_muestras // self.velocidad.get() + 1,
            interval=50,  # 50ms entre frames
            blit=True     # Optimización para mejorar rendimiento
        )
        
        self.canvas.draw()
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación a su estado inicial"""
        # Limpiar zonas de ataque anteriores
        if self.zona_ataque_trafico:
            self.zona_ataque_trafico.remove()
            self.zona_ataque_trafico = None
        if self.zona_ataque_suma:
            self.zona_ataque_suma.remove()
            self.zona_ataque_suma = None
            
        # Crear un nuevo detector con datos frescos
        self.detector = DetectorAnomalias()
        self.detector.generar_datos()
        
        # Restablecer etiquetas e información
        self.label_ataque_info.config(text="Buscando anomalías...", fg="blue")
        
        # Resetear variables de control
        self.anomalia_detectada = False
        self.alerta_mostrada = False
        self.indice_deteccion = None
        self.mostrar_alerta_pendiente = False

# Punto de entrada principal
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionTiempoReal(root)
    root.mainloop() 