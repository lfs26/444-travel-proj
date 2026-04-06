import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🧳 My Bookings")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            b.booking_id,
            co.name AS origin,
            cd.name AS destination,
            b.travel_date,
            b.budget,
            b.travel_style,
            b.created_at
        FROM bookings b
        JOIN countries co ON co.country_id = b.origin_country_id
        JOIN countries cd ON cd.country_id = b.destination_country_id
        ORDER BY b.created_at DESC;
    """)

    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame([
            {
                "Booking ID": r[0],
                "Origin": r[1],
                "Destination": r[2],
                "Travel Date": r[3],
                "Budget (USD)": float(r[4]) if r[4] is not None else None,
                "Style": r[5],
                "Created": r[6].strftime("%Y-%m-%d %H:%M"),
            }
            for r in rows
        ])

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("🗑 Delete a Booking")

        booking_ids = df["Booking ID"].tolist()
        selected = st.selectbox("Select a booking to delete", booking_ids)

        if st.button("Delete Booking"):
            cur.execute("DELETE FROM bookings WHERE booking_id = %s;", (selected,))
            conn.commit()
            st.success("Booking deleted. Refresh the page to see updates.")
    else:
        st.info("No bookings yet. Go to **Book a Trip** to create one.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database error: {e}")
