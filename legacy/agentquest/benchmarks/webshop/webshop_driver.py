import importlib
import json
import random
import sys

import gym

from agentquest.utils import Observation


# Adds a custom `can_proceed` attribute to Observation class
class ObservationExt(Observation):
    def __init__(self, output: str, done: bool, can_proceed: bool):
        self.output = output
        self.done = done
        self.can_proceed = can_proceed


class WebshopDriver:
    def __init__(self, goal):
        base_package_name = __package__.split(".")[0]
        base_package_path = importlib.resources.files(
            base_package_name
        )  # root dir of agentquest package, i.e. agentquest_repo_root_dir/agentquest
        # TODO is there a better way? Probably we should install web_agent_site as package
        sys.path.append(f"{base_package_path}/../benchmarks/webshop/webshop")

        # WebAgentTextEnv driver automatically generates a list of goals starting from the list of products and considering all the combinations of
        # products and configurations (e.g. item size/color). By default WebShop only uses a sample of 1k products and this yields to 6910 tasks.
        # However get_synthetic_goals() adds randomly generated set of prices.
        # In order to guarantee a consistent set of goals across multiple runs of the benchmark we fix the seed.
        # This also allows to properly select individual goals by first generating all of them, by allocating a dummy WebshopDriver in webshop_load_data(),
        # and then by filtering a specific one through the filter_goals_fx().
        random.seed(1234)
        self.goal = goal
        self.env = gym.make(
            "WebAgentTextEnv-v0",
            observation_mode="text",
            filter_goals=self.filter_goals_fx,
        )

    """
    # Example of goal
    {
        'asin': 'B09P8D2Q1Q',
        'category': 'garden',
        'query': 'home office cabinets',
        'name': 'Tiamu File Cabinet - Vertical Filing Cabinet - Office Cabinet with Open Storage Shelf and Drawer - Letter Size Large Modern Storage Cabinet Printer Stand, for Office, Study, Living Room',
        'product_category': 'Office Products › Office Furniture & Lighting › Cabinets, Racks & Shelves › File Cabinets › Vertical File Cabinets',
        'instruction_text': 'Find me home office cabinets with storage space for living room, and price lower than 210.00 dollars',
        'attributes': ['storage space', 'living room'],
        'price_upper': 210.0,
        'goal_options': {},
        'weight': 0.01866359447004608
    }
    """

    def filter_goals_fx(self, goal_idx, goal):
        if self.goal is None:
            return True
        else:
            # Quick comparison based on the product ID
            if goal["asin"] == self.goal["asin"]:
                # Deep comparison on the rest of the attributes
                if self.compare_dicts(goal, self.goal):
                    # print(f'goal_idx: {goal_idx}')
                    # print(f'goal: {goal}')
                    return True

            return False

    @staticmethod
    def compare_dicts(dict1, dict2):
        # Check if the dictionaries have the same keys
        if set(dict1.keys()) != set(dict2.keys()):
            return False

        # Check if the values for each key are equal
        for key in dict1:
            if dict1[key] != dict2[key]:
                return False

        # Dictionaries are equal
        return True

    def reset(self):
        first_obs, _ = self.env.reset()
        available_actions = self.env.get_available_actions()
        obj = {"state": first_obs, "admissible_actions": available_actions}
        obs = ObservationExt(output=json.dumps(obj), done=False, can_proceed=True)
        return obs

    def step(self, action):
        action = action.action_value
        obs_, reward, done, info = self.env.step(action)
        available_actions = self.env.get_available_actions()
        self.last_reward = reward

        if not done:
            obj = {"state": obs_, "admissible_actions": available_actions}
            obj = json.dumps(obj)
            obs = ObservationExt(output=obj, done=False, can_proceed=True)
        else:
            # `done` is set to True by the WebShop web agent (OpenAI Gym) whenever the "Buy Now" button has been clicked, i.e. the user session has been completed.
            # However, the success of the task from the AgentQuest perspective, i.e. obs.done, should be based on having reached reward 1.0.
            # This is confirmed by "Evaluation Metrics" paragraph in Section 3.1 of WebShop paper (https://arxiv.org/pdf/2207.01206.pdf).
            # We use an additional `can_proceed` attribute to signal to the human/agent that no further actions are allowed.
            if reward == 1.0:
                obj = json.dumps({"state": "You Won!"})
                obs = ObservationExt(output=obj, done=True, can_proceed=False)
            else:
                obj = json.dumps({"state": "You Lost!"})
                obs = ObservationExt(output=obj, done=False, can_proceed=False)

        # TODO comment/remove?
        print("---[WebshopDriver DEBUG]--------------------")
        print(f"- Observation: {obs_}")
        print(f"- Reward: {reward}")
        print(f"- Done: {done}")
        print(f"- Info: {info}")
        print("---------------------")
        print(f"- AgentQuest.done: {obs.done}")
        print(f"- AgentQuest.can_proceed: {obs.can_proceed}")
        print("--------------------------------------------")

        return obs

    def get_last_reward(self):
        return self.last_reward


def webshop_load_data(**kwargs):
    # Instantiate a dummy WebAgentTextEnv just to trigger the automatic creation
    # of the synthetic set of goals from the list of products
    dummy_driver = WebshopDriver(None)
    goals = dummy_driver.env.env.server.goals

    return goals
