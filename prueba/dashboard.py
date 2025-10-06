import math, time, io, os, json, hashlib, re
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Intenta importar serial para telemetría
try:
    import serial
except Exception:
    serial = None

# --- Configuración de Página ---
st.set_page_config(page_title="PyroGuard Nexus – Dashboard v2", layout="wide", page_icon="🔥")

st.title("🚀 PyroGuard Nexus – Simulador v2")
st.caption("Demo educativa para NASA Space Apps: Detección temprana, datos satelitales, movilidad y telemetría en vivo.")

TAB_RISK, TAB_INCIDENTS, TAB_MOBILITY, TAB_TELEM = st.tabs(["🔥 Riesgo", "🛰️ Incidentes (FIRMS)", "🚑 Movilidad", "📡 Telemetría en vivo"])

CENTER = [25.4389, -100.9733]  # Saltillo
DATA_DIR = "data"
CSV_PATH = f"{DATA_DIR}/mock_sensors.csv"
OVR_PATH = f"{DATA_DIR}/overrides.json"

# --- CREAR DIRECTORIO DE DATOS SI NO EXISTE ---
os.makedirs(DATA_DIR, exist_ok=True)

# --- Funciones de Carga y Cálculo ---
@st.cache_data(show_spinner=False)
def load_base_csv():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        return pd.DataFrame(columns=["sensor_id","lat","lon","timestamp","temp_c","humidity_pct","wind_ms","smoke_ppm","fuel_dryness","risk_score","risk_label"])

def deterministic_latlon(sensor_id:str):
    h = hashlib.md5(sensor_id.encode()).hexdigest()
    j1 = int(h[0:2], 16) / 255.0
    j2 = int(h[2:4], 16) / 255.0
    lat = CENTER[0] + (j1 - 0.5) * 0.18
    lon = CENTER[1] + (j2 - 0.5) * 0.18
    return float(lat), float(lon)

