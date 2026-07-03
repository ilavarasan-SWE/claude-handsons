from agents.profiler_agent import create_graph
def main():

    app = create_graph()

    initial_state = {
        "file_path": "data/sample_data.csv",
        "schema": {},
        "quality": {},
        "statistics": {},
        "report": {}
    }

    result = app.invoke(initial_state)

    print("\n================== Final State ==================")
    print(result)

if __name__ == "__main__":
    main()