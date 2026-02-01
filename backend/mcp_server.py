import os
import sys
import pandas as pd
from mcp.server.fastmcp import FastMCP
from sqlalchemy import text, inspect

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.database_service import DatabaseService

# Initialize MCP Server
mcp = FastMCP("AskTennis Data Service")

# Initialize Database Service
# We use the existing DatabaseService to handle connection logic (SQLite vs Cloud SQL)
try:
    db_service = DatabaseService()
    print(
        f"MCP Server connected to database type: {db_service._get_db_type()}",
        file=sys.stderr,
    )
except Exception as e:
    print(f"Failed to connect to database: {e}", file=sys.stderr)
    db_service = None


@mcp.tool()
def list_tables() -> str:
    """List all available tables in the tennis database."""
    if not db_service:
        return "Database connection not available."

    try:
        with db_service._get_connection() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            return f"Available tables: {', '.join(tables)}"
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def query_tennis_database(sql_query: str) -> str:
    """
    Execute a read-only SQL query against the tennis database.

    Args:
        sql_query: The SQL SELECT statement to execute.

    Returns:
        A JSON string representation of the query results.
    """
    if not db_service:
        return "Database connection not available."

    # Basic security check for read-only
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    try:
        # Use pandas to read sql and return json
        # We need to format specific for the db type if needed, but read_sql handles most
        with db_service._get_connection() as conn:
            # Handle parameter formatting if needed, but for raw strings we pass directly
            # Note: In production, passing raw SQL from LLM is risky, but standard for this tool pattern
            df = pd.read_sql(text(sql_query), conn)

            # Limit rows to prevent massive payloads
            if len(df) > 100:
                df = df.head(100)

            return df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.resource("tennis://schema")
def get_database_schema() -> str:
    """Get the schema definition of the tennis data database."""
    if not db_service:
        return "Database connection not available."

    schema_info = []

    try:
        with db_service._get_connection() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()

            for table in tables:
                schema_info.append(f"Table: {table}")
                columns = inspector.get_columns(table)
                for col in columns:
                    col_str = f"  - {col['name']} ({col['type']})"
                    if col.get("primary_key"):
                        col_str += " [PK]"
                    if col.get("foreign_keys"):
                        col_str += f" [FK: {col['foreign_keys']}]"
                    schema_info.append(col_str)
                schema_info.append("")  # Empty line between tables

        return "\n".join(schema_info)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


@mcp.resource("tennis://questions")
def get_analytical_questions() -> str:
    """Return a curated list of analytical questions for inspiration."""

    # Based on TENNIS_ANALYTICAL_QUESTIONS_MCP.md
    questions = """
    1. Which player has the highest number of Grand Slam titles in the Open Era?
    2. List all players who have won more than 100 matches in a single calendar year.
    3. Compare the win-loss record of left-handed vs. right-handed players in Grand Slam finals.
    4. Which tournament has the highest average number of aces per match in the last 20 years?
    5. Identify players who won their first Grand Slam after the age of 30.
    6. Who has the highest winning percentage in "Night Sessions"?
    7. Find the longest match (in minutes) for each Grand Slam tournament.
    8. Which player has the most wins against the World No. 1 without ever reaching No. 1 themselves?
    9. Compare the success rate of serve-and-volley players on Grass vs Clay.
    10. Who has the most break points saved in a single match?
    """
    return questions


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
