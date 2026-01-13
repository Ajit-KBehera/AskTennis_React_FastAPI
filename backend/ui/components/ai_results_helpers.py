"""Helper functions for rendering AI query results and visualizations."""

import ast
import json

import pandas as pd
import plotly.express as px
import streamlit as st


def render_conversation_flow(conversation_messages):
    """Helper function to render conversation flow in an expander."""
    if conversation_messages:
        with st.expander("💬 Conversational Flow", expanded=False):
            # Exclude the last message (final answer)
            for i, message in enumerate(conversation_messages[:-1]):
                # Determine message type and role
                message_type = type(message).__name__

                if message_type == 'HumanMessage':
                    st.markdown("**👤 Human:**")
                    content = (
                        message.content
                        if isinstance(message.content, str)
                        else str(message.content)
                    )
                    st.markdown(content)
                elif message_type == 'AIMessage':
                    st.markdown("**🤖 AI:**")
                    # Handle different content formats
                    if isinstance(message.content, list):
                        # Gemini format - list of dicts
                        text_content = ""
                        for part in message.content:
                            if isinstance(part, dict):
                                text_content += part.get('text', '')
                            else:
                                text_content += str(part)

                        # If content is empty but has tool calls, show tool call info
                        if not text_content:
                            if hasattr(message, 'tool_calls') and message.tool_calls:
                                tool_names = [
                                    tc.get('name', 'unknown')
                                    for tc in message.tool_calls
                                ]
                                text_content = (
                                    f"🔧 Calling tool(s): {', '.join(tool_names)}"
                                )
                            else:
                                # Empty content with no tool calls - show placeholder
                                text_content = "*[No text content]*"

                        st.markdown(text_content)
                    else:
                        st.markdown(str(message.content))
                elif message_type == 'ToolMessage':
                    st.markdown("**🔧 Tool Response:**")
                    content_str = str(message.content)
                    if len(content_str) > 500:
                        display_content = content_str[:500] + "..."
                    else:
                        display_content = content_str
                    st.code(display_content, language='text')
                else:
                    st.markdown(f"**📝 {message_type}:**")
                    content_str = str(message.content)
                    if len(content_str) > 200:
                        display_content = content_str[:200] + "..."
                    else:
                        display_content = content_str
                    st.markdown(display_content)

                if i < len(conversation_messages) - 2:
                    st.markdown("---")


def render_sql_queries(sql_queries):
    """Helper function to render SQL queries in an expander."""
    if sql_queries:
        with st.expander("📊 SQL Queries Used", expanded=False):
            for i, sql_query in enumerate(sql_queries, 1):
                st.markdown(f"**Query {i}:**")
                st.code(sql_query, language='sql')
                if i < len(sql_queries):
                    st.markdown("---")


def parse_raw_data_to_dataframe(raw_data):
    """
    Parse raw data from AI query results into a pandas DataFrame.
    
    Handles multiple data formats:
    - Already parsed list/dict structures
    - JSON strings
    - Python literal strings (using ast.literal_eval)
    
    Args:
        raw_data: List containing data in various formats (list, dict, or string)
        
    Returns:
        pandas.DataFrame: Parsed data as DataFrame, or empty DataFrame if parsing fails
    """
    if not raw_data:
        return pd.DataFrame()
    
    try:
        # Check if raw_data[0] is an AST Call object or similar AST node
        if hasattr(ast, 'Call') and isinstance(raw_data[0], ast.Call):
            # Skip AST objects - they're not valid data
            return pd.DataFrame()
        
        # If raw_data[0] is already a list/dict, use it directly
        if isinstance(raw_data[0], (list, dict)):
            data_list = raw_data[0]
        elif isinstance(raw_data[0], str):
            # Check if string looks like an object representation (e.g., "<ast.Call object at 0x...>")
            if raw_data[0].strip().startswith('<') and 'object at' in raw_data[0]:
                # This is an object representation, not valid data
                return pd.DataFrame()
            
            # Try JSON first, then fall back to ast.literal_eval for Python literals
            try:
                data_list = json.loads(raw_data[0])
            except json.JSONDecodeError:
                # If JSON parsing fails, try parsing as Python literal
                # This handles cases where the string is a Python list/dict representation
                try:
                    data_list = ast.literal_eval(raw_data[0])
                except (ValueError, SyntaxError):
                    # Silently return empty DataFrame for invalid data
                    return pd.DataFrame()
        else:
            # For other types, try to convert to DataFrame directly
            # but first check if it's a valid data structure
            if not isinstance(raw_data[0], (list, dict, str, int, float, bool)):
                # Unsupported type, return empty DataFrame
                return pd.DataFrame()
            data_list = raw_data[0]

        # Convert to DataFrame
        if data_list is not None:
            return pd.DataFrame(data_list)
        else:
            return pd.DataFrame()
    except json.JSONDecodeError:
        # Silently return empty DataFrame for JSON errors
        return pd.DataFrame()
    except Exception:
        # Silently return empty DataFrame for any other errors
        return pd.DataFrame()


