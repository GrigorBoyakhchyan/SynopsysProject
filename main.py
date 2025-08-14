from graph import graph_builder

builder = graph_builder()
compiled_graph = builder.compile()

if __name__ == "__main__":
    print(f"Hi!!! How can I assist you today?")
    while True:
        try:
            user_input = input().strip()
            if not user_input:
                continue
            result = compiled_graph.invoke({"query": user_input})
            print(f"Result: ")
            for key, value in result.items():
                print(f"{key}: {value}")
        except KeyboardInterrupt:
            print(f"Bye, bye!!!")
            break
