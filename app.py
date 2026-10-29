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
st.wr
