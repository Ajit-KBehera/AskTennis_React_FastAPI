import streamlit as st
from .filter_panel import render_filter_panel
from .search_panel import render_search_panel
from .results_panel import render_results_panel

def render_main_content(db_service, query_processor, agent_graph, column_layout=None):
    if column_layout is None:
        column_layout = [1.2, 6.8]

    col_left, col_remaining = st.columns(column_layout)

    with col_left:
        render_filter_panel(db_service)

    with col_remaining:
        render_search_panel()
        render_results_panel(query_processor, agent_graph, db_service)
