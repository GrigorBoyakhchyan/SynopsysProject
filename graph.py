from typing import Callable, Any, Optional, Type
from langgraph.graph import StateGraph, START, END

def graph_builder(
        *,
        state_schema: Optional[Type[Any]] = None,
        config_schema: Optional[Type[Any]] = None,
        input: Optional[Type[Any]] = dict,
        output: Optional[Type[Any]] = dict,
        impl: list[tuple[str, Callable]]
)->StateGraph:
    builder = StateGraph(
        state_schema=state_schema,
        config_schema=config_schema,
        input=input, 
        output=output
    )

    nodes_by_name = {name: imp for name, imp in impl}

    builder.add_node(START, nodes_by_name["router"])

    builder.add_node("question", nodes_by_name["question"])
    builder.add_node("answer", nodes_by_name["answer"])

    builder.add_node("code", nodes_by_name["code"])
    builder.add_node("text", nodes_by_name["text"])

    builder.add_node("generate", nodes_by_name["generate"])
    builder.add_node("edit", nodes_by_name["edit"])

    builder.add_node("generate_code", nodes_by_name["generate_code"])
    builder.add_node("generate_text", nodes_by_name["generate_text"])

    builder.add_node("edit_code", nodes_by_name["edit_code"])
    builder.add_node("edit_text", nodes_by_name["edit_text"])

    builder.add_node("save_code", nodes_by_name["save_code"])
    builder.add_node("save_text", nodes_by_name["save_text"])

    builder.add_edge("answer", END)
    builder.add_edge("save_code", END)
    builder.add_edge("save_text", END)
    builder.add_edge("question", "answer")
    
    builder.add_edge("generate", "generate_code")
    builder.add_edge("generate_code", "save_code")
    builder.add_edge("edit", "edit_code")
    builder.add_edge("edit_code", "save_code")

    builder.add_edge("generate", "generate_text")
    builder.add_edge("generate_text", "save_text")
    builder.add_edge("edit", "edit_text")
    builder.add_edge("edit_text", "save_text")



    builder.add_conditional_edges(
        START,
        nodes_by_name["router"],
       {
            "question": "question",
            "code": "code",
            "text": "text"
       }
    )
    builder.add_conditional_edges(
        "code",
        nodes_by_name["code"],
        {
            "generate_code": "generate",
            "edit_code": "edit"
        }
    )
    builder.add_conditional_edges(
        "text",
        nodes_by_name["text"],
        {
            "generate_text": "generate",
            "edit_text": "edit"
        }
    )

    return builder