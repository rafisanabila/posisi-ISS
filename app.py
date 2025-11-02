# app.py
# Streamlit app: Visualisasi posisi Stasiun Luar Angkasa Internasional (ISS)
# Menggunakan API https://api.wheretheiss.at/ untuk data real-time
# Cara jalankan: streamlit run app.py

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime

# ==============================
# KONFIGURASI
# ==============================
API_URL = "https://api.wheretheiss.at/v1/satellites/25544"

st.set_page_config(page_title="ISS Tracker", layout="wide")
st.title("📡 ISS — Posisi Stasiun Luar Angkasa (Real-time)")

# ==============================
# FUNGSI AMBIL DATA ISS
# ==============================
@st.cache_data(ttl=10)
def get_iss_position():
    """Mengambil posisi ISS dari API wheretheiss.at"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        alt = float(data["altitude"])
        vel = float(data["velocity"])
        vis = data["visibility"]
        ts = int(data["timestamp"])
        return {
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "velocity": vel,
            "visibility": vis,
            "timestamp": ts,
        }
    except Exception as e:
        st.error(f"Gagal mengambil data ISS: {e}")
        return None


# ==============================
# TATA LETAK
# ==============================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🌍 Lokasi ISS saat ini di peta")
    map_placeholder = st.empty()

with col2:
    st.markdown("### 📊 Informasi posisi ISS")
    auto_refresh = st.checkbox("Auto-refresh (setiap 10 detik cache)")
    if st.button("Refresh sekarang"):
        get_iss_position.clear()

    info_placeholder = st.empty()


# ==============================
# AMBIL & TAMPILKAN DATA
# ==============================
data = get_iss_position()

if data:
    lat = data["latitude"]
    lon = data["longitude"]
    alt = data["altitude"]
    vel = data["velocity"]
    vis = data["visibility"]
    ts = data["timestamp"]
    ts_human = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")

    with info_placeholder:
        st.write(f"**Latitude:** {lat:.6f}")
        st.write(f"**Longitude:** {lon:.6f}")
        st.write(f"**Altitude:** {alt:.2f} km")
        st.write(f"**Velocity:** {vel:.2f} km/h")
        st.write(f"**Visibility:** {vis}")
        st.write(f"**Timestamp:** {ts_human}")

    df = pd.DataFrame([{"lat": lat, "lon": lon}])

    # Peta menggunakan PyDeck
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=2, pitch=0)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=70000,
        radius_units="meters",
        get_fill_color="[255, 100, 0, 180]",
        pickable=True,
    )

    tooltip = {
        "html": "<b>ISS (International Space Station)</b><br/>Lat: {lat}<br/>Lon: {lon}",
        "style": {"color": "black"},
    }

    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
    with map_placeholder:
        st.pydeck_chart(deck)

    st.markdown("---")
    st.markdown("#### 🧾 Data ringkas")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Latitude": lat,
                    "Longitude": lon,
                    "Altitude (km)": alt,
                    "Velocity (km/h)": vel,
                    "Visibility": vis,
                    "Timestamp (UTC)": ts_human,
                }
            ]
        )
    )

else:
    st.warning("Tidak dapat menampilkan data ISS saat ini.")

# ==============================
# CATATAN
# ==============================
st.caption(
    "Sumber data: [wheretheiss.at](https://wheretheiss.at/) — API publik pelacak ISS. "
    "Gunakan tombol 'Refresh sekarang' atau aktifkan auto-refresh untuk pembaruan otomatis."
)
