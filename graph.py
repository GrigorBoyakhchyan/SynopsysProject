from typing import Callable, Any, Optional, Type
from types import ModuleType
import importlib
from langgraph.graph import StateGraph, START, END

def graph_builder(
        *,
        state_schema: Optional[Type[Any]] = None,
        config_schema: Optional[Type[Any]] = None,
        input: Optional[Type[Any]] = dict,
        output: Optional[Type[Any]] = dict,
        impl_module: Optional[ModuleType] = None,
)->StateGraph:
    builder = StateGraph(
        state_schema=state_schema,
        config_schema=config_schema,
        input=input,
        output=output,
    )

    if impl_module is None:
        impl_module = importlib.import_module("nodes")

    def _getf(name: str)->Callable:
        fn = getattr(impl_module, name, None)
        if not callable(fn):
            raise ValueError(
                f"Missing node implementation for '{name}' in impl"
                f"Add ('{name}', <callable>) to impl"
            )
        return fn
    
    def _passthrough(state: dict)->dict:
        return state

    passthrough_fn = (
        getattr(impl_module, "passthrough", None)
        or
        _passthrough
        )


    builder.add_node("question", _getf("question"))
    builder.add_node("answer", passthrough_fn)

    builder.add_node("code", passthrough_fn)
    builder.add_node("text", passthrough_fn)

    builder.add_node("generate_code", _getf("generate_code"))
    builder.add_node("edit_code", _getf("edit_code"))
    builder.add_node("save_code", _getf("save_code"))
    
    builder.add_node("generate_text", _getf("generate_text"))
    builder.add_node("edit_text", _getf("edit_text"))
    builder.add_node("save_text", _getf("save_text"))

    builder.add_edge("question", "answer")
    builder.add_edge("answer", END)
    
    builder.add_edge("generate_code", "save_code")
    builder.add_edge("edit_code", "save_code")
    builder.add_edge("save_code", END)

    builder.add_edge("generate_text", "save_text")
    builder.add_edge("edit_text", "save_text")
    builder.add_edge("save_text", END)

    builder.add_conditional_edges(
        START,
        _getf("router"),
       {
            "question": "question",
            "code": "code",
            "text": "text"
       },
    )
    builder.add_conditional_edges(
        "code",
        _getf("code_router"),
        {
            "generate_code": "generate_code",
            "edit_code": "edit_code"
        },
    )
    builder.add_conditional_edges(
        "text",
        _getf("text_router"),
        {
            "generate_text": "generate_text",
            "edit_text": "edit_text"
        },
    )

    return builder