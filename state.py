from typing import TypedDict


class PipelineState(TypedDict):
    topic: str
    research_results: list[str]
    summary: str
    quality_score: int
    report: str
    retry_count: int
    refined_query: str
