import sys

from langgraph.graph import StateGraph, END

from nodes import (
    research_node,
    summarize_node,
    report_node,
    save_node,
    route_after_summary,
)
from state import PipelineState


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("research", research_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("report", report_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("research")

    graph.add_edge("research", "summarize")
    graph.add_conditional_edges(
        "summarize",
        route_after_summary,
        {"retry": "research", "proceed": "report"},
    )
    graph.add_edge("report", "save")
    graph.add_edge("save", END)

    return graph.compile()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python agent.py "your topic here"')
        print('       python agent.py --visualize')
        sys.exit(1)

    app = build_graph()

    if sys.argv[1] == "--visualize":
        print(app.get_graph().draw_mermaid())
        sys.exit(0)

    topic = " ".join(sys.argv[1:])
    final_state = app.invoke({"topic": topic})
    print(f"\nDone. Quality: {final_state['quality_score']}, Retries: {final_state['retry_count'] - 1}")
