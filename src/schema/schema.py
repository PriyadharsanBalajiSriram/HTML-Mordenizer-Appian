from pydantic import BaseModel, Field
from typing import List, Dict, Union

class Plan(BaseModel):
    """Plan that the generator agent will folow"""
    application_type: str = Field(
        description="The type of application that the HTML represents. Eg: login page, dashboard, etc."
    )
    plan: List[Dict[str, str]] = Field(
        description="A list of dictionaries where each dictionary contains two keys: 'step' (the step as a string) and 'reason' (why this step is done as a string). Each dictionary represents one step."
    )

class Code(BaseModel):
    """Code that the generator agent will generate based on the plan"""
    modified_html: str = Field(
        description="The modified HTML code based on the plan."
    )
    changes_made: List[Dict[str, str]] = Field(
        description="A list of dictionaries where each dictionary contains two keys: 'step' (the step as a string) and 'reason' (why this step is done as a string). Each dictionary represents one step."
    )

class NextPlan(BaseModel):
    """Feedback from Reviewer"""
    next_plan: Union[
        List[Dict[str, str]],  # A list of dictionaries with 'step' and 'reason' as keys
        str  # A string, e.g., 'No' if the HTML is perfect
    ] = Field(
        description="Either a list of dictionaries where each dictionary contains 'step' and 'reason', or string 'No' if the HTML is perfect."
    )
