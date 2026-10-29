import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Delivery Parking Finder", page_icon="🅿️")


@st.cache_data
def load_data():
    return pd.read_csv("bedford_parking.csv")


@st.cache_data(ttl=86400)
def geocode(place):
    try:
        geolocator = Nominatim(user_agent="delivery-parking-finder-learning-project", timeout=10)
        loc = geolocator.geocode(place + ", Bedford, UK")
        return (loc.latitude, loc.longitude) if loc else None
    except Exception:
        return None


def nearest(df, lat0, lon0, n, free_only):
    d = df.copy()
    R = 6371000
    p1, p2 = np.radians(lat0), np.radians(d["lat"])
    dphi = p2 - p1
    dlam = np.radians(d["lon"] - lon0)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlam / 2) ** 2
    d["distance_m"] = (2 * R * np.arcsin(np.sqrt(a))).round()
    d["walk_min"] = (d["distance_m"] / 80).round(1)
    if free_only:
        d = d[d["fee"] == "no"]
    return d.sort_values("distance_m").head(n)


st.title("🅿️ Delivery Parking Finder")
st.write("Find parking near a pickup point in Bedford.")

df = load_data()

place = st.text_input("Restaurant or street", "Bedford railway station")
n = st.slider("How many results", 3, 20, 8)
free_only = st.checkbox("Show only places marked free")

if st.button("Find parking"):
    centre = geocode(place)
    if centre is None:
        st.session_state["result"] = None
        st.session_state["error"] = "Place not found. Try adding the street name."
    else:
        res = nearest(df, centre[0], centre[1], n, free_only)
        st.session_state["result"] = (place, centre, res)
        st.session_state["error"] = None

if st.session_state.get("error"):
    st.warning(st.session_state["error"])

saved = st.session_state.get("result")
if saved:
    place_name, centre, res = saved
    if res.empty:
        st.info("No matching places. Many places have no fee information in the data.")
    else:
         m = folium.Map(
             location=centre,
             zoom_start=16,
             tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
             attr="© OpenStreetMap contributors © CARTO",
         )
             folium.Marker(centre, popup=place_name, icon=folium.Icon(color="blue")).add_to(m)
             for _, row in res.iterrows():
                    color = "green" if row["fee"] == "no" else "red" if row["fee"] == "yes" else "gray"
                    folium.CircleMarker(
                   location=[row["lat"], row["lon"]], radius=8, color=color, fill=True,
                   popup=f"{row['name']}<br>Fee: {row['fee']}<br>{row['distance_m']} m away",
            ).add_to(m)
st_folium(m, width=700, height=450, returned_objects=[], key="parking_map")
        st.dataframe(res[["name", "fee", "type", "distance_m", "walk_min"]])

st.caption(
    "Green = free, red = paid, gray = unknown. Data from OpenStreetMap contributors. "
    "Always check the signs on the street, because this app can be out of date or wrong."
)
