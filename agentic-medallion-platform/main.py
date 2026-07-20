from agents.profiler_agent import create_graph
def main():

    app = create_graph()

    initial_state = {
        "file_path": "data/sales_raw.csv",
        "schema": {},
        "quality": {},
        "statistics": {},
        "report": {}
    } 

    #Invoke the langgraph workflow with the initial state(langgraph workflow eg: start -> profiler -> end)
    result = app.invoke(initial_state)

    print("\n================== Final State ==================")
    print(result)

if __name__ == "__main__":
    main()