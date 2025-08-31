# Documento Técnico: Detector de Anomalías en Tráfico de Red

## 1. Introducción

Este documento presenta el desarrollo de un sistema de detección de anomalías en tráfico de red utilizando el algoritmo de Suma Acumulada (CUSUM). El proyecto implementa una solución visual e interactiva que permite detectar posibles ataques como inundaciones (floods) o Denegación de Servicio (DoS/DDoS) en tiempo real.

## 2. Fundamento Matemático

### 2.1 El Algoritmo CUSUM

El algoritmo CUSUM (Cumulative Sum) es una técnica estadística desarrollada para detectar cambios abruptos en series temporales. En el contexto de la seguridad de redes, CUSUM permite identificar desviaciones significativas del comportamiento normal del tráfico.

#### Formulación matemática

La base matemática del algoritmo CUSUM se puede expresar mediante la siguiente ecuación recursiva:

S₀ = 0

S𝑡 = max(0, S𝑡₋₁ + (x𝑡 - μ))

Donde:
- S𝑡 es la suma acumulada hasta el tiempo t
- x𝑡 es el valor observado en el tiempo t (volumen de tráfico)
- μ es el valor esperado o línea base (media del tráfico en condiciones normales)
- max(0,·) es una función que impide que la suma acumulada sea negativa

Este enfoque puede interpretarse como una forma de integral discreta que acumula las desviaciones respecto a una línea base, permitiendo detectar variaciones significativas que podrían pasar desapercibidas con métodos menos sofisticados.

### 2.2 Umbrales de Detección

Para determinar cuándo se considera que un valor de CUSUM representa una anomalía, se utilizan dos tipos de umbrales:

1. **Umbral fijo**: Un valor constante determinado empíricamente.
   
   S𝑡 > h
   
   Donde h es el umbral fijo (en nuestra implementación, h = 2000).

2. **Umbral estadístico dinámico**: Se calcula a partir de las estadísticas recientes de la propia suma acumulada.
   
   S𝑡 > μ𝑤 + k·σ𝑤
   
   Donde:
   - μ𝑤 es la media de la suma acumulada en una ventana temporal reciente
   - σ𝑤 es la desviación estándar en esa misma ventana
   - k es un factor multiplicador (en nuestra implementación, k = 2.5)

## 3. Descripción Técnica de Ataques de Red

### 3.1 Ataques de Denegación de Servicio (DoS/DDoS)

Los ataques de Denegación de Servicio tienen como objetivo hacer que un sistema o recurso sea inaccesible para los usuarios legítimos. Se caracterizan por:

- **Volumen anormal**: Generación de un tráfico significativamente mayor al habitual
- **Patrones anómalos**: Distribución temporal y características del tráfico que difieren del comportamiento normal
- **Duración variable**: Pueden ser breves pero intensos, o sostenidos durante períodos más largos

En un ataque DDoS (Denegación de Servicio Distribuida), múltiples fuentes coordinadas generan tráfico malicioso hacia un objetivo, dificultando aún más su detección y mitigación.

### 3.2 Floods (Inundaciones)

Los ataques de tipo "flood" son una subcategoría de DoS que consisten en enviar un gran volumen de paquetes o solicitudes en un corto periodo de tiempo. Los tipos más comunes incluyen:

- **TCP SYN Flood**: Sobrecarga de solicitudes de inicio de conexión TCP
- **UDP Flood**: Envío masivo de paquetes UDP a puertos aleatorios
- **ICMP Flood**: Inundación con paquetes ICMP (ping)
- **HTTP Flood**: Solicitudes HTTP/HTTPS en gran volumen

En nuestra simulación, modelamos estos ataques como un incremento súbito en el volumen de tráfico, multiplicando la media normal por un factor determinado.

## 4. Relación entre CUSUM y Detección de Ataques

El algoritmo CUSUM resulta particularmente eficaz para detectar ataques de red por las siguientes razones:

1. **Sensibilidad a cambios abruptos**: CUSUM acumula las desviaciones, lo que permite detectar picos de tráfico característicos de ataques DoS y flood.

2. **Memoria del sistema**: A diferencia de los métodos que solo consideran el valor actual, CUSUM "recuerda" el comportamiento reciente, lo que permite detectar ataques distribuidos en el tiempo.

3. **Adaptabilidad**: Mediante el uso de umbrales dinámicos, el sistema puede adaptarse a diferentes patrones de tráfico normal.

4. **Reducción de falsos positivos**: Al requerir que la suma acumulada supere un umbral significativo, se reducen las alertas por fluctuaciones normales del tráfico.

### Equivalencia con el concepto de integral definida

En términos matemáticos, CUSUM puede interpretarse como una aproximación discreta a la integral de las desviaciones respecto a la línea base:

CUSUM ≈ ∫₀ᵗ (f(τ) - μ) dτ

Donde f(τ) representa el tráfico en el instante τ.

Esta integral acumula el "exceso" de tráfico sobre lo normal, creciendo rápidamente cuando ocurre un ataque y permitiendo su detección temprana.

## 5. Implementación Técnica

### 5.1 Librerías Utilizadas

El sistema se implementa utilizando las siguientes librerías de Python:

- **NumPy**: Para operaciones matemáticas eficientes con arrays y funciones estadísticas.
- **Matplotlib**: Para la visualización en tiempo real de los datos y resultados del análisis.
- **Tkinter**: Para crear la interfaz gráfica de usuario interactiva.
- **winsound**: Para notificaciones sonoras cuando se detectan anomalías.

