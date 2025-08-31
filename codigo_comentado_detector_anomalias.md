# Código Comentado: Detector de Anomalías en Tráfico de Red

Este documento presenta las partes más relevantes del código del detector de anomalías, enfocándose en la implementación del algoritmo CUSUM y la lógica de detección, dejando de lado aspectos visuales y de interfaz gráfica.

Para ver el documento técnico completo y los fundamentos matemáticos, consulta el [documento técnico](documento_tecnico_detector_anomalias.md).

## 1. Clase DetectorAnomalias - Núcleo del Sistema

```python
import numpy as np

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
        
        El algoritmo se define como:
        S₀ = 0
        S𝑡 = max(0, S𝑡₋₁ + (x𝑡 - μ))
        
        Donde:
        - S𝑡: Suma acumulada en el tiempo t
        - x𝑡: Valor observado en el tiempo t
        - μ: Media del tráfico normal (línea base)
        """
        # Calcula línea base usando los primeros 5 segundos (periodo de estabilización)
        ventana_base = 5 * self.muestras_por_segundo
        linea_base = np.mean(self.trafico[:ventana_base])
        
        # Implementación del algoritmo CUSUM
        for i in range(1, self.total_muestras):
            # La función max garantiza que la suma acumulada nunca sea negativa
            self.suma_acumulada[i] = max(0, self.suma_acumulada[i-1] + (self.trafico[i] - linea_base))
    
    def calcular_umbral_estadistico(self):
        """
        Calcula un umbral estadístico adaptativo basado en media + 3 desviaciones estándar
        usando una ventana deslizante de 5 segundos.
        
        Este umbral se adapta a las variaciones normales del tráfico, reduciendo falsos positivos.
        """
        ventana = 5 * self.muestras_por_segundo  # Tamaño de ventana = 5 segundos
        
        for i in range(ventana, self.total_muestras):
            # Calcula estadísticas de la ventana anterior
            media = np.mean(self.suma_acumulada[i-ventana:i])
            desv_est = np.std(self.suma_acumulada[i-ventana:i])
            
            # Umbral = media + 3*desviación estándar (regla 3-sigma)
            # Esta regla estadística considera como anomalía cualquier valor
            # que exceda la media más 3 veces la desviación estándar
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
        # Se utilizan dos umbrales:
        # 1. Umbral fijo: valor constante predefinido
        # 2. Umbral estadístico: basado en estadísticas recientes
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
```

## 2. Ejemplo de Uso - Detección Offline

Este fragmento de código muestra cómo utilizar el detector de anomalías para analizar un conjunto de datos completo de una sola vez:

```python
def ejemplo_deteccion_offline():
    # Crear instancia del detector
    detector = DetectorAnomalias(ventana_tiempo=60, muestras_por_segundo=60)
    
    # Generar datos simulados con ataque
    detector.generar_datos()
    
    # Calcular suma acumulada para todo el conjunto
    detector.calcular_suma_acumulada()
    
    # Calcular umbral estadístico
    detector.calcular_umbral_estadistico()
    
    # Buscar anomalías en todo el conjunto
    anomalias = []
    for i in range(detector.total_muestras):
        if detector.detectar_anomalia(i):
            anomalias.append(i / detector.muestras_por_segundo)  # Convertir a segundos
            
    # Verificar si se detectó el ataque simulado
    ataque_detectado = any(abs(t - detector.momento_real_ataque) < 1.0 for t in anomalias)
    
    print(f"Ataque simulado en t={detector.momento_real_ataque:.2f}s")
    if ataque_detectado:
        print(f"Ataque detectado con éxito. Puntos de detección: {anomalias}")
        print(f"Tiempo de respuesta: {min([abs(t - detector.momento_real_ataque) for t in anomalias]):.2f}s")
    else:
        print("El ataque no fue detectado.")
        
    return detector, anomalias
```

## 3. Ejemplo de Uso - Detección en Tiempo Real

Este fragmento muestra cómo el detector procesa los datos en tiempo real, paso a paso:

```python
def ejemplo_deteccion_tiempo_real():
    # Crear instancia del detector
    detector = DetectorAnomalias(ventana_tiempo=60, muestras_por_segundo=60)
    
    # Generar datos simulados con ataque
    detector.generar_datos()
    
    # Simulación de procesamiento en tiempo real
    detecciones = []
    
    # Procesar cada punto temporal
    while detector.indice_actual < detector.total_muestras:
        # Procesar punto actual
        if detector.procesar_paso():
            # Se ha detectado una anomalía
            tiempo_deteccion = detector.indice_actual / detector.muestras_por_segundo
            detecciones.append(tiempo_deteccion)
            print(f"Anomalía detectada en t={tiempo_deteccion:.2f}s")
            
        # En un sistema real, aquí habría una pausa para simular el tiempo real
        # time.sleep(1/detector.muestras_por_segundo)
    
    # Evaluar efectividad de la detección
    print(f"Ataque real en t={detector.momento_real_ataque:.2f}s")
    if detector.anomalia_detectada:
        print(f"Ataque detectado en t={detector.momento_deteccion:.2f}s")
        print(f"Tiempo de respuesta: {detector.momento_deteccion - detector.momento_real_ataque:.2f}s")
    else:
        print("El ataque no fue detectado.")
        
    return detector, detecciones
```

## 4. Aspectos Críticos del Algoritmo

### 4.1 Cálculo de la Suma Acumulada (CUSUM)

La parte más crítica del algoritmo es el cálculo de la suma acumulada, implementado en el método `calcular_suma_acumulada()`. Esta función implementa directamente la ecuación del algoritmo CUSUM:

```python
S𝑡 = max(0, S𝑡₋₁ + (x𝑡 - μ))
```

La implementación Python:

```python
self.suma_acumulada[i] = max(0, self.suma_acumulada[i-1] + (self.trafico[i] - linea_base))
```

### 4.2 Determinación de Umbrales

El detector utiliza dos umbrales complementarios:

1. **Umbral fijo**: Un valor constante (2000 en la implementación actual), útil como referencia absoluta
2. **Umbral estadístico**: Calculado dinámicamente como `media + 3 * desviación_estándar`, que se adapta a las características del tráfico

### 4.3 Detección en Tiempo Real

El método `procesar_paso()` es fundamental para la detección en tiempo real, ya que:

1. Actualiza la suma acumulada para el punto temporal actual
2. Calcula el umbral estadístico dinámico basado en la ventana de tiempo reciente
3. Comprueba si la suma acumulada supera alguno de los umbrales
4. Registra el momento exacto de la primera detección

## 5. Parámetros Críticos

Los siguientes parámetros afectan directamente el rendimiento del detector:

- **media_trafico_normal**: Nivel base esperado de tráfico
- **desviacion_trafico_normal**: Variabilidad normal del tráfico
- **umbral_fijo**: Límite absoluto para la suma acumulada
- **factor_multiplicador**: Factor usado para el umbral estadístico (2.5 o 3)
- **ventana_base**: Tamaño de la ventana para calcular la línea base (5 segundos)
- **ventana_estadistica**: Tamaño de la ventana para calcular el umbral estadístico (5 segundos)

En un entorno real, estos parámetros deberían ajustarse según las características específicas de la red monitoreada.

---

**Referencias**:  
Para una explicación detallada de los fundamentos matemáticos y la implementación completa, consulta el [documento técnico completo](documento_tecnico_detector_anomalias.md). 