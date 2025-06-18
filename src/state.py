from typing import Annotated, List, Dict
from typing_extensions import TypedDict


class PlanExecute(TypedDict):
    current_html: str
    plan: List[Dict[str, str]]
    past_htmls: List[str]
    critique_count: int
    human_feedback: str
    changes_made: List[Dict[str, str]]
    past_changes: List[List[Dict[str, str]]]