def render_data_results(df):
    """Helper function to render data results in an expander."""
    if not df.empty:
        with st.expander("📋 Data Results", expanded=False):
            st.markdown("### Data")
            st.dataframe(df)


def _infer_column_types(df):
    """Analyze DataFrame and categorize columns by their data characteristics."""
    col_info = {
        'numeric': [],
        'categorical': [],
        'temporal': [],
        'text': []
    }

    for col in df.columns:
        col_lower = col.lower()

        # Check for temporal columns (by name pattern or dtype)
        temporal_keywords = ['year', 'date', 'month', 'time', 'season']
        if any(kw in col_lower for kw in temporal_keywords):
            col_info['temporal'].append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Numeric but check if it's actually a year disguised as int
            if (df[col].dropna().between(1900, 2100).all() and
                    'id' not in col_lower):
                col_info['temporal'].append(col)
            else:
                col_info['numeric'].append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_info['temporal'].append(col)
        elif (df[col].nunique() < 20 and
              df[col].nunique() < len(df) * 0.5):
            # Low cardinality = categorical
            col_info['categorical'].append(col)
        else:
            col_info['text'].append(col)

    return col_info


def _create_smart_chart(df, col_info):
    """Create appropriate chart based on DataFrame structure."""
    charts = []

    numeric_cols = col_info['numeric']
    categorical_cols = col_info['categorical']
    temporal_cols = col_info['temporal']

    # Identify potential label columns (names, players, tournaments, etc.)
    label_candidates = []
    label_keywords = [
        'name', 'player', 'winner', 'loser',
        'tournament', 'tourney', 'surface', 'round'
    ]
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in label_keywords):
            label_candidates.append(col)

    # If no explicit labels found, use first text/categorical column
    if not label_candidates:
        label_candidates = categorical_cols + col_info['text']

    # CASE 1: Time series data (temporal + numeric)
    if temporal_cols and numeric_cols:
        time_col = temporal_cols[0]
        # Sort by time for proper line chart
        df_sorted = df.sort_values(by=time_col)

        # If we have a categorical column, use it for color grouping
        if categorical_cols:
            color_col = categorical_cols[0]
        elif (label_candidates and
              label_candidates[0] != time_col):
            color_col = label_candidates[0]
        else:
            color_col = None

        # Limit to first 3 numeric columns for readability
        for num_col in numeric_cols[:3]:
            if color_col and df[color_col].nunique() <= 10:
                fig = px.line(
                    df_sorted,
                    x=time_col,
                    y=num_col,
                    color=color_col,
                    title=f"{num_col} over {time_col}",
                    markers=True
                )
            else:
                fig = px.line(
                    df_sorted,
                    x=time_col,
                    y=num_col,
                    title=f"{num_col} over {time_col}",
                    markers=True
                )
            fig.update_layout(template="plotly_white")
            charts.append(fig)

    # CASE 2: Categorical comparison (categorical/label + numeric)
    elif label_candidates and numeric_cols:
        label_col = label_candidates[0]

        # Bar chart for categorical comparisons
        if len(df) <= 30:  # Reasonable number of bars
            for num_col in numeric_cols[:2]:
                # Sort by numeric value for better visualization
                df_sorted = df.sort_values(by=num_col, ascending=False)

                fig = px.bar(
                    df_sorted,
                    x=label_col,
                    y=num_col,
                    title=f"{num_col} by {label_col}",
                    color=num_col,
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(
                    template="plotly_white",
                    xaxis_tickangle=-45
                )
                charts.append(fig)

        # If multiple numeric columns, create grouped bar
        if len(numeric_cols) >= 2 and len(df) <= 15:
            df_melted = df.melt(
                id_vars=[label_col],
                value_vars=numeric_cols[:4],
                var_name='Metric',
                value_name='Value'
            )
            fig = px.bar(
                df_melted,
                x=label_col,
                y='Value',
                color='Metric',
                barmode='group',
                title=f"Comparison of Metrics by {label_col}"
            )
            fig.update_layout(
                template="plotly_white",
                xaxis_tickangle=-45
            )
            charts.append(fig)

    # CASE 3: Two numeric columns - scatter plot
    elif len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]

        # Use a label column for hover/color if available
        hover_col = label_candidates[0] if label_candidates else None

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            hover_name=hover_col,
            title=f"{y_col} vs {x_col}",
            trendline="ols" if len(df) > 5 else None
        )
        fig.update_layout(template="plotly_white")
        charts.append(fig)

    # CASE 4: Single numeric column with labels - horizontal bar
    elif len(numeric_cols) == 1 and label_candidates:
        num_col = numeric_cols[0]
        label_col = label_candidates[0]

        if len(df) <= 25:
            df_sorted = df.sort_values(by=num_col, ascending=True)
            fig = px.bar(
                df_sorted,
                x=num_col,
                y=label_col,
                orientation='h',
                title=f"{num_col} by {label_col}",
                color=num_col,
                color_continuous_scale="Blues"
            )
            height = max(400, len(df) * 25)
            fig.update_layout(template="plotly_white", height=height)
            charts.append(fig)

    # CASE 5: Aggregation data (small dataset with percentages/counts)
    if (len(df) <= 8 and
            len(numeric_cols) == 1 and
            label_candidates):
        num_col = numeric_cols[0]
        label_col = label_candidates[0]

        # Pie chart for distribution data
        if df[num_col].sum() > 0:
            fig = px.pie(
                df,
                values=num_col,
                names=label_col,
                title=f"Distribution of {num_col}",
                hole=0.3  # Donut style
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )
            fig.update_layout(template="plotly_white")
            charts.append(fig)

    return charts


