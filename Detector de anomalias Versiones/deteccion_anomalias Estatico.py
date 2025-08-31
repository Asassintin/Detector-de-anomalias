#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
import datetime
import random

# Configuración de parámetros
DURACION_SEGUNDOS = 60
MUESTRAS_POR_SEGUNDO = 60
NUM_MUESTRAS = DURACION_SEGUNDOS * MUESTRAS_POR_SEGUNDO
MEDIA_TRAFICO_NORMAL = 100  # Bytes por muestra (valor arbitrario)
DESVIACION_TRAFICO_NORMAL = 15  # Desviación estándar del tráfico normal
INTENSIDAD_ATAQUE = 5  # Multiplicador de intensidad del ataque
DURACION_ATAQUE = int(1.5 * MUESTRAS_POR_SEGUNDO)  # 1.5 segundos
UMBRAL_FIJO = 1000  # Umbral fijo para detección
FACTOR_UMBRAL_ESTADISTICO = 3  # Factor multiplicador para umbral estadístico

def generar_trafico_normal(num_muestras, media, desviacion):
    """
    Genera datos de tráfico de red normal simulado utilizando distribución gaussiana.
    
    Args:
        num_muestras: Número total de muestras a generar
        media: Media del tráfico normal
        desviacion: Desviación estándar del tráfico
        
    Returns:
        Array NumPy con los datos de tráfico simulados
    """
    return np.random.normal(media, desviacion, num_muestras)

def insertar_ataque(datos, inicio_ataque, duracion_ataque, intensidad):
    """
    Inserta un ataque simulado (pico de tráfico) en los datos.
    
    Args:
        datos: Array con los datos de tráfico normal
        inicio_ataque: Índice donde comienza el ataque
        duracion_ataque: Duración del ataque en número de muestras
        intensidad: Factor multiplicativo para la intensidad del ataque
        
    Returns:
        Array con los datos modificados que incluyen el ataque
    """
    datos_con_ataque = datos.copy()
    fin_ataque = min(inicio_ataque + duracion_ataque, len(datos))
    
    # Crear un pico de tráfico que represente el ataque
    factor_ataque = np.linspace(1, intensidad, fin_ataque - inicio_ataque)
    datos_con_ataque[inicio_ataque:fin_ataque] *= factor_ataque
    
    return datos_con_ataque

def calcular_suma_acumulada(datos, media_referencia=None):
    """
    Calcula la suma acumulada (CUSUM) para la detección de anomalías.
    
    Args:
        datos: Array con los datos de tráfico
        media_referencia: Media de referencia para el cálculo (si es None, se usa la media de los datos)
        
    Returns:
        Array con la suma acumulada
    """
    if media_referencia is None:
        media_referencia = np.mean(datos)
    
    # La suma acumulada se calcula como la suma de las desviaciones respecto a la media
    desviaciones = datos - media_referencia
    suma_acumulada = np.cumsum(desviaciones)
    
    return suma_acumulada

def calcular_umbral_estadistico(datos_suma_acumulada):
    """
    Calcula un umbral estadístico basado en la desviación estándar de la suma acumulada.
    
    Args:
        datos_suma_acumulada: Array con los datos de suma acumulada
        
    Returns:
        Valor del umbral calculado
    """
    return FACTOR_UMBRAL_ESTADISTICO * np.std(datos_suma_acumulada)

def detectar_anomalia(suma_acumulada, umbral):
    """
    Detecta si hay una anomalía basada en si la suma acumulada cruza el umbral.
    
    Args:
        suma_acumulada: Array con la suma acumulada
        umbral: Valor umbral para la detección
        
    Returns:
        Índice donde se detecta la anomalía, o None si no se detecta
    """
    indices_por_encima = np.where(suma_acumulada > umbral)[0]
    if len(indices_por_encima) > 0:
        return indices_por_encima[0]
    return None

def generar_etiquetas_tiempo(num_muestras, muestras_por_segundo):
    """
    Genera etiquetas de tiempo para los gráficos.
    
    Args:
        num_muestras: Número total de muestras
        muestras_por_segundo: Número de muestras por segundo
        
    Returns:
        Array con objetos datetime y array con valores numéricos para ploteo
    """
    tiempo_inicio = datetime.datetime.now()
    etiquetas_tiempo = [tiempo_inicio + datetime.timedelta(seconds=i/muestras_por_segundo) 
                        for i in range(num_muestras)]
    tiempo_num = date2num(etiquetas_tiempo)
    return etiquetas_tiempo, tiempo_num

