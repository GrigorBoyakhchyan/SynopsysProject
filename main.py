from graph import graph_builder
from nodes import *

impl = [
    ("question", question),
    ("answer", question),
    ("code", code_router),
    ("text", text_router),
    ("generate", passtrough),
    ("edit", passtrough),
    ("generate_code", generate_code),
    ("generate_text", generate_text),
    ("edit_code", edit_code),
    ("edit_text", edit_text),
    ("save_code", save_code),
    ("save_text", save_text),
    ("router", router),
]

builder = graph_builder(impl=impl)
compiled_graph = builder.compile()

if __name__ == "__main__":
    print(f"Hi!!! How can I assist you today?")
    while True:
        try:
            user_input = input()
            result = compiled_graph.invoke({"query": user_input})
            print(f"Result: ")
            for key, value in result.items():
                print(f"{key}: {value}")
        except KeyboardInterrupt:
            print(f"Bye, bye!!!")
            break
