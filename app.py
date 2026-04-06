import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Travel Booking App", page_icon="🌍", layout="wide")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🌍 Travel Booking App")
st.write("Welcome! Use the sidebar to navigate between pages.")

st.markdown("---")
st.subheader("📊 Current Data Overview")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM countries;")
    country_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM visa_info;")
    visa_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM flight_prices;")
    flight_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings;")
    booking_count = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries", country_count)
    col2.metric("Visa Records", visa_count)
    col3.metric("Flight Price Entries", flight_count)
    col4.metric("Bookings", booking_count)

    st.markdown("---")
    st.subheader("📋 Recent Bookings")

    cur.execute("""
        SELECT 
            co.name AS origin,
            cd.name AS destination,
            b.travel_date,
            b.budget,
            b.travel_style,
            b.created_at
        FROM bookings b
        JOIN countries co ON co.country_id = b.origin_country_id
        JOIN countries cd ON cd.country_id = b.destination_country_id
        ORDER BY b.created_at DESC
        LIMIT 20;
    """)

    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame([
            {
                "Origin": r[0],
                "Destination": r[1],
                "Travel Date": r[2],
                "Budget (USD)": float(r[3]) if r[3] is not None else None,
                "Style": r[4],
                "Created": r[5].strftime("%Y-%m-%d %H:%M"),
            }
            for r in rows
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bookings yet. Go to **Book a Trip** to create one.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
