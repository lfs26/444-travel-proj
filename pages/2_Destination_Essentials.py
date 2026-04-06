import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🌍 Destination Essentials")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM countries ORDER BY name;")
    countries = cur.fetchall()

    df = pd.DataFrame(countries, columns=[
        "country_id", "name", "region", "subregion",
        "currency_code", "currency_name", "language_list", "population"
    ])

    if df.empty:
        st.warning("No countries found in the database.")
    else:
        name = st.selectbox("Select a country", df["name"])
        row = df[df["name"] == name].iloc[0]

        st.subheader(row["name"])
        st.write(f"**Region:** {row['region']} ({row['subregion']})")
        st.write(f"**Currency:** {row['currency_name']} ({row['currency_code']})")
        st.write(f"**Languages:** {row['language_list']}")
        st.write(f"**Population:** {row['population']:,}")

        cur.execute("""
            SELECT visa_required, visa_on_arrival, visa_free_days, notes
            FROM visa_info
            WHERE country_id = %s;
        """, (row["country_id"],))
        visa = cur.fetchone()

        st.markdown("---")
        st.subheader("🛂 Visa Information")

        if visa:
            st.write(f"**Visa Required:** {'Yes' if visa[0] else 'No'}")
            st.write(f"**Visa on Arrival:** {'Yes' if visa[1] else 'No'}")
            if visa[2] is not None:
                st.write(f"**Visa-Free Days:** {visa[2]}")
            if visa[3]:
                st.write(f"**Notes:** {visa[3]}")
        else:
            st.info("No visa information available for this country.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database error: {e}")
