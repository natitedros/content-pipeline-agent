import json
import os

from dotenv import load_dotenv
from groq import Groq

from state import PipelineState
from tools import web_search

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"


def research_node(state: PipelineState) -> dict:
    query = state.get("refined_query") or state["topic"]
    results = web_search(query)
    return {
        "research_results": results,
        "retry_count": state.get("retry_count", 0) + 1,
    }


def summarize_node(state: PipelineState) -> dict:
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

    return {
        "summary": data["summary"],
        "quality_score": int(data["quality_score"]),
        "refined_query": data.get("refined_query", ""),
    }
