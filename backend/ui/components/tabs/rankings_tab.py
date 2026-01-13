import streamlit as st
from ui.charts.rankings_tab.ranking_timeline_chart import create_ranking_timeline_chart
from ui.charts.serve_tab.serve_stats import build_year_suffix

def render_ranking_tab(db_service, filters):
    player = filters.get('player')
    opponent = filters.get('opponent')
    tournament = filters.get('tournament')
    surfaces = filters.get('surfaces', [])

    available_surfaces = db_service.get_surfaces_for_player(player) if player else ["Hard", "Clay", "Grass", "Carpet"]

    conditions_met = (
        player and
        player != db_service.ALL_PLAYERS and
        opponent == db_service.ALL_OPPONENTS and
        tournament == db_service.ALL_TOURNAMENTS and
        set(surfaces) == set(available_surfaces)
    )

    if conditions_met:
        try:
            year = filters.get('year')

            ranking_df = db_service.get_player_ranking_timeline(player, year=year)

            if ranking_df.empty:
                st.warning(f"No ranking data found for {player}.")
                st.info("Ranking timeline chart not available.")
            else:
                year_suffix = build_year_suffix(year)
                title = f"{player} - Ranking Timeline - {year_suffix}"

                ranking_fig = create_ranking_timeline_chart(player, ranking_df, title=title)

                if ranking_fig:
                    plotly_config = {'displayModeBar': True, 'width': 'stretch'}
                    st.plotly_chart(ranking_fig, config=plotly_config)
                else:
                    st.info("Ranking timeline chart not available.")

        except Exception as e:
            st.error(f"Error generating ranking timeline chart: {e}")
            st.info("Ranking timeline chart not available.")
    else:
        st.info("Ranking timeline chart not available.")
        reasons = []
        if not player or player == db_service.ALL_PLAYERS:
            reasons.append("Please select exactly 1 player")
        if opponent != db_service.ALL_OPPONENTS:
            reasons.append("Opponent must be 'All Opponents'")
        if tournament != db_service.ALL_TOURNAMENTS:
            reasons.append("Tournament must be 'All Tournaments'")
        if set(surfaces) != set(available_surfaces):
            reasons.append(f"All available surfaces must be selected ({', '.join(available_surfaces)})")

        if reasons:
            st.caption("Requirements: " + " | ".join(reasons))
