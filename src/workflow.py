import rootutils
from langgraph.graph import StateGraph, START, END
import os
from pprint import pprint
import webbrowser
from typing import Annotated, List, Dict
from typing import Literal
from typing_extensions import TypedDict

# root = rootutils.find_root(search_from=os.path.dirname(__file__), indicator="README.md")
rootutils.setup_root(__file__, indicator="README.md", pythonpath=True)
# rootutils.setup_root(root, dotenv=True, pythonpath=True)

from utils.json_extraction import process_llm_output
from src.schema.schema import Plan, Code, NextPlan
from src.agents import critique, executor, planner
from src.state import PlanExecute

WORKING_DIR = "./data"

os.makedirs(os.path.join(WORKING_DIR, "generated"), exist_ok=True)


def plan_step(state: PlanExecute):
    response =  planner.invoke(input={"input": state["current_html"], "human_feedback": state["human_feedback"]})
    plan = process_llm_output(response.content, Plan)
    print("Plan generated !")
    return {"plan": plan.plan, "current_html": state["current_html"], "past_htmls": state['past_htmls'], "critique_count": state["critique_count"], "past_changes": state["past_changes"]}

def human_preference(state: PlanExecute):
    print("Choose your preferences:")
    for idx, choice in enumerate(state["plan"], start=1):
        print(f"{idx}.")
        pprint(choice)
        print()  # Blank line for better readability
    
    while True:
        try:
            # Take input from the user
            user_input = input(
                "Enter the numbers of the choices you want to accept, separated by commas (or type 'all' or 'none'): "
            ).strip().lower()

            if user_input == "all":
                # Take all choices
                selected_indices = list(range(len(state["plan"])))
            elif user_input == "none":
                # Take no choices
                return {"human_feedback": 'No' , "current_html": state["current_html"], "past_htmls": state["past_htmls"], "critique_count": state["critique_count"], "past_changes": state["past_changes"]}
            else:
                # Validate the input format
                if not all(part.strip().isdigit() for part in user_input.split(",")):
                    raise ValueError("Input must be numbers, 'all', or 'none'.")

                # Parse the input and validate
                selected_indices = [int(num.strip()) - 1 for num in user_input.split(",")]

                # Check if all indices are within range
                if not all(0 <= idx < len(state["plan"]) for idx in selected_indices):
                    raise ValueError("One or more selected numbers are out of range.")

            break  # Exit the loop if input is valid
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter valid numbers, 'all', or 'none'.")

    # Filter the choices based on user input
    filtered_plan = [state["plan"][i] for i in selected_indices]

    return {"plan": filtered_plan, "current_html": state["current_html"], "past_htmls": state['past_htmls'], "critique_count": state["critique_count"], "past_changes": state["past_changes"]}
        

def execute_step(state: PlanExecute):
    plan = state["plan"]
    input_html = state["current_html"]
    plan_list = "\n".join(
        f"- Step: {item['step']}\n  Reason: {item['reason']}"
        for item in plan
    )
    response = executor.invoke(input={'input':input_html, 'plan':plan_list})
    modified_html = process_llm_output(response.content, Code)
    print("New HTML generated !")
    state["past_htmls"].append(modified_html.modified_html)
    html_id = len(state['past_htmls'])
    html_file_path = os.path.join(WORKING_DIR, f"generated/generated_html_{html_id}.html")
    os.makedirs(WORKING_DIR, exist_ok=True)  # Ensure directory exists
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(modified_html.modified_html)
    
    changes = modified_html.changes_made
    state["past_changes"].append(changes)

    # Open the new HTML file in the default browser
    webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
    
    return {"current_html": modified_html.modified_html, "past_htmls": state["past_htmls"], "critique_count": state["critique_count"], "changes_made": modified_html.changes_made, "past_changes": state["past_changes"]}

def critique_step(state: PlanExecute):
    state['critique_count'] += 1
    if state['critique_count'] > 3:
        return {"plan": "No", "current_html": state["current_html"], "past_htmls": state["past_htmls"]}
    input_html = state["current_html"]
    response = critique.invoke(input={'input':input_html, 'plan':state["plan"]})
    next_plan = process_llm_output(response.content, NextPlan)
    print("Review generated !")
    return {"plan": next_plan.next_plan, "current_html": state["current_html"], "past_htmls": state["past_htmls"], "critique_count": state["critique_count"], "past_changes": state["past_changes"]}

def human_input(state: PlanExecute):
    critique_count = 0
    while True:
        try:
            preference = input("Which UI do you prefer? Options: 1, 2, 3, 4: ")
            if preference.isdigit() and 1 <= int(preference):
                preference = int(preference)
                break
            else:
                print("Invalid input. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # Set current_html based on preference
    if preference:
        current_html = state["past_htmls"][preference - 1]
    else:
        current_html = state["current_html"]

    # Prompt for feedback
    while True:
        try:
            feedback = input("Please provide your feedback if any (else type 'No'): ")
            if feedback.strip():  # Ensure input is not empty
                break
            else:
                print("Feedback cannot be empty. Please type something.")
        except Exception as e:
            print(f"Error while providing feedback: {e}")

    print("Feedback received !")
    if feedback and feedback.lower() != 'no':
        return {"human_feedback": feedback , "current_html": current_html, "past_htmls": state["past_htmls"], "critique_count": critique_count, "past_changes": state["past_changes"]}
    else:
        return {"human_feedback": 'No' , "current_html": current_html, "past_htmls": state["past_htmls"], "critique_count": critique_count, "past_changes": state["past_changes"]}       


def critique_condition(state: PlanExecute)->Literal["human", "executor"]:
    if (isinstance(state['plan'], str) and state['plan'].lower() == 'no') or state['critique_count'] > 3:
        return "human"
    else:
        return "executor"

def human_condition(state: PlanExecute)->Literal["planner", END]:
    if 'human_feedback' in state and state['human_feedback'].lower() == 'no':
        return END
    else:
        return "planner"
    
def pref_decision(state: PlanExecute)->Literal[END, "executor"]:
    if 'human_feedback' in state and state['human_feedback'].lower() == 'no':
        return END
    else:
        return "executor"
    


workflow = StateGraph(PlanExecute)

workflow.add_node("planner", plan_step)

workflow.add_node("human_pref", human_preference)

workflow.add_node("executor", execute_step)

workflow.add_node("critique", critique_step)

workflow.add_node("human", human_input)

workflow.add_edge(START, "planner")

workflow.add_edge("planner", "human_pref")

workflow.add_edge("executor", "critique")

workflow.add_conditional_edges("critique", critique_condition)

workflow.add_conditional_edges("human", human_condition)

workflow.add_conditional_edges("human_pref", pref_decision)

graph = workflow.compile()
