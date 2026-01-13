"""Results panel component for displaying query results and analysis."""

import streamlit as st
from utils.df_utils import add_player_match_columns
import pandas as pd
from .ai_results_helpers import (
    parse_raw_data_to_dataframe,
    render_conversation_flow,
    render_data_results,
    render_plots_from_results,
    render_sql_queries,
)
from .tabs.matches_tab import render_matches_tab
from .tabs.rankings_tab import render_ranking_tab
from .tabs.raw_tab import render_raw_tab
from .tabs.return_tab import render_return_tab
from .tabs.serve_tab import render_serve_tab

def render_results_panel(query_processor, agent_graph, db_service):
    """
    Render the main results panel based on current session state.

    Args:
        query_processor: Query processor instance for AI queries
        agent_graph: Agent graph instance for processing queries
        db_service: Database service instance for data retrieval
    """
    if (st.session_state.get('show_ai_results', False) and
            st.session_state.get('ai_query')):
        render_ai_query_results(query_processor, agent_graph)

    elif st.session_state.get('analysis_generated', False):
        filters = st.session_state.analysis_filters

        df_matches = db_service.get_matches_with_filters(
            player=filters['player'],
            opponent=filters['opponent'],
            tournament=filters['tournament'],
            year=filters['year'],
            surfaces=filters['surfaces'],
            return_all_columns=True,
            _cache_bust=st.session_state.get('cache_bust', 0)
        )

        if df_matches.empty:
            st.warning("No matches found for the selected criteria.")
            return

        player = filters['player']
        if player and player != 'All Players':
            df_matches = add_player_match_columns(df_matches, player)

        tabs = create_analysis_tabs()
        tab_matches, tab_serve, tab_return, tab_ranking, tab_raw = tabs

        with tab_matches:
            render_matches_tab(df_matches)

        with tab_serve:
            render_serve_tab(df_matches, filters)

        with tab_return:
            render_return_tab(df_matches, filters)

        with tab_ranking:
            render_ranking_tab(db_service, filters)

        with tab_raw:
            render_raw_tab(df_matches, filters)

def render_ai_query_results(query_processor, agent_graph):
    """
    Render AI query results including conversation flow, SQL queries, and data.

    Args:
        query_processor: Query processor instance for handling queries
        agent_graph: Agent graph instance for processing queries
    """
    try:
        with st.spinner("AI is analyzing your question..."):
            query_processor.handle_user_query(
                st.session_state.ai_query,
                agent_graph
            )

        conversation_messages = st.session_state.get('ai_conversation_messages',[])
        sql_queries = st.session_state.get('ai_query_sql', [])
        raw_data = st.session_state.get('ai_data_list', [])
        response = st.session_state.get('ai_query_response')

        # Parse raw data into DataFrame using helper function
        data_list_df = parse_raw_data_to_dataframe(raw_data)
        
        # Display conversation flow in an expander
        render_conversation_flow(conversation_messages)

        # Display SQL queries in an expander
        render_sql_queries(sql_queries)

        # Display results as dataframe if available
        render_data_results(data_list_df)

        # Create plots based on this df
        render_plots_from_results(data_list_df)

        if response:
            # Display the final response
            st.markdown("### Answer")
            st.markdown(response)
        else:
            st.warning(
                "I processed your request but couldn't generate a clear "
                "response. Please check the conversation flow above for "
                "details."
            )
            st.info(
                "💡 **Tip**: If you didn't find what you're looking for, "
                "try checking the spelling of player or tournament names. "
                "The system is case-sensitive and requires exact matches."
            )

    except Exception as e:
        st.error(f"Error processing query: {e}")

def create_analysis_tabs():
    """
    Create and return Streamlit tabs for different analysis views.

    Returns:
        tuple: Five tab objects for Matches, Serve, Return, Ranking, and RAW
    """
    return st.tabs([
        "📊 Matches",
        "🎾 Serve",
        "🏓 Return",
        "📈 Ranking",
        "📋 RAW"
    ])
