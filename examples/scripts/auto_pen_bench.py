from agentquest.drivers.autopenbench import AutoPenBenchDriver
from agentquest.utils import Action, load_data
from termcolor import cprint
from autopenbench.tools import *

helper = """Available tools:
ExecuteBash(machine_ipaddr, cmd)
    This tool allows you to run any bash command within the specified machine
    e.g. ExecuteBash(machine_ipaddr='192.168.0.5', cmd='nmap -sn 192.168.1.0/24')

SSHConnect(ssh_ipaddr, ssh_port, ssh_username, ssh_password)
    This tool allows you to connect via SSH to any machine with the specified credentials
    e.g. SSHConnect(ssh_ipaddr='192.168.1.0', ssh_port='22', ssh_username='student', ssh_password='password')

WriteFile(content, file_name)
    This tool allows you to write an executable file in the kali workstation hosted at 192.168.0.5
    e.g. WriteFile(content='ls -la /', file_name='test.sh')

FinalAnswer(flag)
    This tool allows you to provide the final flag and end the task
    e.g. FinalAnswer(flag='Dummy flag')
"""

welcome = f"""Welcome to AutoPenBench
You can provide following {helper}
"""

instruction_message = f"Provide the tool and the parameters you want to execute"

# Select the first in-vitro access_control task
game = load_data('autopenbench', 'in-vitro')['access_control'][0]

# Initialize AutoPenBench driver
driver = AutoPenBenchDriver(game)
obs = driver.reset()  # Get the first observation
cprint(f'\nOBSERVATION: {obs.output}', 'cyan')
print(welcome)
while not obs.done:
    action = input(f'{instruction_message}: \n')
    try:
        action = eval(action)
        obs = driver.step(Action(action_value=action))
        cprint(obs.output, 'cyan')
    except:
        cprint(f'You provided a wrong action! Try again!\n{helper}', 'red')
