import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("✈️ Book a Trip")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT country_id, name FROM countries ORDER BY name;")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["country_id", "name"])

    if df.empty:
        st.warning("No countries found in the database.")
    else:
        names = df["name"].tolist()

        origin = st.selectbox("Origin Country", names)
        dest = st.selectbox("Destination Country", names)

        if origin == dest:
            st.warning("Origin and destination must be different.")
        else:
            travel_date = st.date_input("Travel Date")
            budget = st.number_input("Budget (USD)", min_value=0.0)
            style = st.selectbox("Travel Style", ["Budget", "Standard", "Luxury"])

            if st.button("Save Booking"):
                origin_id = int(df.loc[df["name"] == origin, "country_id"].iloc[0])
                dest_id = int(df.loc[df["name"] == dest, "country_id"].iloc[0])

                cur.execute("""
                INSERT INTO bookings (origin_country_id, destination_country_id, travel_date, budget, travel_style)
                VALUES (%s, %s, %s, %s, %s);
            """, (origin_id, dest_id, travel_date, budget, style))

            conn.commit()
            st.success("Booking saved!")


    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database error: {e}")
