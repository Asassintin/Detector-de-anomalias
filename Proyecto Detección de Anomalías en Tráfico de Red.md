# Proyecto: Detección de Anomalías en Tráfico de Red con Integrales.

## **Objetivo**

El objetivo de este proyecto es aplicar el concepto de **integral definida** para calcular el área bajo la curva del tráfico de red y detectar picos anómalos que puedan indicar posibles ataques (como *floods* o *Denial of Service*).

---

## **Fundamento Matemático**

La integral definida permite calcular la acumulación de una cantidad a lo largo del tiempo. En este caso, se utiliza para sumar el tráfico de red de manera acumulativa y compararlo con un umbral predefinido. Si el valor de la integral supera dicho umbral, se activa una alerta de posible anomalía.

**Temas aplicados:**

- Integral definida (suma acumulada de tráfico).
- Comparación de umbrales (regla básica de detección).
    
    **Herramientas:**
    
- Python con `numpy` (cálculos) para sumar datos y `matplotlib` para gráficar (visualización).

**Ejemplo simplificado:**

- Datos: Lista de paquetes/segundo en una red.

---

## **Definición de la Integral en este Contexto**

En matemáticas, la **integral definida** de una función $*f(t)*$ en un intervalo $[a,b]$ representa el **área bajo la curva** desde $*a*$ hasta $*b*$.

En el caso del tráfico de red:

- **$*f(t) =*$** Cantidad de paquetes por segundo en el instante $*t*$.
- **Integral acumulada** = Suma total de paquetes desde el inicio ($*t=0*$) hasta un tiempo $*t*$.

### **¿Por qué usar integrales?**

- Si un ataque (ej: *DDoS*) genera un pico repentino de tráfico, la integral crecerá más rápido de lo normal.
- Al comparar con un **umbral**, podemos detectar anomalías sin depender solo del valor instantáneo.

---

## **Intervalos de Tiempo y Discretización**

En la práctica, el tráfico de red se mide en **intervalos discretos** (cada segundo o cada minuto).

### **Ejemplo con datos discretos**

Supongamos que medimos paquetes/segundo:

| **Tiempo (s)** | **0** | **1** | **2** | **3** | **4** | **5** |
| --- | --- | --- | --- | --- | --- | --- |
| Paquetes | 10 | 12 | 15 | 100 | 10 | 11 |

La **integral discreta (suma acumulada)** sería:

- En $*t=0: S(0)=10*$
- En $*t=1: S(1)=10+12=22*$
- En $*t=2: S(2)=22+15=37*$
- En $*t=3: S(3)=37+100=137$ . (¡Pico!)*
- ...

En Python, esto se calcula con `np.cumsum()`.

---

## **¿Cómo Definir los Intervalos?**

Depende de la granularidad de los datos:

1. **Si los datos son en tiempo real** (ej: paquetes/segundo):
    - La integral se actualiza cada segundo.
    - Ejemplo: `np.cumsum([10, 12, 15, 100, ...])`.
2. **Si los datos son agregados** (ej: tráfico por minuto):
    - La integral suma valores por bloques de tiempo.
    - Ejemplo: `np.cumsum([200, 150, 5000, ...])` (paquetes/minuto).

---

## **¿Cómo Definir el Umbral?**

El umbral depende del **comportamiento normal** de la red:

- **Método 1**: Umbral fijo (ej: 50 paquetes/segundo).
    - Si $*S(t) > 50*$, hay alerta.
- **Método 2**: Umbral dinámico (estadístico).
    - Usar la media $+ 2$ desviaciones estándar del tráfico histórico.

### **Ejemplo de umbral estadístico en Python**

```python
import numpy as np

trafico_normal = np.array([10, 12, 15, 10, 11])  # Datos históricos
media = np.mean(trafico_normal)
desviacion = np.std(trafico_normal)
umbral = media + 2 * desviacion  # Ej: 15 + 2*2 = 19
```

## **¿Por qué Funciona para Ciberseguridad?**

- **Ataques de Flood**: Envían una gran cantidad de paquetes en poco tiempo, causando que $*S(t)*$ aumente de manera abrupta.
- **Ejemplo**:
    - Tráfico normal: `[10, 12, 15, 10, 11]` → $*S(t)*$ crece gradualmente.
    - Ataque DDoS: `[10, 12, 15, 1000, 10]` → $*S(3) = 1037*$ (supera el umbral).

