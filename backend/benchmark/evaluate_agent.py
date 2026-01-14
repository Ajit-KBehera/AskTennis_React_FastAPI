
import sys
import os
import json
import re
import random
import time
import argparse
from typing import List, Dict, Any

# Add the backend directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor

QUESTION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../TENNIS_ANALYTICAL_QUESTIONS_MCP.md'))
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'benchmark_results.json')
GOLD_STANDARD_FILE = os.path.join(os.path.dirname(__file__), 'gold_standard.json')

def parse_questions(filepath: str) -> List[Dict[str, Any]]:
    """
    Parses the markdown file to extract questions.
    Assumes format like "1. Question text"
    """
    questions = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Match lines starting with a number followed by a dot
            match = re.match(r'^(\d+)\.\s+(.+)', line)
            if match:
                q_id = int(match.group(1))
                q_text = match.group(2)
                questions.append({'id': q_id, 'question': q_text})
    return questions

def load_gold_standard() -> Dict[int, Any]:
    if os.path.exists(GOLD_STANDARD_FILE):
        with open(GOLD_STANDARD_FILE, 'r') as f:
            return {item['id']: item for item in json.load(f)}
    return {}

def run_benchmark(limit: int = 5, question_ids: List[int] = None):
    print(f"--- Loading Questions from {QUESTION_FILE} ---")
    all_questions = parse_questions(QUESTION_FILE)
    print(f"Found {len(all_questions)} questions.")

    if question_ids:
        questions_to_run = [q for q in all_questions if q['id'] in question_ids]
    else:
        questions_to_run = all_questions[:limit] if limit else all_questions

    print(f"--- Initializing Agent ---")
    try:
        agent_graph = setup_langgraph_agent()
        query_processor = QueryProcessor()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    results = []
    gold_standard = load_gold_standard()

    print(f"--- Starting Benchmark on {len(questions_to_run)} questions ---")
    for i, q in enumerate(questions_to_run):
        print(f"Processing ({i+1}/{len(questions_to_run)}): [ID {q['id']}] {q['question']}")
        
        start_time = time.time()
        try:
            response = query_processor.handle_user_query(q['question'], agent_graph)
            duration = time.time() - start_time
            
            result_entry = {
                "id": q['id'],
                "question": q['question'],
                "generated_sql": response.get("sql_queries", []),
                "generated_answer": response.get("answer", ""),
                "duration_seconds": round(duration, 2),
                "status": "success"
            }
            
            # Simple verification if gold standard exists
            if q['id'] in gold_standard:
                gs = gold_standard[q['id']]
                result_entry["gold_expected_keywords"] = gs.get("expected_answer_keywords", [])
                
                # Check for keywords
                gen_ans_lower = str(response.get("answer", "")).lower()
                keywords_met = [k for k in gs.get("expected_answer_keywords", []) if k.lower() in gen_ans_lower]
                
                is_correct = len(keywords_met) == len(gs.get("expected_answer_keywords", []))
                result_entry["is_correct"] = is_correct
                result_entry["keywords_found"] = keywords_met
                
            else:
                 result_entry["is_correct"] = None # Unknown
                
        except Exception as e:
            print(f"Error processing question {q['id']}: {e}")
            result_entry = {
                "id": q['id'],
                "question": q['question'],
                "error": str(e),
                "status": "error",
                "is_correct": False
            }
        
        results.append(result_entry)
        
        # Save intermediate results
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(results, f, indent=2)

    # Calculate Score
    total_checked = len([r for r in results if r.get("is_correct") is not None])
    total_correct = len([r for r in results if r.get("is_correct") is True])
    
    print(f"--- Benchmark Complete. Results saved to {OUTPUT_FILE} ---")
    if total_checked > 0:
        print(f"Accuracy vs Gold Standard: {total_correct}/{total_checked} ({total_correct/total_checked*100:.1f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AskTennis Benchmark")
    parser.add_argument("--limit", type=int, default=5, help="Number of questions to run (default: 5)")
    parser.add_argument("--ids", type=str, help="Comma-separated list of question IDs to run (e.g. 1,5,10)")
    parser.add_argument("--range", type=str, help="Range of question IDs to run (e.g. 1-10)")

    args = parser.parse_args()
    
    q_ids = []
    if args.ids:
        q_ids.extend([int(x.strip()) for x in args.ids.split(',')])
        
    if args.range:
        try:
            start, end = map(int, args.range.split('-'))
            q_ids.extend(range(start, end + 1))
        except ValueError:
            print("Error: Invalid range format. Please use 'start-end' (e.g., 1-10).")
            sys.exit(1)
            
    # Deduplicate and sort if we have IDs
    if q_ids:
        q_ids = sorted(list(set(q_ids)))
    else:
        q_ids = None
    
    run_benchmark(limit=args.limit, question_ids=q_ids)