def main():
    # Generar datos de tráfico normal
    trafico_normal = generar_trafico_normal(NUM_MUESTRAS, MEDIA_TRAFICO_NORMAL, DESVIACION_TRAFICO_NORMAL)
    
    # Insertar ataque en momento aleatorio
    inicio_ataque = random.randint(int(NUM_MUESTRAS * 0.2), int(NUM_MUESTRAS * 0.8))
    trafico_con_ataque = insertar_ataque(trafico_normal, inicio_ataque, DURACION_ATAQUE, INTENSIDAD_ATAQUE)
    
    # Calcular suma acumulada
    suma_acumulada = calcular_suma_acumulada(trafico_con_ataque)
    
    # Calcular umbrales
    umbral_estadistico = calcular_umbral_estadistico(suma_acumulada)
    
    # Detectar anomalía con ambos métodos
    deteccion_umbral_fijo = detectar_anomalia(suma_acumulada, UMBRAL_FIJO)
    deteccion_umbral_estadistico = detectar_anomalia(suma_acumulada, umbral_estadistico)
    
    # Generar etiquetas de tiempo
    etiquetas_tiempo, tiempo_num = generar_etiquetas_tiempo(NUM_MUESTRAS, MUESTRAS_POR_SEGUNDO)
    
    # Crear figura para gráficas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Formatear ejes para mostrar tiempo
    formatter = DateFormatter('%H:%M:%S')
    
    # Graficar tráfico original
    ax1.plot(tiempo_num, trafico_con_ataque, 'b-', label='Tráfico de red')
    ax1.axvspan(tiempo_num[inicio_ataque], tiempo_num[min(inicio_ataque + DURACION_ATAQUE, NUM_MUESTRAS-1)], 
               alpha=0.3, color='red', label='Ataque real')
    ax1.set_title('Tráfico de Red con Anomalía')
    ax1.set_xlabel('Tiempo')
    ax1.set_ylabel('Bytes por muestra')
    ax1.xaxis.set_major_formatter(formatter)
    ax1.legend()
    ax1.grid(True)
    
    # Graficar suma acumulada
    ax2.plot(tiempo_num, suma_acumulada, 'g-', label='Suma acumulada (CUSUM)')
    ax2.axhline(y=UMBRAL_FIJO, color='r', linestyle='-', label=f'Umbral fijo ({UMBRAL_FIJO})')
    ax2.axhline(y=umbral_estadistico, color='m', linestyle='--', 
               label=f'Umbral estadístico ({umbral_estadistico:.2f})')
    
    # Marcar detecciones
    if deteccion_umbral_fijo is not None:
        ax2.axvline(x=tiempo_num[deteccion_umbral_fijo], color='r', linestyle=':',
                   label=f'Detección umbral fijo')
    
    if deteccion_umbral_estadistico is not None:
        ax2.axvline(x=tiempo_num[deteccion_umbral_estadistico], color='m', linestyle=':',
                   label=f'Detección umbral estadístico')
    
    ax2.set_title('Detección de Anomalías con Método de Suma Acumulada')
    ax2.set_xlabel('Tiempo')
    ax2.set_ylabel('Valor acumulado')
    ax2.xaxis.set_major_formatter(formatter)
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    
    # Mostrar resultados de detección
    print("Información de la simulación:")
    print(f"- Inicio del ataque real: {etiquetas_tiempo[inicio_ataque].strftime('%H:%M:%S.%f')[:-3]}")
    
    if deteccion_umbral_fijo is not None:
        tiempo_deteccion = etiquetas_tiempo[deteccion_umbral_fijo].strftime('%H:%M:%S.%f')[:-3]
        retraso = (deteccion_umbral_fijo - inicio_ataque) / MUESTRAS_POR_SEGUNDO
        print(f"- Detección con umbral fijo: {tiempo_deteccion} (retraso: {retraso:.3f} segundos)")
    else:
        print("- No se detectó anomalía con umbral fijo")
        
    if deteccion_umbral_estadistico is not None:
        tiempo_deteccion = etiquetas_tiempo[deteccion_umbral_estadistico].strftime('%H:%M:%S.%f')[:-3]
        retraso = (deteccion_umbral_estadistico - inicio_ataque) / MUESTRAS_POR_SEGUNDO
        print(f"- Detección con umbral estadístico: {tiempo_deteccion} (retraso: {retraso:.3f} segundos)")
    else:
        print("- No se detectó anomalía con umbral estadístico")
        
    plt.show()
    
    # Explicación matemática
    print("\nExplicación matemática de la detección con suma acumulada (CUSUM):")
    print("1. La suma acumulada se calcula como:")
    print("   S_t = S_(t-1) + (X_t - μ)")
    print("   Donde:")
    print("   - S_t es la suma acumulada en el tiempo t")
    print("   - X_t es el valor del tráfico en el tiempo t")
    print("   - μ es la media de referencia del tráfico normal")
    print("2. Una anomalía se detecta cuando S_t supera un umbral predefinido.")
    print("3. El método es efectivo porque pequeñas desviaciones persistentes se")
    print("   acumulan con el tiempo, mientras que el ruido aleatorio tiende a cancelarse.")

if __name__ == "__main__":
    main() 