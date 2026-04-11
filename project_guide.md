# Project 3 — Workflow Orchestration

> **Automated Content Pipeline Agent**

---

## Description

You give it a broad topic (e.g. _"AI in healthcare"_). It runs a defined multi-step workflow: research the topic → summarize findings → generate a structured report → save it as a markdown file. Each step is a node, and the agent manages state as it flows between them.

**What you'll learn:** How to design a workflow as a graph of steps with shared state, how to make some steps conditional ("if research is thin, search again"), and how to use **LangGraph** (free, open source) as a lightweight workflow modeler. This directly maps to the MCP and workflow orchestration world.

**Key concepts:** LangGraph, DAG-based workflows, state machines, conditional edges, and how enterprise orchestration tools (n8n, Prefect, Temporal) relate to what you're building.

**Time estimate:** 1–2 days  
**Stack:** Python, LangGraph, Groq

---

## Build Steps

### Step 1 — Set Up Your Environment

- Create a new project folder: `project3-workflow-agent/`
- Install dependencies: `pip install langgraph groq python-dotenv requests beautifulsoup4`
- Confirm your Groq API key is accessible via `.env`
- Skim the [LangGraph quickstart docs](https://langchain-ai.github.io/langgraph/) — just the first page is enough
- **Goal:** Understand that LangGraph is just a way to define nodes (functions) and edges (transitions) in a graph

### Step 2 — Define Your State Object

- Create a Python `TypedDict` called `PipelineState` with fields like:
  - `topic: str` — the input topic
  - `research_results: list[str]` — raw search results
  - `summary: str` — the compressed summary
  - `report: str` — the final formatted report
  - `quality_score: int` — a self-assessed quality rating (used for conditional logic)
- **Goal:** In LangGraph, state is everything. Every node reads from state and writes back to it. This is the "shared memory" of the workflow.

### Step 3 — Build the Research Node

- Write a function `research_node(state: PipelineState) -> PipelineState`
- Inside, use the web search tool from Project 2 (or a simple `requests` call) to fetch information about `state["topic"]`
- Store results in `state["research_results"]`
- **Goal:** A node is just a Python function that takes state and returns updated state. Nothing magic.

### Step 4 — Build the Summarize Node

- Write a `summarize_node(state: PipelineState) -> PipelineState` function
- Call Gemini to compress `state["research_results"]` into a clean 3–5 paragraph summary
- Store in `state["summary"]`
- Also ask the model to rate the quality of the research from 1–10 and store in `state["quality_score"]`
- **Goal:** Nodes can call LLMs, run code, call APIs — they are just functions

### Step 5 — Add a Conditional Edge (Quality Check)

- This is the key orchestration concept: not all paths are linear
- After the summarize node, add a decision: if `quality_score < 6`, go back to the research node and search with a refined query; if `quality_score >= 6`, proceed to the report node
- In LangGraph, this is done with a `conditional_edge` that calls a small routing function
- Add a counter to prevent infinite re-research loops (max 2 retries)
- **Goal:** Understand conditional edges — this is what makes a workflow an intelligent pipeline, not just a script

### Step 6 — Build the Report Generation Node

- Write a `report_node(state: PipelineState) -> PipelineState` function
- Call Gemini with the summary and ask it to generate a structured markdown report with sections: Introduction, Key Findings, Implications, and Further Reading
- Store the result in `state["report"]`
- **Goal:** See how a node can do complex formatting, not just raw data retrieval

### Step 7 — Build the Save Node

- Write a `save_node(state: PipelineState) -> PipelineState` function
- Save `state["report"]` to a local `.md` file named after the topic (e.g., `ai_in_healthcare_report.md`)
- Print a confirmation message
- **Goal:** The final node in many real pipelines is a "sink" — writing to a database, sending an email, posting to an API, etc.

### Step 8 — Assemble and Run the Graph

- Import LangGraph's `StateGraph`, add all your nodes, define the edges between them (including the conditional edge from Step 5), set the entry and finish points
- Compile the graph and invoke it with a starting state: `graph.invoke({"topic": "AI in healthcare"})`
- **Goal:** Watch the full pipeline execute end-to-end and produce a real markdown report

### Step 9 — Visualize the Graph

- LangGraph can output a Mermaid diagram of your graph: `graph.get_graph().draw_mermaid()`
- Print it and paste it into [mermaid.live](https://mermaid.live) to see your workflow visually
- **Goal:** Connect the code you wrote to the visual diagram — this is how orchestration tools like n8n and Prefect represent workflows

---

## Project Structure

```
project3-workflow-agent/
├── agent.py            # Graph assembly and entry point
├── nodes.py            # All node functions (research, summarize, report, save)
├── state.py            # PipelineState TypedDict definition
├── tools.py            # Reusable search/fetch utilities (from Project 2)
├── outputs/            # Generated reports saved here
├── .env                # API key (never commit this)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## The Workflow Graph (Visual)

```
[START]
   │
   ▼
[Research Node]
   │
   ▼
[Summarize Node] ──── quality < 6 ────► [Research Node] (retry, max 2x)
   │
   │ quality >= 6
   ▼
[Report Node]
   │
   ▼
[Save Node]
   │
   ▼
[END]
```

---

## How This Relates to the Real World

| What You Built     | Real-World Equivalent              |
| ------------------ | ---------------------------------- |
| LangGraph nodes    | Steps in n8n / Prefect tasks       |
| Conditional edges  | If/else branches in workflow tools |
| Shared state dict  | Message bus / workflow context     |
| The compiled graph | A deployed workflow / DAG          |
| Save node          | Webhook / database sink node       |

---

## Bonus Extensions

- Add a second parallel branch: while one path writes a report, another generates a 5-bullet executive summary
- Add a human-in-the-loop step where the workflow pauses and asks you to approve the summary before generating the report (LangGraph supports this natively with `interrupt_before`)
- Connect to your Project 1 memory store — save report summaries as long-term memories
- Add email delivery of the final report using a free SMTP service

---

## Features & Changelog

| Date | Feature | Notes |
| ---- | ------- | ----- |
| —    | —       | —     |

---

## Learnings & Notes

