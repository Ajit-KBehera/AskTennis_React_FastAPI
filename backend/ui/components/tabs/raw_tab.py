import streamlit as st

def render_raw_tab(df_matches, filters):
    st.dataframe(df_matches, width='stretch')

    csv_data = df_matches.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"tennis_matches.csv",
        mime="text/csv",
        key="download_raw_csv"
    )
