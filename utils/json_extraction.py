import json
import re
from pydantic import BaseModel, ValidationError

def process_llm_output(raw_output: str, response_format: BaseModel) -> BaseModel:
    """
    Process the raw output from the LLM and ensure it complies with the Plan schema.

    Args:
        raw_output (str): The raw output from the LLM, including markdown-style JSON.

    Returns:
        Plan: A validated Pydantic Plan object.

    Raises:
        ValueError: If the output cannot be processed or validated.
    """
    # Step 1: Strip the markdown code block indicators
    if raw_output.startswith("```json"):
        pattern = r"```json\n(.+)\n```"
        raw_output = re.sub(pattern, r"\1", raw_output, flags=re.DOTALL)


    # Step 2: Parse the JSON string into a dictionary
    try:
        output_dict = json.loads(raw_output, strict=False)
        # output_dict = preprocess_json(raw_output)
    except json.JSONDecodeError as e:
        print("JSONDecodeerror_json : ", raw_output)
        raise ValueError(f"Invalid JSON format: {e}")

    # Step 3: Validate the parsed data with Pydantic
    try:
        validated_plan = response_format.model_validate(output_dict)
    except ValidationError as e:
        print("Validationerror_json : ", output_dict)
        raise ValueError(f"Validation failed: {e}")

    return validated_plan