def render_plots_from_results(df):
    """Helper function to create and render plots from result list."""

    try:

        # Only proceed if DataFrame is not empty and has meaningful data
        if df.empty or len(df.columns) < 2:
            return

        # Skip if too many rows (performance) or too few rows (not meaningful)
        if len(df) > 500 or len(df) < 2:
            return

        # Analyze column types
        col_info = _infer_column_types(df)

        # Only create charts if we have numeric data to visualize
        if not col_info['numeric'] and not col_info['temporal']:
            return

        # Generate appropriate charts
        charts = _create_smart_chart(df, col_info)

        if charts:
            with st.expander("📈 Visualizations", expanded=False):
                # Display charts in a grid if multiple
                if len(charts) == 1:
                    st.plotly_chart(charts[0], width='stretch')
                elif len(charts) == 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(charts[0], width='stretch')
                    with col2:
                        st.plotly_chart(charts[1], width='stretch')
                else:
                    # For 3+ charts, show in rows of 2
                    for i in range(0, len(charts), 2):
                        cols = st.columns(2)
                        with cols[0]:
                            st.plotly_chart(
                                charts[i],
                                width='stretch'
                            )
                        if i + 1 < len(charts):
                            with cols[1]:
                                st.plotly_chart(
                                    charts[i + 1],
                                    width='stretch'
                                )

    except Exception as e:
        st.warning(f"Could not create visualizations: {e}")
