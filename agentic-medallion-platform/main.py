import sys

from agents.profiler_agent import create_graph


def main() -> None:
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data/sales_raw.csv"

    app = create_graph()
    initial_state = {
        "file_path": file_path,
        "schema": {},
        "quality": {},
        "statistics": {},
        "report": {},
    }

    result = app.invoke(initial_state)

    print("\n================== Final State ==================")
    print(result.get("final_report", result))

if __name__ == "__main__":
    main()