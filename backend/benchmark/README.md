# AskTennis AI Benchmark Suite

This directory contains tools to evaluate the accuracy of the Text-to-SQL agent.

## Usage

1.  **Run the Benchmark**:
    ```bash
    # Run first 5 questions
    python3 backend/benchmark/evaluate_agent.py --limit 5

    # Run specific questions by ID
    python3 backend/benchmark/evaluate_agent.py --ids 1,101,200
    ```

2.  **View Results**:
    Results are saved to `backend/benchmark/benchmark_results.json`.

3.  **Gold Standard Comparison**:
    If a question ID exists in `backend/benchmark/gold_standard.json`, the script will check if the expected keywords appear in the agent's answer and calculate an accuracy score.

## Files

*   `evaluate_agent.py`: Main script to run the agent against `TENNIS_ANALYTICAL_QUESTIONS_MCP.md`.
*   `gold_standard.json`: A JSON file containing manually verified answers/keywords for specific question IDs.
*   `benchmark_results.json`: Output file (overwritten on each run).
