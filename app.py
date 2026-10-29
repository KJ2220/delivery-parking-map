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
        m = folium.Map(location=centre, zoom_start=16, tiles="CartoDB positron")
        folium.Marker(centre, popup=place_name, icon=folium.Icon(color="blue")).add_to(m)
        for _, row in res.iterrows():
            color = "green" if row["fee"] == "no" else "red" if row["fee"] == "yes" else "gray"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]], radius=8, color=color, fill=True,
                popup=f"{row['name']}<br>Fee: {row['fee']}<br>{row['distance_m']} m away",
            ).add_to(m)
        st_folium(m, width=700, height=450, returned_objects=[], key="parking_map")
        st.dataframe(res[["name", "fee", "type", "distance_m", "walk_min"]])
