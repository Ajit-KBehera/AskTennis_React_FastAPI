import streamlit as st

def render_search_panel(column_layout=None):
    if column_layout is None:
        column_layout = [8.5, 1.5]

    search_container = st.container()
    with search_container:
        col_search, col_buttons = st.columns(column_layout)

        with col_search:
            if st.session_state.get('clear_search_input', False):
                del st.session_state.clear_search_input
                if 'ai_search_input' in st.session_state:
                    del st.session_state.ai_search_input

            ai_query = st.text_input(
                "AskTennis Search:",
                placeholder="Ask any tennis question (e.g., Who won Wimbledon 2022?)",
                key="ai_search_input",
                label_visibility="visible"
            )

        with col_buttons:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns([1, 1])

            with btn_col1:
                send_clicked = st.button("Send", type="primary", key="search_send_button")
                if send_clicked:
                    if ai_query:
                        st.session_state.ai_query = ai_query
                        st.session_state.show_ai_results = True
                        st.session_state.analysis_generated = False
                        st.rerun()

            with btn_col2:
                clear_clicked = st.button("Clear", key="search_clear_button")
                if clear_clicked:
                    st.session_state.ai_query_results = None
                    st.session_state.show_ai_results = False
                    st.session_state.analysis_generated = False
                    st.session_state.clear_search_input = True
                    st.rerun()

    if st.session_state.get('show_ai_results', False) and st.session_state.get('ai_query'):
        return st.session_state.get('ai_query')

    return None
