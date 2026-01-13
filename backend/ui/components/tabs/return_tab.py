import streamlit as st
from ui.charts.return_tab.combined_return_charts import create_combined_return_charts

def render_return_tab(df_matches, filters):
    player = filters['player'] if filters['player'] != 'All Players' else None
    opponent = filters['opponent'] if filters['opponent'] != 'All Opponents' else None
    tournament = filters['tournament'] if filters['tournament'] != 'All Tournaments' else None
    surfaces = filters['surfaces'] if filters['surfaces'] else None
    year = filters.get('year')
    if year == 'All Years' or year is None:
        year = None

    if player:
        try:
            return_points_timeline_fig, bp_conversion_timeline_fig, radar_fig = create_combined_return_charts(
                player_name=player,
                df=df_matches,
                year=year,
                opponent=opponent,
                tournament=tournament,
                surfaces=surfaces
            )

            plotly_config = {'displayModeBar': True, 'width': 'stretch'}

            st.plotly_chart(return_points_timeline_fig, config=plotly_config)
            st.plotly_chart(bp_conversion_timeline_fig, config=plotly_config)
            st.plotly_chart(radar_fig, config=plotly_config)

        except Exception as e:
            st.error(f"Error generating return charts: {e}")
            st.info("Please ensure the player name matches exactly and has matches in the selected filters.")
    else:
        st.info("ℹ️ Please select a player to view return statistics.")
