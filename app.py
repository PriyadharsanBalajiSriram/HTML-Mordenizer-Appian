import rootutils
import logging
import os

# root = rootutils.find_root(search_from=os.path.dirname(__file__), indicator="README.md")
# rootutils.setup_root(root, dotenv=True, pythonpath=True)
rootutils.setup_root(__file__, indicator="README.md", pythonpath=True)


from src.workflow import graph

WORKING_DIR = "./data"

os.makedirs(WORKING_DIR, exist_ok=True)  # Ensure the working directory exists

log_file = os.path.join(WORKING_DIR, "cool.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()



if __name__ == "__main__":
    test_html_path = os.path.join(WORKING_DIR, "input/input.html")

    with open(test_html_path, 'r', encoding='utf-8') as f:
        raw_html = f.read()


    for event in graph.stream(input={"current_html": raw_html, "past_htmls": [], "critique_count": 0, "human_feedback": str('None'), "past_changes": []}, config = {"recursion_limit": 100}):
        for k, v in event.items():
            if k != "__end__":
                logger.info(f"Key: {k}")
                
                # Check if 'plan' exists in the value and log it
                if isinstance(v, dict) and 'plan' in v:
                    logger.info(f"  Plan: {v['plan']}")
                
                if 'changes_made' in v:
                    logger.info(f"  Changes Made: {v['changes_made']}")
                

                # Log critique_count
                logger.info(f"  Critique Count: {v.get('critique_count')}")
                
                # Log human_feedback
                logger.info(f"  Human Feedback: {v.get('human_feedback')}")
                
                # Log length of 'past_htmls'
                logger.info(f"  Past HTMLs Length: {len(v.get('past_htmls'))}")
                
                # Add a separator for clarity
                logger.info("-" * 40)
