import streamlit as st

def render_matches_tab(df_matches):
    display_columns = ['event_year', 'tourney_date', 'tourney_name',
                      'round', 'winner_name', 'loser_name', 'surface', 'score']

    st.dataframe(df_matches[display_columns], width='stretch')
    if st.button("🗑️ Clear Results", key="clear_matches"):
        st.session_state.analysis_generated = False
        st.session_state.analysis_context = {}
        st.rerun()
