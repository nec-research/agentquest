from remoteweb.client import WebBrowserClient

from agentquest.utils import Observation


class GaiaDriver:
    def __init__(self, game, llm):
        self.problem = game["question"]  # The question to answer
        self.truth = game["final_answer"]  # The solution
        self.llm = llm
        self.browser = WebBrowserClient()

    def reset(self):
        # Instantiate your initial observation from the environment
        obs = Observation(output=self.problem, done=False)

        return obs

    def step(self, action):
        agent_out = action.action_value
        tool = agent_out.__class__.__name__

        if tool == "WebBrowse":
            output = agent_out.run(self.browser, llm=self.llm)
            output = output.to_str()
        elif tool == "OnlineSearch" or tool == "FileDownload":
            output = agent_out.run(self.browser)
        elif tool == "FileReader":
            output = agent_out.run(llm=self.llm)
        elif tool == "FinalAnswer":
            if agent_out.check(
                question=self.problem, answer=self.truth, llm=self.llm
            ).is_correct:
                # Return the observation
                obs = Observation(output="You won!", done=True)
            else:
                # Return the observation
                obs = Observation(output="Wrong answer. Try again.", done=False)
            return obs

        # Return the observation
        obs = Observation(output=output, done=False)
        return obs
