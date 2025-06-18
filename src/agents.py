import rootutils
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# root = rootutils.find_root(search_from=os.path.dirname(__file__), indicator="README.md")
# rootutils.setup_root(root, dotenv=True, pythonpath=True)

rootutils.setup_root(__file__, indicator="README.md", pythonpath=True)

from src.config.prompts import planner_prompt, executor_prompt, reflection_prompt

load_dotenv()

class planner_agent:
    """
    Analysis agent:
    #### Inputs 
    1. Raw HTML

    #### Actions
    This agent will have the following objectives :
    1. Analyze and understand the application that the HTML is representing
    2. Identify the areas of improvements that can modernize the HTML

    #### Outputs
    1. A report that will have the following details
        1. The application type - eg: login page, dashboard, etc
        2. The areas of improvements - eg: use of tables, inline styles, etc
        3. The modernization suggestions - eg: use of flexbox, grid, etc
        
    """

    def __init__(self):
        self.llm = ChatLiteLLM(model="gemini/gemini-1.5-flash")
        self.system_prompt = planner_prompt
        self.user_prompt = """Now analyze the following code : \
                            """
        self.feedback_prompt = """Additional inputs: \
                                """
        self.SystemPrompt = SystemMessage(content=self.system_prompt)
        self.UserPrompt = HumanMessage(content=self.user_prompt)

        self.messages = (
            self.SystemPrompt + self.UserPrompt + "{input}" + self.feedback_prompt + "{human_feedback}"
        )

    def chain(self):
        planner = self.messages | self.llm
        return planner        





class executor_agent:
    '''
    #### Inputs 
    1. Raw HTML
    2. Created plan

    #### Actions
    This agent will have the following objectives :
    1. Modify the given HTML based on the plan created by the Planner

    #### Outputs
    1. Modified HTML
    '''
    def __init__(self):
        self.llm = ChatLiteLLM(model="gemini/gemini-1.5-flash")
        self.system_prompt = executor_prompt
        self.user_prompt1 = """Now modify the following code : \
                            """
        self.user_prompt2 = """based on the following plan : \
                            """
        self.SystemPrompt = SystemMessage(content=self.system_prompt)
        self.UserPrompt1 = HumanMessage(content=self.user_prompt1)
        self.UserPrompt2 = HumanMessage(content=self.user_prompt2)

        self.messages = (self.SystemPrompt + self.UserPrompt1 + "{input}" + self.UserPrompt2 + "{plan}")

    def chain(self):
        executor = self.messages | self.llm
        return executor



class reflection_agent:
    '''
    #### Inputs 
    1. Modified HTML

    #### Actions
    This agent will have the following objectives :
    1. Critique the modified HTML and provide feedback

    #### Outputs
    1. next_plan
    '''
    def __init__(self):
        self.llm = ChatLiteLLM(model="gemini/gemini-1.5-flash")
        
        self.system_prompt = reflection_prompt
        self.user_prompt1 = """Now critique this code : \
                            """
        self.user_prompt2 = """based on the following plan : \
                            """
        self.SystemPrompt = SystemMessage(content=self.system_prompt)
        self.UserPrompt1 = HumanMessage(content=self.user_prompt1)
        self.UserPrompt2 = HumanMessage(content=self.user_prompt2)

        self.messages = (self.SystemPrompt + self.UserPrompt1 + "{input}" + self.UserPrompt2 + "{plan}")

    def chain(self):
        critique = self.messages | self.llm
        return critique
    

planner = planner_agent().chain()
executor = executor_agent().chain()
critique = reflection_agent().chain()
