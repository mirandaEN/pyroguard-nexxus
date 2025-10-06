# 🔥 PyroGuard Nexus - Predictive Fire Management Dashboard

**Submission for the NASA International Space Apps Challenge 2025 by Team Nexxus-Prime.**

---

## 📖 Project Overview & Live Prototype

PyroGuard Nexus is an end-to-end system designed to shift the paradigm of fire management from reactive response to proactive, data-driven prevention. It demonstrates how real-time IoT sensor data can be ingested, analyzed, and visualized to anticipate and mitigate wildfire risks.

This repository contains a **functional prototype** of the system, showcasing the core data pipeline from a physical hardware sensor to a live data visualization dashboard.

### Visual Showcase

<table>
  <tr>
    <td align="center"><b>Live Telemetry Dashboard</b></td>
    <td align="center"><b>Functional Hardware Prototype</b></td>
  </tr>
  <tr>
    <td>
      <img src="[https://i.imgur.com/your-dashboard-image-link.png](https://imgur.com/GAjETks)" alt="Dashboard Screenshot" width="100%">
    </td>
    <td>
      <img src="[https://i.imgur.com/your-hardware-image-link.jpg](https://imgur.com/fNyTJm4)" alt="Hardware Prototype" width="100%">
    </td>
  </tr>
</table>

---

## 🛰️ Core Features

-   **Real-time Data Visualization:** Ingests and displays live telemetry from remote IoT sensor nodes.
-   **Predictive Risk Analysis:** Utilizes environmental data (temperature, humidity, etc.) to calculate a dynamic fire risk score.
-   **Interactive Dashboard:** Built with Python and Streamlit for a user-friendly and interactive command center interface.
-   **Geospatial Mapping:** Plots sensor locations and risk levels on an interactive 3D map for complete situational awareness.
-   **Autonomous Hardware:** The system is designed around low-cost, solar-powered hardware for long-term, maintenance-free deployment.

---

## ⚙️ Tech Stack & Requirements

-   **Backend & Dashboard:** Python 3.9+
-   **Key Libraries:** Streamlit, Pandas, NumPy
-   **Hardware Prototype:** Arduino / ESP32, DHT22 Sensor
-   **A `requirements.txt` file is included for all necessary Python packages.**

---

## 💻 How to Run Locally

Follow these steps to run the dashboard on your local machine.

1.  **Clone the repository:**
    ```bash
    # INSTRUCCIÓN: Reemplaza con la URL real de tu repositorio.
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Install the required libraries:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Run the Streamlit application:**
    ```bash
    streamlit run dashboard.py
    ```

The application will then be available in your web browser, typically at **`http://localhost:8501`**.
