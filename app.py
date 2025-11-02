# app.py
# Streamlit app: Visualisasi posisi Stasiun Luar Angkasa Internasional (ISS)
# Cara pakai: streamlit run app.py

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime

API_URL = "http://api.open-notify.org/iss-now.json"

@st.cache_data(ttl=10)
def get_iss_position():
    """Mengambil posisi ISS dari API open-notify.
    Mengembalikan dict: {"latitude": float, "longitude": float, "timestamp": int}
    Jika gagal, mengembalikan None.
    """
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        pos = data.get("iss_position", {})
        lat = float(pos.get("latitude"))
        lon = float(pos.get("longitude"))
        ts = int(data.get("timestamp", 0))
        return {"latitude": lat, "longitude": lon, "timestamp": ts}
    except Exception as e:
        st.error(f"Gagal mengambil data ISS: {e}")
        return None

# Layout
st.set_page_config(page_title="ISS Tracker", layout="wide")
st.title("📡 ISS — Posisi Stasiun Luar Angkasa (Real-time)")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### Lokasi saat ini di peta")
    placeholder = st.empty()

with col2:
    st.markdown("##### Info posisi")
    auto_refresh = st.checkbox("Auto-refresh (setiap 10 detik cache)")
    if st.button("Refresh sekarang"):
        # Force re-run by clearing cache for get_iss_position
        get_iss_position.clear()

    info_box = st.empty()

# Ambil data
pos = get_iss_position()

if pos is not None:
    lat = pos["latitude"]
    lon = pos["longitude"]
    ts = pos["timestamp"]
    ts_human = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Tampilkan angka
    with info_box:
        st.write(f"**Latitude:** {lat:.6f}")
        st.write(f"**Longitude:** {lon:.6f}")
        st.write(f"**Timestamp:** {ts} ({ts_human})")

    # Dataframe untuk st.map atau pydeck
    df = pd.DataFrame([{"lat": lat, "lon": lon}])

    # PyDeck map fancy
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=2, pitch=0)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=50000,
        radius_units="meters",
        get_fill_color="[255, 0, 0, 160]",
        pickable=True,
    )
    tooltip = {"html": "<b>ISS</b><br/>Latitude: {lat}<br/>Longitude: {lon}", "style": {"color": "#000000"}}

    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

    with placeholder:
        st.pydeck_chart(r)

    # Additional: tampilkan lokasi dalam format tabel kecil
    st.markdown("---")
    st.markdown("#### Riwayat (sementara dari cache)")
    st.dataframe(df)

else:
    st.warning("Tidak ada data posisi ISS saat ini.")

# Catatan auto-refresh: pengguna bisa menekan tombol Refresh, atau biarkan cache ttl=10 detik untuk pembaruan otomatis
st.caption("Sumber data: open-notify.org — API publik untuk posisi ISS. Tekan 'Refresh sekarang' untuk memperbarui.")
