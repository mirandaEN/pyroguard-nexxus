# 🔥 PyroGuard Nexus - Predictive Fire Management Dashboard

This repository contains the source code for the **PyroGuard Nexus** dashboard, a functional prototype developed for the **NASA International Space Apps Challenge 2025**.

The application is an end-to-end system that demonstrates how real-time IoT sensor data can be ingested, analyzed, and visualized to proactively manage and prevent wildfires. It moves beyond traditional, reactive methods by providing a predictive, data-driven approach to fire safety.

## Core Features

-   **Real-time Data Visualization:** Ingests and displays live telemetry from remote IoT sensor nodes.
-   **Predictive Risk Analysis:** Utilizes environmental data (temperature, humidity, etc.) to calculate a dynamic fire risk score.
-   **Interactive Dashboard:** Built with Python and Streamlit for a user-friendly and interactive command center interface.
-   **Geospatial Mapping:** Plots sensor locations and risk levels on an interactive 3D map for complete situational awareness.

## Tech Stack

-   **Frontend/Backend:** Python, Streamlit
-   **Data Manipulation:** Pandas, NumPy
-   **Visualization:** Pydeck
-   **Hardware Prototype:** Arduino, ESP32, DHT22 Sensor

## Running the Project Locally

1.  **Clone the repository:**
    ```bash
    git clone [your-repository-url]
    cd [your-repository-folder]
    ```

2.  **Install the required libraries:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Run the Streamlit application:**
    ```bash
    streamlit run dashboard.py
    ```

The application will then be available in your browser at `http://localhost:8501`.
