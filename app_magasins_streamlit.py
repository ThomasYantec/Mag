
import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from streamlit_folium import st_folium

st.set_page_config(page_title="Carte des magasins", layout="wide")
st.title("🗺️ Carte interactive des magasins (géocodage automatique)")

@st.cache_data
def load_data():
    df = pd.read_excel("Clients CA.xlsx", skiprows=6, engine="openpyxl")
    df = df.dropna(subset=[df.columns[2]])  # colonne nom magasin
    df = df.rename(columns={df.columns[1]: "Département", df.columns[2]: "Nom Magasin"})
    return df[["Nom Magasin", "Département"]]

@st.cache_data(show_spinner="📍 Géocodage en cours...")
def geocode_data(df):
    geolocator = Nominatim(user_agent="magasins_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    latitudes = []
    longitudes = []

    for nom in df["Nom Magasin"]:
        location = geocode(nom + ", France")
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    return df.dropna(subset=["Latitude", "Longitude"])

df = load_data()

departements = sorted(df["Département"].dropna().unique())
selection = st.selectbox("📍 Choisis un département :", ["Tous"] + list(departements))

if selection != "Tous":
    df = df[df["Département"] == selection]

df_geo = geocode_data(df)

m = folium.Map(location=[48.5, 3.5], zoom_start=6)
for _, row in df_geo.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=row["Nom Magasin"],
        icon=folium.Icon(color="green", icon="shopping-cart", prefix="fa"),
    ).add_to(m)

st_folium(m, width=1000, height=600)
