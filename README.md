# 🔥 PyroGuard Nexus: A New Paradigm for Wildfire Prevention

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Framework: Streamlit](https://img.shields.io/badge/Framework-Streamlit-brightgreen.svg)

**Submission for the NASA International Space Apps Challenge 2025 by Team Nexxus-Prime.**

> At PyroGuard Nexus, our mission is to fundamentally change humanity's relationship with fire. We are moving beyond a reactive posture of fighting fires once they become catastrophic, towards a proactive, predictive paradigm where we can anticipate and neutralize threats before they begin. This is not just detection; this is foresight.

---

## The Problem: Fighting Yesterday's War

The escalating threat of wildfires is outpacing our traditional response capabilities. We rely on detection methods that only trigger an alarm when a fire is already established and growing, putting lives, ecosystems, and economies at immense risk. We are always one step behind. PyroGuard Nexus was born from a simple question: **What if we could get there before the smoke does?**

## Our Solution: An Intelligent, Autonomous Shield

PyroGuard Nexus is an integrated, end-to-end ecosystem that acts as a self-sustaining nervous system for our environment. It senses, analyzes, and alerts with unprecedented speed and intelligence.

### How It Works: From Sensor to Insight
Our system creates a complete data-to-decision pipeline:
1.  **SENSE:** A distributed network of autonomous **IoT Sensor Nodes** acts as our eyes and ears on the ground. They continuously monitor critical environmental variables—temperature, humidity, and atmospheric gases—that are precursors to fire.
2.  **ANALYZE:** This real-time data is streamed to our cloud-based **Predictive AI Core**. Here, machine learning algorithms fuse the ground-truth data with meteorological forecasts and **NASA satellite data** (like FIRMS and Landsat) to analyze patterns, calculate risk, and forecast threats with a time horizon of up to 72 hours.
3.  **VISUALIZE:** All this intelligence is delivered to a **Centralized Command Dashboard**. It provides a single source of truth with interactive maps and real-time alerts, empowering decision-makers with the situational awareness needed to act decisively.

### Designed for the Real World: Scalable & Low-Maintenance
We engineered PyroGuard Nexus not just to be innovative, but to be practical for global deployment.
* **Massive Scalability:** The architecture is inherently scalable. Utilizing **LoRaWAN**, a single gateway can support thousands of nodes across hundreds of square kilometers, making it ideal for covering vast, remote territories.
* **Zero Maintenance:** Each sensor node is a self-sufficient unit. Powered by **solar energy** and engineered for ultra-low power consumption via deep-sleep modes, the nodes are designed to operate autonomously for years without human intervention. This "deploy-and-forget" capability makes the system economically viable and operationally efficient.

### The Technology We Use
We believe in using robust, accessible, and powerful tools to solve real-world problems.
* **Hardware:** Our functional prototypes are built on the **Arduino and ESP32** platforms, chosen for their reliability and vast community support.
* **Software:** The dashboard and AI core are built in **Python**, leveraging powerful libraries like **Streamlit** for rapid UI development, **Pandas** for data manipulation, and **Pydeck** for high-performance 3D mapping.

---

## Functional Prototype Showcase

We have built a working, end-to-end prototype that validates our core concept. The images below showcase our physical hardware and the live data dashboard it communicates with.

#### Live Telemetry Dashboard
*Real-time data visualization from our functional prototype.*
![PyroGuard Nexus Dashboard in Action](https://i.imgur.com/tdZqBpW.gif)

---
#### Hardware Prototypes
*Our functional IoT sensor nodes built with Arduino and ESP32 platforms.*
<img src="https://i.imgur.com/fNyTJm4.jpg" alt="Arduino Prototype" width="400"> <img src="https://i.imgur.com/wU13f6W.jpg" alt="ESP32 Prototype" width="400">

---

## Our Vision: A Safer, More Resilient Future

Our goal extends beyond this competition. We aim to develop PyroGuard Nexus into a global standard for proactive environmental protection. We envision a future where communities and ecosystems are shielded by intelligent, autonomous technology, transforming our fight against wildfires from a desperate battle into a managed and predictable science.

---

## How to Run This Prototype Locally

1.  **Clone the repository:**
    ```bash
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
The application will then be available in your web browser at **`http://localhost:8501`**.
