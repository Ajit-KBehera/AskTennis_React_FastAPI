import streamlit as st
from ui.charts.serve_tab.combined_serve_charts import create_combined_serve_charts

def render_serve_tab(df_matches, filters):
    player = filters['player'] if filters['player'] != 'All Players' else None
    opponent = filters['opponent'] if filters['opponent'] != 'All Opponents' else None
    tournament = filters['tournament'] if filters['tournament'] != 'All Tournaments' else None
    surfaces = filters['surfaces'] if filters['surfaces'] else None
    year = filters.get('year')
    if year == 'All Years' or year is None:
        year = None

    if player:
        try:
            timeline_fig, ace_df_timeline_fig, bp_timeline_fig, radar_fig = create_combined_serve_charts(
                player_name=player,
                df=df_matches,
                year=year,
                opponent=opponent,
                tournament=tournament,
                surfaces=surfaces
            )

            plotly_config = {'displayModeBar': True, 'width': 'stretch'}

            st.plotly_chart(timeline_fig, config=plotly_config)
            st.plotly_chart(ace_df_timeline_fig, config=plotly_config)
            st.plotly_chart(bp_timeline_fig, config=plotly_config)
            st.plotly_chart(radar_fig, config=plotly_config)

        except Exception as e:
            st.error(f"Error generating serve charts: {e}")
            st.info("Please ensure the player name matches exactly and has matches in the selected filters.")
    else:
        st.info("ℹ️ Please select a player to view serve statistics.")
