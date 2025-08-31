# Network Traffic Anomaly Detector using CUSUM Algorithm

## 🌐 Project Overview

This project implements a real-time network traffic anomaly detection system using the CUSUM (Cumulative Sum) algorithm. The system simulates network traffic, introduces random attacks (DoS/DDoS), and detects these anomalies through visual and auditory alerts. It features an interactive graphical interface built with Python, making it an excellent educational tool for understanding cybersecurity concepts and mathematical algorithms applied to network security.

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![Matplotlib](https://img.shields.io/badge/matplotlib-latest-green.svg)
![NumPy](https://img.shields.io/badge/numpy-latest-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Asassintin/Detector-de-anomalias.git
cd Detector-de-anomalias

# Install dependencies
pip install numpy matplotlib

# Run the application (GUI version)
python "detector_anomalias v2.py"

# OR run static version (headless compatible)
cd "Detector de anomalias Versiones"
python "deteccion_anomalias Estatico.py"
```

## 🎯 Key Features

- **Real-time Anomaly Detection**: Uses CUSUM algorithm for statistical anomaly detection
- **Interactive GUI**: Beautiful Tkinter-based interface with real-time visualizations
- **Dual Threshold Detection**: Implements both fixed and adaptive statistical thresholds
- **Attack Simulation**: Simulates DoS/DDoS attacks with configurable parameters
- **Visual Alerts**: Real-time graphs showing traffic patterns and anomaly detection
- **Audio Notifications**: Sound alerts when anomalies are detected (Windows)
- **Mathematical Explanation**: Built-in educational content explaining the CUSUM algorithm
- **Multiple Versions**: Different implementations for learning and comparison

## 📊 Mathematical Foundation

### CUSUM Algorithm

The Cumulative Sum (CUSUM) algorithm is a statistical method for detecting abrupt changes in time series data. In network security context, it helps identify traffic deviations that may indicate attacks.

**Mathematical Formula:**
```
S₀ = 0
Sₜ = max(0, Sₜ₋₁ + (xₜ - μ))
```

Where:
- `Sₜ`: Cumulative sum at time t
- `xₜ`: Traffic value at time t
- `μ`: Baseline (normal traffic mean)
- `max(0,·)`: Prevents negative accumulation

### Threshold Detection

The system uses two detection methods:

1. **Fixed Threshold**: `Sₜ > h` (where h = 2000)
2. **Statistical Threshold**: `Sₜ > μw + k·σw` (where k = 2.5)

## 📁 Repository Structure

### 🐍 Python Implementation Files

- **`detector_anomalias v2.py`** - Main application with GUI and real-time detection
- **`Detector de anomalias Versiones/`** - Directory containing different versions:
  - `detector_anomalias v2 -corregido.py` - Corrected version 2
  - `detector_anomalias v3 - copia.py` - Version 3 with enhanced features
  - `deteccion_anomalias Estatico.py` - Static analysis version without GUI

### 📚 Documentation Files

- **`documento_tecnico_detector_anomalias.md`** - Complete technical documentation (Spanish)
- **`codigo_comentado_detector_anomalias.md`** - Detailed code documentation with comments
- **`Proyecto Detección de Anomalías en Tráfico de Red.md`** - Project description and mathematical foundations
- **`Explicacion Codigo.txt`** - Code explanation and architecture overview

### 🎥 Media Files

- **`Demo Detector de Anomalias.mp4`** - Video demonstration of the application
- **`Documento Técnico Detector de Anomalías en Tráfico de Red.pdf`** - PDF version of technical documentation
- **`Proyecto Mates.docx`** - Mathematical project documentation

## 🚀 Installation and Setup

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Required Dependencies

```bash
pip install numpy matplotlib
```

### System Requirements

**For GUI Version (`detector_anomalias v2.py`):**
- `tkinter` - GUI interface (included with most Python installations)
- `winsound` - Audio alerts (Windows only, optional)
- Display environment (not suitable for headless servers)

**For Static Analysis Version (`deteccion_anomalias Estatico.py`):**
- Works in headless environments
- No GUI dependencies required
- Suitable for server environments and batch processing

### Additional Dependencies (Built-in)
- `random` - For attack simulation
- `datetime` - For timestamp formatting

## 🎮 Usage Instructions

### Running the Main Application (GUI Version)

```bash
python "detector_anomalias v2.py"
```

**Note**: Requires a display environment (desktop/GUI). Not suitable for headless servers.

### Running the Static Analysis Version

```bash
cd "Detector de anomalias Versiones"
python "deteccion_anomalias Estatico.py"
```

**Features**: Works in any environment, generates static plots, suitable for batch analysis.

### Alternative Versions

```bash
# Enhanced version with themes
python "Detector de anomalias Versiones/detector_anomalias v3 - copia.py"

# Corrected version 2
python "Detector de anomalias Versiones/detector_anomalias v2 -corregido.py"
```

### Application Interface

1. **Splash Screen**: Professional loading animation
2. **Main Interface**: 
   - Real-time traffic visualization
   - Cumulative sum graph with thresholds
   - Control buttons (Start/Restart simulation)
   - Information displays
3. **Mathematical Explanation**: Click "?" button for CUSUM theory

### Interface Controls

- **Start/Restart**: Begin or reset the simulation
- **Theme Toggle**: Switch between light and dark themes (v3)
- **Speed Control**: Adjust simulation speed (v3)
- **Help**: Access mathematical explanations

## 🔧 System Architecture

### Core Classes

1. **`DetectorAnomalias`**: 
   - Implements CUSUM algorithm
   - Generates simulated traffic data
   - Manages threshold calculations
   - Handles anomaly detection logic

2. **`AplicacionTiempoReal`**: 
   - Manages GUI interface
   - Handles real-time visualization
   - Controls animation and updates
   - Manages user interactions

3. **`ExplicacionMatematica`**: 
   - Provides educational content
   - Explains CUSUM algorithm
   - Interactive help system

4. **`PantallaCarga`**: 
   - Professional loading screen
   - Smooth animations

### Data Flow

```
Traffic Generation → CUSUM Calculation → Threshold Comparison → Anomaly Detection → Visual/Audio Alerts
```

## 📈 Algorithm Parameters

### Traffic Simulation
- **Normal Traffic Mean**: 100 packets/second
- **Normal Traffic Std Dev**: 15 packets/second
- **Attack Multiplier**: 3x normal traffic
- **Attack Duration**: 0.5 seconds
- **Simulation Window**: 60 seconds
- **Sampling Rate**: 60 samples/second

### Detection Thresholds
- **Fixed Threshold**: 2000
- **Statistical Threshold**: μ + 2.5σ (adaptive)
- **Window Size**: 5 seconds for statistical calculations

## 🛡️ Security Applications

This system demonstrates detection of:

- **DoS (Denial of Service)** attacks
- **DDoS (Distributed Denial of Service)** attacks
- **Network flooding** attacks
- **Traffic anomalies** and unusual patterns

## 📊 Visualization Features

### Real-time Graphs
1. **Traffic Volume Graph**: Shows network traffic over time
2. **Cumulative Sum Graph**: Displays CUSUM values and thresholds
3. **Anomaly Highlighting**: Visual markers for detected attacks
4. **Threshold Lines**: Both fixed and adaptive thresholds

### Alert System
- **Visual Alerts**: Color changes and highlighting
- **Audio Alerts**: Sound notifications (Windows)
- **Information Display**: Attack timing and response metrics

## 🎓 Educational Value

This project serves as an excellent educational tool for:

- **Cybersecurity**: Understanding attack detection methods
- **Mathematics**: Practical application of statistical algorithms
- **Programming**: GUI development and real-time data processing
- **Data Analysis**: Time series analysis and anomaly detection

## 📖 Documentation Languages

- **Spanish**: Original documentation (comprehensive technical details)
- **English**: This README and code comments
- **Mathematical Notation**: Universal mathematical expressions

## 🔍 Version Differences

### Version 2 (`detector_anomalias v2.py`)
- Basic GUI implementation
- Real-time detection
- Fixed and statistical thresholds
- Audio alerts

### Version 2 Corrected (`detector_anomalias v2 -corregido.py`)
- Bug fixes and improvements
- Enhanced visualization
- Better error handling

### Version 3 (`detector_anomalias v3 - copia.py`)
- Dark/light theme support
- Speed controls
- Enhanced UI design
- Additional configuration options

### Static Version (`deteccion_anomalias Estatico.py`)
- Non-interactive analysis
- Batch processing capability
- Static visualizations and plots
- Educational demonstrations
- **Headless environment compatible**
- Generates matplotlib figures
- Timestamp-based analysis

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 📝 License

This project is available for educational and research purposes. Please refer to the original authors for commercial use permissions.

## 🏆 Project Context

This project was developed as part of a mathematical and cybersecurity study, demonstrating the practical application of integral calculus concepts (cumulative sums) in network security. It showcases how mathematical algorithms can be applied to real-world cybersecurity challenges.

## 🔧 Troubleshooting

### Common Issues

**"No module named 'tkinter'"**
- Solution: Install tkinter or use the static version
- Alternative: `sudo apt-get install python3-tk` (Linux)
- Use static version for headless environments

**"No module named 'winsound'"**
- Normal on non-Windows systems
- Audio alerts will be disabled automatically
- Does not affect core functionality

**GUI not displaying**
- Ensure you have a display environment
- Try the static version: `deteccion_anomalias Estatico.py`
- For servers, use headless plotting with matplotlib

### Performance Tuning

**Detector not finding anomalies:**
- Adjust `umbral_fijo` parameter (default: 2000)
- Lower values = more sensitive detection
- Higher values = fewer false positives

**Simulation too fast/slow:**
- Modify `muestras_por_segundo` parameter
- Adjust `ventana_tiempo` for simulation duration

## 🧪 Testing

The core detection algorithm has been validated:
- ✅ CUSUM calculation accuracy
- ✅ Anomaly detection with configurable thresholds  
- ✅ Attack simulation with realistic parameters
- ✅ Response time measurement (typically < 0.5 seconds)
- ✅ Cross-platform compatibility (Windows/Linux/Mac)

## 📞 Support

For questions or support:
- Review the technical documentation in `documento_tecnico_detector_anomalias.md`
- Check code comments in `codigo_comentado_detector_anomalias.md`
- Watch the demonstration video `Demo Detector de Anomalias.mp4`

---

*This project demonstrates the intersection of mathematics, programming, and cybersecurity through practical implementation of anomaly detection algorithms.*