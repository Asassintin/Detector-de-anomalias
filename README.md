# Detector de Anomalías en Tráfico de Red usando Algoritmo CUSUM

## 🌐 Descripción del Proyecto

Este proyecto implementa un sistema de detección de anomalías en tráfico de red en tiempo real utilizando el algoritmo CUSUM (Suma Acumulativa). El sistema simula tráfico de red, introduce ataques aleatorios (DoS/DDoS), y detecta estas anomalías a través de alertas visuales y auditivas. Cuenta con una interfaz gráfica interactiva construida con Python, convirtiéndolo en una excelente herramienta educativa para entender conceptos de ciberseguridad y algoritmos matemáticos aplicados a la seguridad de redes.

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![Matplotlib](https://img.shields.io/badge/matplotlib-latest-green.svg)
![NumPy](https://img.shields.io/badge/numpy-latest-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/Asassintin/Detector-de-anomalias.git
cd Detector-de-anomalias

# Instalar dependencias
pip install numpy matplotlib

# Ejecutar la aplicación (versión GUI)
python "detector_anomalias v2.py"

# O ejecutar versión estática (compatible con headless)
cd "Detector de anomalias Versiones"
python "deteccion_anomalias Estatico.py"
```

## 🎯 Características Principales

- **Detección de Anomalías en Tiempo Real**: Utiliza el algoritmo CUSUM para detección estadística de anomalías
- **GUI Interactiva**: Hermosa interfaz basada en Tkinter con visualizaciones en tiempo real
- **Detección de Doble Umbral**: Implementa umbrales fijos y estadísticos adaptativos
- **Simulación de Ataques**: Simula ataques DoS/DDoS con parámetros configurables
- **Alertas Visuales**: Gráficos en tiempo real mostrando patrones de tráfico y detección de anomalías
- **Notificaciones de Audio**: Alertas sonoras cuando se detectan anomalías (Windows)
- **Explicación Matemática**: Contenido educativo integrado explicando el algoritmo CUSUM
- **Múltiples Versiones**: Diferentes implementaciones para aprendizaje y comparación

## 📊 Fundamento Matemático

### Algoritmo CUSUM

El algoritmo de Suma Acumulativa (CUSUM) es un método estadístico para detectar cambios abruptos en datos de series temporales. En el contexto de seguridad de redes, ayuda a identificar desviaciones de tráfico que pueden indicar ataques.

**Fórmula Matemática:**
```
S₀ = 0
Sₜ = max(0, Sₜ₋₁ + (xₜ - μ))
```

Donde:
- `Sₜ`: Suma acumulativa en el tiempo t
- `xₜ`: Valor de tráfico en el tiempo t
- `μ`: Línea base (media del tráfico normal)
- `max(0,·)`: Previene acumulación negativa

### Detección de Umbrales

El sistema utiliza dos métodos de detección:

1. **Umbral Fijo**: `Sₜ > h` (donde h = 2000)
2. **Umbral Estadístico**: `Sₜ > μw + k·σw` (donde k = 2.5)

## 📁 Estructura del Repositorio

### 🐍 Archivos de Implementación en Python

- **`detector_anomalias v2.py`** - Aplicación principal con GUI y detección en tiempo real
- **`Detector de anomalias Versiones/`** - Directorio que contiene diferentes versiones:
  - `detector_anomalias v2 -corregido.py` - Versión 2 corregida
  - `detector_anomalias v3 - copia.py` - Versión 3 con características mejoradas
  - `deteccion_anomalias Estatico.py` - Versión de análisis estático sin GUI

### 📚 Archivos de Documentación

- **`documento_tecnico_detector_anomalias.md`** - Documentación técnica completa (Español)
- **`codigo_comentado_detector_anomalias.md`** - Documentación detallada del código con comentarios
- **`Proyecto Detección de Anomalías en Tráfico de Red.md`** - Descripción del proyecto y fundamentos matemáticos
- **`Explicacion Codigo.txt`** - Explicación del código y resumen de arquitectura

### 🎥 Archivos Multimedia

- **`Demo Detector de Anomalias.mp4`** - Video demostración de la aplicación
- **`Documento Técnico Detector de Anomalías en Tráfico de Red.pdf`** - Versión PDF de la documentación técnica
- **`Proyecto Mates.docx`** - Documentación del proyecto matemático

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.6 o superior
- Gestor de paquetes pip

### Dependencias Requeridas

```bash
pip install numpy matplotlib
```

### Requisitos del Sistema

**Para la Versión GUI (`detector_anomalias v2.py`):**
- `tkinter` - Interfaz GUI (incluido con la mayoría de instalaciones de Python)
- `winsound` - Alertas de audio (Solo Windows, opcional)
- Entorno de visualización (no adecuado para servidores headless)

**Para la Versión de Análisis Estático (`deteccion_anomalias Estatico.py`):**
- Funciona en entornos headless
- No requiere dependencias de GUI
- Adecuado para entornos de servidor y procesamiento por lotes

### Dependencias Adicionales (Integradas)
- `random` - Para simulación de ataques
- `datetime` - Para formateo de marcas de tiempo

## 🎮 Instrucciones de Uso

### Ejecutar la Aplicación Principal (Versión GUI)

```bash
python "detector_anomalias v2.py"
```

**Nota**: Requiere un entorno de visualización (escritorio/GUI). No adecuado para servidores headless.

### Ejecutar la Versión de Análisis Estático

```bash
cd "Detector de anomalias Versiones"
python "deteccion_anomalias Estatico.py"
```

**Características**: Funciona en cualquier entorno, genera gráficos estáticos, adecuado para análisis por lotes.

### Versiones Alternativas

```bash
# Versión mejorada con temas
python "Detector de anomalias Versiones/detector_anomalias v3 - copia.py"

# Versión 2 corregida
python "Detector de anomalias Versiones/detector_anomalias v2 -corregido.py"
```

### Interfaz de la Aplicación

1. **Pantalla de Inicio**: Animación de carga profesional
2. **Interfaz Principal**: 
   - Visualización de tráfico en tiempo real
   - Gráfico de suma acumulativa con umbrales
   - Botones de control (Iniciar/Reiniciar simulación)
   - Pantallas de información
3. **Explicación Matemática**: Haz clic en el botón "?" para la teoría CUSUM

### Controles de Interfaz

- **Iniciar/Reiniciar**: Comenzar o reiniciar la simulación
- **Alternador de Tema**: Cambiar entre temas claro y oscuro (v3)
- **Control de Velocidad**: Ajustar velocidad de simulación (v3)
- **Ayuda**: Acceder a explicaciones matemáticas

## 🔧 Arquitectura del Sistema

### Clases Principales

1. **`DetectorAnomalias`**: 
   - Implementa el algoritmo CUSUM
   - Genera datos de tráfico simulado
   - Gestiona cálculos de umbrales
   - Maneja la lógica de detección de anomalías

2. **`AplicacionTiempoReal`**: 
   - Gestiona la interfaz GUI
   - Maneja la visualización en tiempo real
   - Controla animación y actualizaciones
   - Gestiona interacciones del usuario

3. **`ExplicacionMatematica`**: 
   - Proporciona contenido educativo
   - Explica el algoritmo CUSUM
   - Sistema de ayuda interactivo

4. **`PantallaCarga`**: 
   - Pantalla de carga profesional
   - Animaciones suaves

### Flujo de Datos

```
Generación de Tráfico → Cálculo CUSUM → Comparación de Umbrales → Detección de Anomalías → Alertas Visuales/Audio
```

## 📈 Parámetros del Algoritmo

### Simulación de Tráfico
- **Media de Tráfico Normal**: 100 paquetes/segundo
- **Desviación Estándar de Tráfico Normal**: 15 paquetes/segundo
- **Multiplicador de Ataque**: 3x tráfico normal
- **Duración del Ataque**: 0.5 segundos
- **Ventana de Simulación**: 60 segundos
- **Tasa de Muestreo**: 60 muestras/segundo

### Umbrales de Detección
- **Umbral Fijo**: 2000
- **Umbral Estadístico**: μ + 2.5σ (adaptativo)
- **Tamaño de Ventana**: 5 segundos para cálculos estadísticos

## 🛡️ Aplicaciones de Seguridad

Este sistema demuestra la detección de:

- Ataques **DoS (Denegación de Servicio)**
- Ataques **DDoS (Denegación de Servicio Distribuida)**
- Ataques de **inundación de red**
- **Anomalías de tráfico** y patrones inusuales

## 📊 Características de Visualización

### Gráficos en Tiempo Real
1. **Gráfico de Volumen de Tráfico**: Muestra el tráfico de red a lo largo del tiempo
2. **Gráfico de Suma Acumulativa**: Muestra valores CUSUM y umbrales
3. **Resaltado de Anomalías**: Marcadores visuales para ataques detectados
4. **Líneas de Umbral**: Tanto umbrales fijos como adaptativos

### Sistema de Alertas
- **Alertas Visuales**: Cambios de color y resaltado
- **Alertas de Audio**: Notificaciones sonoras (Windows)
- **Pantalla de Información**: Métricas de tiempo de ataque y respuesta

## 🎓 Valor Educativo

Este proyecto sirve como una excelente herramienta educativa para:

- **Ciberseguridad**: Comprender métodos de detección de ataques
- **Matemáticas**: Aplicación práctica de algoritmos estadísticos
- **Programación**: Desarrollo de GUI y procesamiento de datos en tiempo real
- **Análisis de Datos**: Análisis de series temporales y detección de anomalías

## 📖 Idiomas de Documentación

- **Español**: Documentación original (detalles técnicos completos)
- **Inglés**: Este README y comentarios de código
- **Notación Matemática**: Expresiones matemáticas universales

## 🔍 Diferencias entre Versiones

### Versión 2 (`detector_anomalias v2.py`)
- Implementación básica de GUI
- Detección en tiempo real
- Umbrales fijos y estadísticos
- Alertas de audio

### Versión 2 Corregida (`detector_anomalias v2 -corregido.py`)
- Correcciones de errores y mejoras
- Visualización mejorada
- Mejor manejo de errores

### Versión 3 (`detector_anomalias v3 - copia.py`)
- Soporte de tema oscuro/claro
- Controles de velocidad
- Diseño de UI mejorado
- Opciones de configuración adicionales

### Versión Estática (`deteccion_anomalias Estatico.py`)
- Análisis no interactivo
- Capacidad de procesamiento por lotes
- Visualizaciones y gráficos estáticos
- Demostraciones educativas
- **Compatible con entornos headless**
- Genera figuras matplotlib
- Análisis basado en marcas de tiempo

## 🤝 Contribuciones

Para contribuir a este proyecto:

1. Haz fork del repositorio
2. Crea una rama de características
3. Realiza tus cambios
4. Añade pruebas si es aplicable
5. Actualiza la documentación
6. Envía un pull request

## 📝 Licencia

Este proyecto está disponible para propósitos educativos y de investigación. Por favor, consulta con los autores originales para permisos de uso comercial.

## 🏆 Contexto del Proyecto

Este proyecto fue desarrollado como parte de un estudio matemático y de ciberseguridad, demostrando la aplicación práctica de conceptos de cálculo integral (sumas acumulativas) en seguridad de redes. Muestra cómo los algoritmos matemáticos pueden aplicarse a desafíos de ciberseguridad del mundo real.

## 🔧 Solución de Problemas

### Problemas Comunes

**"No module named 'tkinter'"**
- Solución: Instala tkinter o usa la versión estática
- Alternativa: `sudo apt-get install python3-tk` (Linux)
- Usa la versión estática para entornos headless

**"No module named 'winsound'"**
- Normal en sistemas no Windows
- Las alertas de audio se deshabilitarán automáticamente
- No afecta la funcionalidad principal

**GUI no se muestra**
- Asegúrate de tener un entorno de visualización
- Prueba la versión estática: `deteccion_anomalias Estatico.py`
- Para servidores, usa gráficos headless con matplotlib

### Ajuste de Rendimiento

**El detector no encuentra anomalías:**
- Ajusta el parámetro `umbral_fijo` (predeterminado: 2000)
- Valores más bajos = detección más sensible
- Valores más altos = menos falsos positivos

**Simulación muy rápida/lenta:**
- Modifica el parámetro `muestras_por_segundo`
- Ajusta `ventana_tiempo` para la duración de simulación

## 🧪 Pruebas

El algoritmo central de detección ha sido validado:
- ✅ Precisión del cálculo CUSUM
- ✅ Detección de anomalías con umbrales configurables
- ✅ Simulación de ataques con parámetros realistas
- ✅ Medición de tiempo de respuesta (típicamente < 0.5 segundos)
- ✅ Compatibilidad multiplataforma (Windows/Linux/Mac)

## 📞 Soporte

Para preguntas o soporte:
- Revisa la documentación técnica en `documento_tecnico_detector_anomalias.md`
- Consulta los comentarios del código en `codigo_comentado_detector_anomalias.md`
- Ve el video de demostración `Demo Detector de Anomalias.mp4`

---

*Este proyecto demuestra la intersección de matemáticas, programación y ciberseguridad a través de la implementación práctica de algoritmos de detección de anomalías.*