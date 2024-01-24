import os
import json
import gym
import textworld
import textworld.gym
from alfworld.agents.utils.misc import Demangler, add_task_to_grammar
from termcolor import colored
from alfworld.info import ALFWORLD_DATA
from agentquest.utils import Observation

class AlfredDemangler(textworld.core.Wrapper):

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)

        demangler = Demangler(game_infos=self._game.infos)
        for info in self._game.infos.values():
            info.name = demangler.demangle_alfred_name(info.id)

DOMAIN = '/tmp/alfworld_data/logic/alfred.pddl'
GRAMMAR = '/tmp/alfworld_data/logic/alfred.twl2'

class AlfWorldDriver():
    def __init__(self, problem):
        GAME_LOGIC = {
            "pddl_domain": open(DOMAIN).read(),
            "grammar": open(GRAMMAR).read(),
        }
        # load state and trajectory files
        pddl_file = os.path.join(problem, 'initial_state.pddl')
        json_file = os.path.join(problem, 'traj_data.json')
        with open(json_file, 'r') as f:
            traj_data = json.load(f)
        GAME_LOGIC['grammar'] = add_task_to_grammar(
            GAME_LOGIC['grammar'], 
            traj_data
        )

        # dump game file
        gamefile = os.path.join(os.path.dirname(pddl_file), 'game.tw-pddl')

        # register a new Gym environment.
        infos = textworld.EnvInfos(won=True, admissible_commands=True)
        env_id = textworld.gym.register_game(
            gamefile, 
            infos, 
            max_episode_steps=1000000, 
            wrappers=[AlfredDemangler]
        )

        # reset env
        self.env = gym.make(env_id)
    
    def reset(self):
        obs, info = self.env.reset()
        obj = {
            'state':obs, 
            'admissible_actions':info['admissible_commands']
        }
        obs = Observation(
            output=json.dumps(obj),
            done=False
        )
        return obs

    def step(self, action):
        action = action.action_value
        obs, _, done, info = self.env.step(action)

        if not done:
            obj = {
                'state':obs, 
                'admissible_actions':info['admissible_commands']
            }
            obj = json.dumps(obj)
        else:
            obj = json.dumps({'state':'You Won!'})
        obs = Observation(
            output=obj,
            done=done
        )
        return obs