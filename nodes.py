import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from state import PipelineState
from tools import web_search

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"


def research_node(state: PipelineState) -> dict:
    query = state.get("refined_query") or state["topic"]
    print(f"> Researching: {query}")
    results = web_search(query)
    print(f"  Found {len(results)} results.")
    return {
        "research_results": results,
        "retry_count": state.get("retry_count", 0) + 1,
    }


def summarize_node(state: PipelineState) -> dict:
    print("> Summarizing findings...")
    results_text = "\n\n".join(state["research_results"])
    prompt = f"""You are a research analyst. Given the raw search results below about the topic "{state['topic']}", produce:

1. A clean 3-5 paragraph summary capturing the most important findings.
2. A quality score from 1-10 rating how useful these results are for writing a structured report. Score harshly: 1-3 = mostly noise, 4-6 = some signal but gaps, 7-10 = solid coverage.
3. If the quality score is below 6, propose a refined search query that would surface better results. Otherwise return an empty string.

Return ONLY a JSON object with keys: summary, quality_score, refined_query.

RAW RESULTS:
{results_text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    print(f"  Quality: {int(data['quality_score'])}/10")

    return {
        "summary": data["summary"],
        "quality_score": int(data["quality_score"]),
        "refined_query": data.get("refined_query", ""),
    }


def route_after_summary(state: PipelineState) -> str:
    """Decide whether to retry research or proceed to report generation."""
    if state["quality_score"] >= 6:
        return "proceed"
    if state.get("retry_count", 0) >= 3:
        print("  Quality still low — proceeding anyway (out of retries).")
        return "proceed"
    print("  Quality below threshold — retrying with refined query.")
    return "retry"


def report_node(state: PipelineState) -> dict:
    print("> Generating report...")
    prompt = f"""Write a structured markdown report on "{state['topic']}" using the summary below.

The report must have these sections (use ## headers):
- Introduction
- Key Findings (use bullet points)
- Implications
- Further Reading

Use proper markdown. No preamble, no "here is your report" — start directly with "# {state['topic'].title()}".

SUMMARY:
{state['summary']}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"report": response.choices[0].message.content}


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def save_node(state: PipelineState) -> dict:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    filepath = outputs_dir / f"{_slugify(state['topic'])}_report.md"
    filepath.write_text(state["report"], encoding="utf-8")
    print(f"> Report saved to {filepath}")
    return {}
