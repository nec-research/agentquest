"""
Tested with WebShop Commit Version: 64fa2a5

This is a REST API interface to interact with WebShop's text environment from outside.
Why: Because WebShop runs in a different Virtual Environment than AgentQuest (for dependency issues and conflicts)
Benefits: Lightweight Flask Wrapper running in WebShop's virtual environment

Usage:
- Run this with .webshop-venv (not agentquest's .venv)
- Remember, it is a one client system. The env variable is stateful.
- Everytime the reset is called, a new goal is loaded.
- Once, done=True after a step() call, make sure the reset() API is called manually.
"""

import sys

sys.path.insert(1, "./WebShop")


import gym
from flask import Flask, jsonify, request
from web_agent_site.envs import WebAgentTextEnv  # type: ignore  # noqa: F401
from web_agent_site.utils import DEBUG_PROD_SIZE  # type: ignore

app = Flask(__name__)
env = gym.make(
    "WebAgentTextEnv-v0", observation_mode="text", num_products=DEBUG_PROD_SIZE
)


@app.route("/")
def test():
    return jsonify({"test": "okay"})


@app.route("/reset", methods=["POST"])
def reset():
    """Every reset call invokes a new item being loaded in webshop"""
    obs, info = env.reset()
    available_actions = env.get_available_actions()
    response = jsonify(
        {"obs": obs, "info": info, "available_actions": available_actions}
    )
    return response


@app.route("/step", methods=["POST"])
def step():
    action = request.json.get("action", 0)
    obs, reward, done, info = env.step(action)
    available_actions = env.get_available_actions()
    return jsonify(
        {
            "obs": obs,
            "reward": reward,
            "done": done,
            "info": info,
            "available_actions": available_actions,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)
