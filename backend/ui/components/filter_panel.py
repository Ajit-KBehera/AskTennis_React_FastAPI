import streamlit as st

def render_filter_panel(db_service):
    st.markdown("Analyze Tennis data:")

    if 'analysis_filters' not in st.session_state:
        st.session_state.analysis_filters = {
            'player': None,
            'opponent': None,
            'tournament': None,
            'year': None,
            'surfaces': []
        }

    all_players = db_service.get_all_players()
    selected_player = st.selectbox(
        "Search Player:",
        all_players,
        key="player_select",
        help="Type to search players (e.g., Federer, Nadal)"
    )

    if selected_player and selected_player != "All Players":
        opponent_options = db_service.get_opponents_for_player(selected_player)
    else:
        opponent_options = all_players

    selected_opponent = st.selectbox(
        "Search Opponent:",
        opponent_options,
        key="opponent_select",
        help="Type to search opponents"
    )

    tournament_options = db_service.get_all_tournaments(selected_player)
    selected_tournament = st.selectbox(
        "Search Tournament:",
        tournament_options,
        key="tournament_select",
        help="Type to search tournaments (e.g., Wimbledon, French Open)"
    )

    if selected_player and selected_player != "All Players":
        min_year, max_year = db_service.get_player_year_range(selected_player)
    else:
        min_year, max_year = (1968, 2024)

    player_changed = (
        'previous_player' not in st.session_state or
        st.session_state.previous_player != selected_player
    )
    year_range_missing = 'year_range' not in st.session_state

    year_range_invalid = False
    if not year_range_missing:
        current_min, current_max = st.session_state.year_range
        year_range_invalid = (
            current_min < min_year or
            current_max > max_year or
            current_min > current_max
        )

    if player_changed or year_range_missing or year_range_invalid:
        st.session_state.year_range = (min_year, max_year)
        st.session_state.previous_player = selected_player

    use_all_years = st.checkbox(
        "All Years",
        value=False,
        key="year_all_years_checkbox",
        help=f"Select all available years ({min_year}-{max_year})"
    )

    if use_all_years:
        selected_year = None
        st.info(f"Year Range: {min_year} - {max_year} (All Years)")
    elif min_year == max_year:
        selected_year = min_year
        st.info(f"Only one year available: {min_year}")
        st.session_state.year_range = (min_year, max_year)
    else:
        year_range = st.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=st.session_state.year_range,
            key="year_range_slider",
            help=f"Drag handles to select start and end year. Drag both to same position for single year. Range: {min_year}-{max_year}"
        )
        st.session_state.year_range = year_range

        if year_range[0] == year_range[1]:
            selected_year = year_range[0]
        else:
            selected_year = (year_range[0], year_range[1])

        if year_range[0] == year_range[1]:
            st.caption(f"Selected: {year_range[0]}")
        else:
            st.caption(f"Selected: {year_range[0]} - {year_range[1]} ({year_range[1] - year_range[0] + 1} years)")

    surface_options = db_service.get_surfaces_for_player(selected_player)
    selected_surfaces = st.multiselect(
        "Select Surfaces:",
        surface_options,
        default=surface_options,
        key="surface_multiselect",
        help="Select one or more surfaces to filter matches"
    )

    st.markdown("---")
    col_generate, col_clear_cache = st.columns([2, 1])

    with col_generate:
        generate_button = st.button(
            "🔍 Generate",
            type="primary",
            key="filter_generate_button"
        )

    with col_clear_cache:
        if st.button("🗑️", help="Clear cached data if results seem stale", key="filter_clear_cache_button"):
            db_service.clear_cache()
            st.success("Cache cleared!")
            st.rerun()

    if generate_button:
        st.session_state.analysis_filters = {
            'player': selected_player,
            'opponent': selected_opponent,
            'tournament': selected_tournament,
            'year': selected_year,
            'surfaces': selected_surfaces
        }
        st.session_state.analysis_generated = True
        st.session_state.show_ai_results = False
        st.session_state.cache_bust = st.session_state.get('cache_bust', 0) + 1
        return True

    return False