---

## **Ejemplo Matemático con Función Continua**

### **Caso Ideal (Función Continua):**

Supongamos que el tráfico normal sigue una función suave con un pico abrupto (ataque):

$$
f(t) = \begin{cases} 10 + 2t & \text{para } 0 \leq t \leq 3 \quad \text{(Comportamiento normal)} \\100 & \text{para } t = 3.5 \quad \text{(Ataque)} \\10 & \text{para } 3.5 < t \leq 5 \quad \text{(Retorno a normalidad)}\end{cases}
$$

### **Cálculo de la Integral Definida:**

Queremos calcular el tráfico acumulado entre $t=0$ y $t=5$:

$$
S(t) = \int_{0}^{5} f(t) \, dt
$$

### **Descomposición por intervalos:**

1. **De 0 a 3** (Crecimiento lineal normal):

$$
\int_{0}^{3} (10 + 2t) \, dt = \left[ 10t + t^2 \right]_{0}^{3} = 30 + 9 = 39
$$

1. **En $t=3.5$** (Pico de ataque como impulso):
    - En un sistema discreto, sería un valor puntual: $100$ paquetes.
    - En modelo continuo, aproximamos como un delta: $\int_{3}^{4} f(t) \, dt ≈100$
2. **De 4 a 5** (Normalidad): 

$$
\int_{4}^{5} 10 \, dt = 10 \times (5 - 4) = 10
$$

### **Total acumulado (aproximado):**

$S(5)≈39+100+10=149$  (Mucho mayor que el tráfico normal)

---

## **Versión Discreta (Aplicación Real con Datos)**

### **Datos Muestreados (Paquetes/Segundo):**

| **Tiempo (s)** | **0** | **1** | **2** | **3** | **4** | **5** |
| --- | --- | --- | --- | --- | --- | --- |
| $f(t)$ | 10 | 12 | 15 | 100 | 10 | 11 |

### **Integral Discreta (Suma Acumulada):**

$$
S(t) = \sum_{k=0}^{t} f(k)
$$

- $S(0) = 10$
- $S(1) = 10 + 12 = 22$
- $S(2) = 22 + 15 = 37$
- $S(3) = 37 + 100 = 137$ *(¡Pico de ataque!)*
- $S(4) = 137 + 10 = 147$
- $S(5) = 147 + 11 = 158$

### **Detección de Anomalía:**

Si definimos un **umbral** $U = 50$:

- $S(3) = 137 > 50$ → **¡Alerta!** (Exceso de tráfico en $t = 3$).
    - La **integral definida** cuantifica el tráfico acumulado, permitiendo detectar picos abruptos.
    - En la práctica, se usa la **suma acumulada discreta** (equivalente a la integral en tiempo muestreado).
    - El método es eficaz para ataques que generan **grandes volúmenes de tráfico en poco tiempo** (DDoS, scans).

---

### **Actividad Práctica: Simulación del Ataque**

Desarrolla un programa en **Python** que:

1. Genere datos simulados de tráfico de red normal durante 1 minuto (60 muestras por segundo)
2. Inserte un ataque simulado (pico de tráfico) en un momento aleatorio
3. Implemente la detección de anomalías usando el método de integral discreta (suma acumulada)
4. Gráfique:
    - El tráfico original vs tiempo
    - La suma acumulada vs tiempo
    - El umbral de detección
5. Muestre una alerta cuando se detecte la anomalía, indicando el momento exacto

**Requerimientos adicionales:**

- Usar `NumPy` para los cálculos y `Matplotlib` para las gráficas
- Implementar al menos dos métodos diferentes para definir el umbral (fijo y estadístico)
- Documentar el código con comentarios explicativos
- Incluir una breve explicación matemática de cómo funciona la detección

---

**Entregables:**

1. **Presentación técnica (3-5 min)**:
    - Explica tu tema y la parte matemática.
    - Muestra tu código en vivo.
2. **Documento Técnico**: (Imprimir el reporte)
    - Parte matemática y descripción técnica de los ataques.
    - La relación de esos ataques con las integrales.
    - Explicación técnica del código (librerías, etc.) y lógica de programación.
3. **Código Comentado**:
    - Sube a Notion con comentarios explicativos, y explica paso a paso tu código.
    - Anexa el link al documento técnico.