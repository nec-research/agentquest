import json
import re
import sys

from agentquest.utils import Observation

from .utils.api import *
from .utils.sparql_executer import SparqlExecuter


class KnowledgeGraphDriver:
    def __init__(self, record):
        self.record = record
        self.sparql_executor = SparqlExecuter()
        self.variables_list = []
        self.answer = record["answer"]
        self.intersection_was_called = False

    def reset(self):
        obj = {"question": self.record["question"], "entities": self.record["entities"]}

        obs = Observation(output=json.dumps(obj), done=False)
        return obs

    def extract_function_and_arguments(self, action):
        function_name = re.findall(r"(\w+)\(", action)
        matches = re.findall(r"{}\((.+?)\)".format(function_name), action)
        arguments = re.split(r"\s*,\s*", matches[0])
        func = getattr(sys.modules[__name__], function_name[0])

        return func, arguments

    def prepare_function_call(self, arguments):
        args_to_exec = []
        for i, argument in enumerate(arguments):
            if isinstance(argument, str):
                argument = argument.replace("'", "")
            if argument.startswith("#"):
                # Replace the variable with the actual value
                args_to_exec.append(self.variables_list[int(argument[1:])])
            else:
                args_to_exec.append(argument)

        # Add the sparql executor as the last argument
        args_to_exec.append(self.sparql_executor)

        return args_to_exec

    def step(self, action):
        if "FINAL ANSWER" in action.action_value:
            if self.intersection_was_called:
                return self.check_correct(action)
            else:
                obs = Observation(
                    output="Your answer is partial. You should use intersection at least once before getting the final answer.",
                    done=False,
                )
                return obs

        action = action.action_value
        if "intersection" in action:
            self.intersection_was_called = True
        # Extract the function name and the arguments from the output
        try:
            func, arguments = self.extract_function_and_arguments(action)
            # Create function call with arguments
            arguments = self.prepare_function_call(arguments)
        except:
            execution, execution_message = None, "Invalid action format."
            obs = Observation(output=execution_message, done=False)
            return obs
        # Call the function with the arguments
        try:
            execution, execution_message = func(*arguments)
        except Exception as e:
            if "JOIN" in str(e):
                execution, execution_message = (
                    None,
                    "Error: Before using get_neighbors, use get_relations.",
                )
            else:
                execution, execution_message = None, f"Error: {str(e)}"
        if execution:
            execution_message = execution_message.replace(
                "##", f"#{len(self.variables_list)}"
            )
            self.variables_list.append(execution)
        obs = Observation(output=execution_message, done=False)

        return obs

    def check_correct(self, action):
        final_answer = action.action_value
        final_answer = re.findall(r"(?:Find|FINAL) ANSWER: #(\d+)", final_answer)
        try:
            answer_variable = self.variables_list[int(final_answer[0])]
        except IndexError:
            obs = Observation(output="Invalid variable ID. Try again", done=False)
            return obs

        answer = final_execute(answer_variable, self.sparql_executor)
        correct = True
        for ans in self.answer:
            if ans["answer_argument"] not in answer:
                correct = False
                obs = Observation(output="Wrong answer. Try again.", done=False)

        if correct:
            obs = Observation(output="You won!", done=True)

        return obs