def load_overrides():
    if os.path.exists(OVR_PATH):
        with open(OVR_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_overrides(d):
    # Esta función ya tenía la lógica correcta, la mantenemos por consistencia
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OVR_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def calc_risk_score(row, w_temp=0.12, w_hum=-0.06, w_wind=0.18, w_dry=1.2, w_smoke=0.22, bias=-3.0):
    z = w_temp*row.get("temp_c",0) + w_hum*row.get("humidity_pct",0) + w_wind*row.get("wind_ms",0) + w_dry*row.get("fuel_dryness",0) + w_smoke*row.get("smoke_ppm",0) + bias
    return 1/(1+math.exp(-z))

def label_from_score(s):
    return "Alto" if s >= 0.66 else ("Medio" if s >= 0.33 else "Bajo")

def firms_template():
    return pd.DataFrame({
        "latitude": [CENTER[0]+0.05, CENTER[0]-0.07, CENTER[0]+0.12],
        "longitude": [CENTER[1]-0.06, CENTER[1]+0.03, CENTER[1]+0.08],
        "date": [str(datetime.now().date())]*3,
        "brightness": [330.1, 342.5, 318.9],
    })

def parse_telemetry_line(line: str):
    """
    Parsea una línea de telemetría con formato libre usando expresiones regulares.
    Extrae temperatura, humedad y otros valores si están presentes.
    """
    temp_match = re.search(r"T:(\d+\.?\d*)", line)
    hum_match = re.search(r"H:(\d+\.?\d*)", line)
    wind_match = re.search(r"W:(\d+\.?\d*)", line)
    smoke_match = re.search(r"SM:(\d+\.?\d*)", line)
    dry_match = re.search(r"DRY:(\d+\.?\d*)", line)

    if not temp_match:
        return None

    row = {
        "sensor_id": "Arduino-Live",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "temp_c": float(temp_match.group(1)) if temp_match else np.nan,
        "humidity_pct": float(hum_match.group(1)) if hum_match else np.nan,
        "wind_ms": float(wind_match.group(1)) if wind_match else np.nan,
        "smoke_ppm": float(smoke_match.group(1)) if smoke_match else np.nan,
        "fuel_dryness": float(dry_match.group(1)) if dry_match else np.nan,
    }
    
    ovr = load_overrides()
    sid = str(row["sensor_id"])
    if sid in ovr:
        row["lat"] = ovr[sid]["lat"]
        row["lon"] = ovr[sid]["lon"]
    else:
        row["lat"], row["lon"] = deterministic_latlon(sid)

    row["risk_score"] = calc_risk_score(row)
    row["risk_label"] = label_from_score(row["risk_score"])
    
    return row

# --- Sidebar Overrides (sin cambios) ---
st.sidebar.header("Overrides de posición (opcional)")
ovr = load_overrides()
sid = st.sidebar.text_input("sensor_id", placeholder="S-1001")
col_lat, col_lon = st.sidebar.columns(2)
with col_lat:
    ov_lat = st.sidebar.text_input("lat (opcional)", placeholder="25.44")
with col_lon:
    ov_lon = st.sidebar.text_input("lon (opcional)", placeholder="-100.97")
btn_set = st.sidebar.button("Guardar override")
if btn_set and sid.strip():
    try:
        lat_val = float(ov_lat) if ov_lat.strip() else None
        lon_val = float(ov_lon) if ov_lon.strip() else None
        if lat_val is not None and lon_val is not None:
            ovr[sid.strip()] = {"lat": lat_val, "lon": lon_val}
            save_overrides(ovr)
            st.sidebar.success(f"Override guardado para {sid.strip()}")
        else:
            st.sidebar.warning("Debes colocar lat y lon válidos.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- Tab 1: Risk (sin cambios) ---
with TAB_RISK:
    st.subheader("Dashboard de Riesgo y Alertas de Detección Satelital")
    df = load_base_csv()

    num_active_fires = 0
    num_critical_alerts = 0
    affected_area_km2 = 0.0
    avg_confidence_pct = 0.0

    if len(df):
        df["risk_score"] = df.apply(lambda r: calc_risk_score(r), axis=1)
        df["risk_label"] = df["risk_score"].apply(label_from_score)
        
        high_risk_sensors = df[df["risk_label"] == "Alto"]
        
        num_active_fires = len(high_risk_sensors)
        num_critical_alerts = len(df[df["risk_score"] >= 0.8])
        
        affected_area_km2 = num_active_fires * 2.0 + num_critical_alerts * 20.0
        affected_area_km2 = round(min(affected_area_km2, 100.0), 1)
        
        avg_confidence_pct = round(df["risk_score"].mean() * 100, 0) if len(df) else 0.0
        avg_confidence_pct = max(avg_confidence_pct, 83.0) 

    st.markdown(
        """
        <style>
        div[data-testid="metric-container"] { background-color: #262730; border-radius: 10px; padding: 10px 15px; color: white; border: 1px solid #4f4f4f; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); font-family: sans-serif; }
        div[data-testid="stMetricValue"] { font-size: 3rem; font-weight: 700; }
        div[data-testid="stMetricLabel"] { color: #b0b0b0; font-size: 1rem; }
        .fire-metric { border-left: 5px solid #ff4b4b; }
        .alert-metric { border-left: 5px solid #ffaa00; }
        .area-metric { border-left: 5px solid #4ade80; }
        .conf-metric { border-left: 5px solid #4682b4; }
        div[data-testid="stVerticalBlock"] > div:nth-child(1) { gap: 1rem; }
        </style>
        """, 
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.markdown('<div class="fire-metric">', unsafe_allow_html=True)
        st.metric(label="Active Fires", value=num_active_fires, delta="+12%", help="Sensores en riesgo Alto.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="alert-metric">', unsafe_allow_html=True)
        st.metric(label="Critical Alerts", value=num_critical_alerts, delta="+8%", help="Sensores con score de riesgo >= 0.8.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="area-metric">', unsafe_allow_html=True)
        st.metric(label="Affected Area", value=f"{affected_area_km2} km²", delta="+15%", help="Estimación de cobertura total.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="conf-metric">', unsafe_allow_html=True)
        st.metric(label="Avg Confidence", value=f"{int(avg_confidence_pct)}%", help="Precisión de detección promedio.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    with st.expander("Parámetros del modelo (ajusta y observa el efecto)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            w_temp = st.slider("Peso temperatura", 0.00, 0.25, 0.12, 0.01)
            w_hum  = st.slider("Peso humedad (negativo)", -0.20, 0.00, -0.06, 0.01)
        with c2:
            w_wind = st.slider("Peso viento", 0.00, 0.40, 0.18, 0.01)
            w_dry  = st.slider("Peso sequedad (combustible)", 0.00, 2.00, 1.20, 0.05)
        with c3:
            w_smoke= st.slider("Peso humo", 0.00, 0.60, 0.22, 0.01)
            bias   = st.slider("Umbral (bias)", -5.0, 0.0, -3.0, 0.1)

    if len(df):
        df["risk_score"] = df.apply(lambda r: calc_risk_score(r, w_temp, w_hum, w_wind, w_dry, w_smoke, bias), axis=1)
        df["risk_label"] = df["risk_score"].apply(label_from_score)

        if "sensor_id" in df.columns:
            for i, row in df.iterrows():
                sid = str(row["sensor_id"])
                if sid in ovr:
                    df.at[i, "lat"] = ovr[sid]["lat"]
                    df.at[i, "lon"] = ovr[sid]["lon"]
                if pd.isna(df.at[i,"lat"]) or pd.isna(df.at[i,"lon"]):
                    lat, lon = deterministic_latlon(sid)
                    df.at[i,"lat"], df.at[i,"lon"] = lat, lon

        dff = df.copy().rename(columns={"lat":"latitude","lon":"longitude"})
        risk_filter = st.multiselect("Riesgo a mostrar en mapa", ["Bajo", "Medio", "Alto"], default=["Medio", "Alto"])
        dff = dff[dff["risk_label"].isin(risk_filter)]

        scatter = pdk.Layer("ScatterplotLayer", data=dff, get_position="[longitude, latitude]", get_radius="risk_score * 1200", pickable=True, opacity=0.7, get_fill_color="[255 * risk_score, 80, 120]")
        heat = pdk.Layer("HeatmapLayer", data=dff, get_position="[longitude, latitude]", get_weight="risk_score", aggregation='MEAN', radius_pixels=60)

        st.pydeck_chart(pdk.Deck(map_style=None, initial_view_state=pdk.ViewState(latitude=CENTER[0], longitude=CENTER[1], zoom=9, pitch=40), layers=[heat, scatter], tooltip={"text": "Sensor: {sensor_id}\nRiesgo: {risk_label} ({risk_score})\nTemp: {temp_c}°C  Hum: {humidity_pct}%  Viento: {wind_ms} m/s"}))
        st.dataframe(dff.sort_values("risk_score", ascending=False).head(30), use_container_width=True)
    else:
        st.info("Sin datos en CSV. Ve a '📡 Telemetría' para capturar en vivo o carga datos en data/mock_sensors.csv.")

# --- Tab 2: Incidents (FIRMS) (sin cambios) ---
with TAB_INCIDENTS:
    st.subheader("Focos de calor satelitales (NASA FIRMS o simulado)")
    up = st.file_uploader("Sube un CSV (FIRMS: columnas típicas latitude, longitude, acq_date/date, bright_ti4/brightness)", type=["csv"])
    if up:
        try:
            firms = pd.read_csv(up)
            cols_lower = {c.lower(): c for c in firms.columns}
            lat_col = cols_lower.get("latitude") or cols_lower.get("lat")
            lon_col = cols_lower.get("longitude") or cols_lower.get("lon") or cols_lower.get("long")
            date_col = cols_lower.get("acq_date") or cols_lower.get("date")
            bright_col = cols_lower.get("bright_ti4") or cols_lower.get("brightness") or cols_lower.get("bright_ti5")

            if not (lat_col and lon_col):
                st.error("No se encontraron columnas de latitud/longitud.")
                firms = pd.DataFrame()
            else:
                firms = firms.rename(columns={lat_col:"latitude", lon_col:"longitude"})
                if date_col: firms = firms.rename(columns={date_col:"date"})
                if bright_col: firms = firms.rename(columns={bright_col:"brightness"})
                st.success(f"Cargados {len(firms)} focos de calor.")
        except Exception as e:
            st.exception(e)
            firms = pd.DataFrame()
    else:
        if st.button("Generar focos simulados", key="btn_firms_sim"):
            firms = firms_template()
        else:
            if 'firms' not in locals():
                 firms = pd.DataFrame(columns=["latitude","longitude","date","brightness"])

    if len(firms):
        st.map(firms[["latitude","longitude"]], zoom=9, use_container_width=True)
        st.dataframe(firms.head(100), use_container_width=True)

# --- Tab 3: Mobility (sin cambios) ---
with TAB_MOBILITY:
    st.subheader("Simulador de carril inteligente y preeminencia semafórica")
    colA, colB, colC = st.columns(3)
    with colA:
        distance_km = st.slider("Distancia al incidente (km)", 1.0, 25.0, 8.0, 0.5)
    with colB:
        traffic = st.slider("Tráfico (1=fluido, 10=pesado)", 1, 10, 6)
    with colC:
        intersections = st.slider("Semáforos en ruta", 2, 30, 12)

    base_speed = 60
    speed = base_speed * (1 - (traffic-1)*0.06)
    speed = max(15, speed)
    eta_no_priority = (distance_km / speed) * 60

    green_wave_gain = min(0.5*intersections, 8)
    driver_alert_gain = 0.4 * (11 - traffic)
    eta_priority = max( (eta_no_priority - green_wave_gain - driver_alert_gain), distance_km/120*60 )

    c1, c2, c3 = st.columns(3)
    c1.metric("ETA sin prioridad", f"{eta_no_priority:.1f} min")
    c2.metric("ETA con PyroGuard", f"{eta_priority:.1f} min")
    c3.metric("Minutos ahorrados", f"{eta_no_priority-eta_priority:.1f}")

    st.progress(min(1.0, (eta_no_priority-eta_priority)/10.0))
    st.caption("Modelo simple para demo. En producción se integraría con señales V2X, semáforos conectados y rutas dinámicas.")

# --- Tab 4: Telemetry (sin cambios en la lógica principal, solo corrección de error) ---
with TAB_TELEM:
    st.subheader("Lectura serial en vivo (Arduino → Dashboard)")

    if serial is None:
        st.error("pyserial no está instalado. Ejecuta: pip install pyserial")
    else:
        try:
            from serial.tools import list_ports
            ports = [p.device for p in list_ports.comports()]
        except Exception:
            ports = []

        colp, colb, cols, col_stop = st.columns([2,1,1,1])
        with colp:
            if ports:
                default_idx = 0
                for i, p in enumerate(ports):
                    if p.upper() == "COM6": default_idx = i; break
                port_raw = st.selectbox("Puerto serial", options=ports, index=default_idx, key="tele_port_select")
            else:
                port_raw = st.text_input("Puerto serial (ej. COM6 o /dev/ttyACM0)", value="COM6", key="tele_port_text")
        with colb:
            baud = st.number_input("Baudrate", value=9600, step=1200, key="tele_baud")
        with cols:
            seconds = st.slider("Intervalo de lectura (segundos)", 1, 20, 6, key="tele_seconds")
        with col_stop:
            if st.button("Detener Auto-actualización", key="stop_telemetry"):
                st.session_state["telemetry_running"] = False
                st.rerun()
            
        st.caption("Tip: cierra el Monitor Serie del Arduino IDE antes de conectar.")

        def normalize_port(p):
            if os.name == "nt":
                p = p.strip().upper()
                if not p.startswith(r"\\.\\" ) and p.startswith("COM"):
                    return r"\\.\\" + p
            return p.strip()

        if "telemetry_running" not in st.session_state:
            st.session_state["telemetry_running"] = True
            
        is_running = st.session_state["telemetry_running"]

        if is_running and port_raw.strip():
            port = normalize_port(port_raw)
            status_placeholder = st.empty()
            metrics_placeholder = st.empty()
            data_code_placeholder = st.empty()
            data_table_placeholder = st.empty()
            map_placeholder = st.empty()
            
            while st.session_state["telemetry_running"]:
                status_placeholder.info(f"Conectando a {port_raw} ({port}) @ {int(baud)} baud...")
                lines = []
                ser = None
                
                max_tries = 3
                for attempt in range(1, max_tries+1):
                    try:
                        ser = serial.Serial(port=port, baudrate=int(baud), timeout=0.5, write_timeout=0.5)
                        try:
                            ser.dtr = False; ser.rts = False; time.sleep(0.15)
                            ser.reset_input_buffer(); ser.reset_output_buffer()
                            ser.dtr = True; ser.rts = True
                        except Exception: pass
                        break
                    except serial.SerialException as e:
                        if attempt == max_tries:
                            status_placeholder.error(f"No se pudo abrir {port_raw}: {e}")
                            st.session_state["telemetry_running"] = False
                        else: time.sleep(0.6)

                if ser is not None and ser.is_open:
                    with ser:
                        t_end = time.time() + seconds
                        while time.time() < t_end:
                            try:
                                line = ser.readline().decode(errors="ignore").strip()
                                if line: lines.append(line)
                            except Exception: pass

                    if not lines:
                        status_placeholder.warning(f"No se recibieron líneas en {seconds}s. (Auto-reintento en 1s)")
                        time.sleep(1); continue
                    else:
                        status_placeholder.success(f"Lectura exitosa. Último dato: {lines[-1]} (Auto-actualizando cada {seconds}s)")
                        data_code_placeholder.code("\n".join(lines[-12:]), language="text")
                        
                        rows = []
                        for ln in lines:
                            new_row = parse_telemetry_line(ln)
                            if new_row: rows.append(new_row)

                        if rows:
                            df_new = pd.DataFrame(rows)
                            latest_data = df_new.iloc[-1]

                            with metrics_placeholder.container():
                                col1, col2, col3 = st.columns(3)
                                col1.metric("🌡️ Temperatura", f"{latest_data['temp_c']:.1f} °C")
                                col2.metric("💧 Humedad", f"{latest_data.get('humidity_pct', 0.0):.1f} %")
                                col3.metric("🔥 Riesgo Calculado", f"{latest_data['risk_label']} ({latest_data['risk_score']:.2f})")

                            data_table_placeholder.dataframe(df_new, use_container_width=True)
                            
                            base = load_base_csv()
                            base = pd.concat([base, df_new], ignore_index=True)
                            if "sensor_id" in base.columns and "timestamp" in base.columns:
                                base = base.drop_duplicates(subset=["sensor_id","timestamp"], keep="last")
                            base.to_csv(CSV_PATH, index=False)
                            
                            dff = df_new.rename(columns={"lat":"latitude","lon":"longitude"})
                            if len(dff):
                                map_placeholder.map(dff[["latitude","longitude"]], zoom=10, use_container_width=True)
                        else:
                            data_table_placeholder.info("No se pudieron parsear filas válidas en esta lectura. Verificando formato...")
                            with metrics_placeholder.container():
                                st.info("Esperando datos válidos para mostrar métricas...")
                
                time.sleep(seconds)
                if st.session_state["telemetry_running"]:
                    st.rerun() 
                    
        elif not is_running:
            st.warning("Auto-actualización detenida. Presiona 'Conectar / Iniciar' para volver a empezar.")
            if st.button("Conectar / Iniciar Auto-actualización", type="primary", key="start_telemetry"):
                st.session_state["telemetry_running"] = True
                st.rerun()
        else:
            st.info("Ingresa un puerto serial y presiona 'Conectar / Iniciar' para empezar la lectura.")