### 5.2 Arquitectura del Sistema

El sistema se estructura en las siguientes clases principales:

1. **DetectorAnomalias**: Implementa la lógica central del algoritmo CUSUM:
   - Generación de datos simulados
   - Cálculo de la suma acumulada
   - Determinación de umbrales
   - Detección de anomalías

2. **AplicacionTiempoReal**: Gestiona la interfaz gráfica y la visualización:
   - Gráficas en tiempo real
   - Control de la simulación
   - Alertas visuales y sonoras

3. **ExplicacionMatematica**: Proporciona una ventana informativa sobre la base matemática del algoritmo.

4. **PantallaCarga**: Implementa una animación de inicio profesional.

### 5.3 Lógica de Programación

#### Generación de datos simulados

```python
def generar_datos(self):
    # Generación de tráfico normal usando distribución gaussiana
    self.trafico = np.random.normal(
        self.media_trafico_normal, 
        self.desviacion_trafico_normal, 
        self.total_muestras
    )
    
    # Inserción del ataque: añade un pico de tráfico
    self.trafico[self.inicio_ataque:self.fin_ataque] += (self.media_trafico_normal 
                                                      * self.factor_ataque 
                                                      * np.ones(self.duracion_ataque))
```

El tráfico normal se modela mediante una distribución gaussiana, mientras que el ataque se simula incrementando el tráfico base por un factor multiplicativo durante un intervalo de tiempo aleatorio.

#### Implementación del algoritmo CUSUM

```python
def calcular_suma_acumulada(self):
    # Calcula línea base usando los primeros 5 segundos
    ventana_base = 5 * self.muestras_por_segundo
    linea_base = np.mean(self.trafico[:ventana_base])
    
    # Implementación del algoritmo CUSUM
    # S_t = max(0, S_{t-1} + (x_t - μ))
    for i in range(1, self.total_muestras):
        self.suma_acumulada[i] = max(0, self.suma_acumulada[i-1] + (self.trafico[i] - linea_base))
```

El algoritmo calcula una línea base a partir de los primeros segundos de tráfico y luego aplica la fórmula recursiva de CUSUM para acumular las desviaciones.

#### Cálculo de umbral estadístico dinámico

```python
def calcular_umbral_estadistico(self):
    ventana = 5 * self.muestras_por_segundo  # Tamaño de ventana = 5 segundos
    
    for i in range(ventana, self.total_muestras):
        # Calcula estadísticas de la ventana anterior
        media = np.mean(self.suma_acumulada[i-ventana:i])
        desv_est = np.std(self.suma_acumulada[i-ventana:i])
        
        # Umbral = media + 3*desviación estándar (regla 3-sigma)
        self.umbral_estadistico[i] = media + 3 * desv_est
```

El umbral dinámico se calcula utilizando la regla de tres sigmas (media + 3 desviaciones estándar) sobre una ventana deslizante de 5 segundos.

#### Detección de anomalías en tiempo real

```python
def detectar_anomalia(self, indice, en_tiempo_real=False):
    # No evaluar durante el periodo inicial de estabilización
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
```

La detección se realiza comparando el valor actual de CUSUM con los umbrales establecidos, activando una alerta cuando se superan.

### 5.4 Visualización y Alertas

El sistema presenta dos gráficas principales:

1. **Tráfico de red en tiempo real**: Muestra el volumen de tráfico por segundo.
2. **Suma acumulada y umbrales**: Visualiza el valor de CUSUM y los umbrales de detección.

Cuando se detecta una anomalía:
- Se resalta la zona del ataque en ambas gráficas
- Se emite una alerta sonora
- Se muestra un mensaje con información sobre el momento del ataque y su detección
- Se anima visualmente el panel de información para llamar la atención del operador

## 6. Resultados y Conclusiones

### 6.1 Eficacia del Sistema

En nuestras pruebas, el sistema ha demostrado ser capaz de:

- Detectar anomalías con un tiempo de respuesta promedio de menos de 1 segundo después del inicio del ataque.
- Mantener una tasa de falsos positivos baja gracias al uso combinado de umbrales fijos y estadísticos.
- Visualizar de forma clara y efectiva tanto el tráfico normal como los eventos anómalos.

### 6.2 Limitaciones

- El modelo asume que el tráfico normal sigue una distribución gaussiana, lo cual puede no ser válido en todos los escenarios reales.
- La detección se basa en volumen de tráfico, pero algunos ataques modernos pueden operar con volúmenes bajos pero patrones anómalos.
- La determinación del umbral óptimo requiere ajustes según las características específicas de cada red.

### 6.3 Posibles Mejoras

- Implementar métodos adicionales de detección que consideren características más allá del volumen de tráfico.
- Incorporar aprendizaje automático para adaptar automáticamente los parámetros del detector.
- Añadir capacidad de análisis post-mortem para examinar en detalle los incidentes detectados.

## 7. Conclusión

El detector de anomalías implementado demuestra la eficacia del algoritmo CUSUM para identificar cambios abruptos en el tráfico de red que podrían indicar ataques. La visualización en tiempo real y las alertas permiten a los operadores responder rápidamente ante posibles incidentes de seguridad.

La base matemática sólida de CUSUM, combinada con una implementación eficiente y una interfaz intuitiva, hacen de este sistema una herramienta valiosa para la monitorización de seguridad en redes. 