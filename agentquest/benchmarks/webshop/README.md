# Webshop

Webshop: Aligning Text and Embodied Environments for Interactive Learning (Shridhar et al.)

Link to Webshop Paper: https://arxiv.org/pdf/2207.01206

Link to Webshop Website: https://webshop-pnlp.github.io/

**Description (from Webshop github repo)**: WebShop is a simulated e-commerce website environment with 1.18 million real-world products and 12,087 crowd-sourced text instructions. In this environment, an agent needs to navigate multiple types of webpages and issue diverse actions to find, customize, and purchase a product given an instruction. WebShop provides several challenges including understanding compositional instructions, query (re-)formulation, dealing with noisy text in webpages, and performing strategic exploration.

### About Webshop

Webshop consists of tasks in which the goal is to find the item in Webshop which matches the task description and buy it. There are two versions of Webshop, web version and text version using gym. In AgentQuest, we shall use the text version of Webshop to benchmark the agent.

## Webshop in AgentQuest

AgentQuest wraps the text interface of Webshop and provides an easy method to benchmark your agent with Webshop. Webshop [version commit: 64fa2a5](https://github.com/princeton-nlp/WebShop/commit/64fa2a5c15c7daa698b9ac93f5bb5437b634c9bd) is used in this version of AgentQuest installed by cloning the Webshop git repo.

Since, WebShop project uses python packages which are quite old, we install WebShop in a separate virtual environment to that of AgentQuest to avoid dependency conflicts. Then we wrap the WebShop's text environment with a simple API in flask which can be called to call the reset and step functions for WebShop. See the `interface.py` file. This API running in port 5555 in localhost allows AgentQuest to interact with Webshop.

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                                                          |
| ------------------- | ----------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **State**           | value       | json     | The response json object received from Webshop's interface api from last step or reset call.                                             |
| **Action**          | value       | str      | Agent action to Webshop environment to move forward the game or carry out the task. This is either 'search[...]' or 'click[...]' action. |
| **Observation**     | output      | str      | Feedback to the agent by Webshop's environment. Also, includes a list of available actions.                                              |
|                     | success     | bool     | True if task has been completed successfully, False otherwise.                                                                           |
|                     | can_proceed | bool     | True if game can still be played, False otherwise. In Webshop, it is always opposite to success.                                         |
| **Repetition Rate** | -           | float    | Rate to quantify the repetitions of actions. Based on levenshtein ratio between action values.                                           |
| **Progress Rate**   | -           | float    | The reward number obtained from Webshop's environment, after an item is bought for a task.                                               |

### Installation

For webshop, create a new directory `webshop`. Then download [setup.sh](setup.sh) and [interface.py](interface.py) scripts into the directory.

```
pip install agentquest
# Download setup script and interface.py script
bash ./setup.sh
```

The setup.sh clones the github repo for WebShop, creates a new python virtual environment _.webshop-venv_, installs necessary python packages in this virtual environment and downloads files for Webshop. By default, the installation downloads and indexes data for a smaller version of Webshop with 1000 items. This can be changed by modifying the _setup.sh_ file where it runs the _WebShop/setup.sh_ (See WebShop's documentation on how to do so).

### Usage

#### Start Webshop Interface API server

Make sure the interface script is run in the parent directory to the WebShop repo directory.

```bash
source .webshop-env/bin/activate
python interface.py
```

#### AgentQuest's Benchmarking Part

```python
from agentquest.benchmarks.webshop import WebshopDriver, WebshopUtils, WebshopAction

driver = WebshopDriver(base_url="http://localhost:5555")
obs = driver.reset()

print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input()
    obs = driver.step(WebshopAction(value=human_input))
    # obs = driver.step_raw(human_input)
    print(obs.output)

```

Calling the `reset()` method initializes an instance of Webshop problem in the gym environment and provides the description about the problem, as well as the possible available actions.

```
Welcome to WebShop, a simulated e-commerce website environment. Your goal is to find and buy the best product matching the instruction provided.
There are two possible actions `search[<query>]` and `click[<clickable>]`. These actions will help you navigate through the WebShop environment. The list of possible actions and clickables are provided in the observation output after every action.
Your output should in the following format:
Action: <action>
WebShop [SEP] Instruction: [SEP] Find me slim fit, machine wash women's jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 40.00 dollars [SEP] Search
Available actions in json:
{"clickables": ["search"], "has_search_bar": true}
```

The `step()` method call, progresses the game one step further. The Webshop environment provides feedback for a command. An example of a step() method's observation for command `search[women jumpsuits]`

```
Instruction: [SEP] Find me slim fit, machine wash women's jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B09NDS8F4V [SEP] AODONG Onesie Pajamas for Women Onesies Romper Pajamas Printed Bodycon Jumpsuit Shorts Sexy One Piece Pjs Overall [SEP] $2.99 to $7.99 [SEP] B09PVNLVRW [SEP] Women's V-Neck Rompers Printed Jumpsuit Long Sleeve Homewear Butt Flap Pajamas One-Piece Onesies Nightwear Sexy Bodysuit [SEP] $17.4 to $28.67 [SEP] B09RV4TXKJ [SEP] ORT Bodycon Lingeries for Women,2 Piece 2 pc Sleepwear for Women,Sexy Printed Ugly Valentine Nightdress Loungewear Lingeries Rompers Clubwear [SEP] $13.08 [SEP] B099WX3CV5 [SEP] Women Aesthetic Short Sleeve Jumpsuit Bodycon Sexy V Neck Button Shorts Rompers Knitted One Piece Bodysuit Overall [SEP] $13.99 to $24.89 [SEP] B09Q37JQZ6 [SEP] Women's Sexy Swimsuit One Piece High Neck Halter Bikini Floral Stiching See Through Monokini Tummy Control Beachwear [SEP] $10.99 to $18.99 [SEP] B09QPX97VW [SEP] Sandals For Women Gold Sandals Slippers Sandy From Grease Red Shoes Strap Platforms Golf Shoes Jeans Stretch Short Sleeve Shirts Midi Skirts Women Suede Pumps [SEP] $100.0 [SEP] B09NSC5VDG [SEP] CofeeMO Womens Lingerie Sleep Lounge Everyday Nursing Bras Printed Underwear Seamless Printed Bralette for Sex Naughty Play [SEP] $14.99 [SEP] B09QGK5XHZ [SEP] WENKOMG1 Men's Long Sleeve Undershirt with Mask Turtleneck Hooded T-Shirt Solid Color Workout Tops Zipper Side Slit Shirts Slim Fit Sweatshirt Spring/Summer Tee Shirts(Gray,) [SEP] $8.39 [SEP] B09S632DT3 [SEP] Sleepwear Womens Chemise Nightgown Full Slip Lace Lounge Dress with Briefs Mesh Chemise V Neck Soft Pajama Dress Nightdress [SEP] $11.99 to $14.99 [SEP] B09QXF3V3X [SEP] DEUVOUM Summer Trend Mesh Shoes Men's Sports Shoes Solid Color Lace-Up Sneakers Fashion All-Match Walking Shoes Outdoor Hiking Shoes Non-Slip Shock-Absorbing Casual Sports Shoes [SEP] $100.0
Available actions in json
{"clickables": ["back to search", "next >", "b09nds8f4v", "b09pvnlvrw", "b09rv4txkj", "b099wx3cv5", "b09q37jqz6", "b09qpx97vw", "b09nsc5vdg", "b09qgk5xhz", "b09s632dt3", "b09qxf3v3x"], "has_search_bar": false}
```

AgentQuest adds the response format at the end of the problem, so that the agent's output can be easily parsed using `step_raw` method. Developers are free to cut this part out or even send a custom parser to `step_raw` method.

```python
# dummy_agent_output = "Here is the action. Action: search[men t-shirts]" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

Here is the metrics output example for an instance of Webshop game in AgentQuest.

```python
{'goal': "WebShop [SEP] Instruction: [SEP] Find me slim fit, machine wash women's jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Search",
 'success': False,
 'actions': [{'value': 'search[women jumpsuits]'},
  {'value': 'click[b09qgk5xhz]'},
  {'value': 'click[buy now]'}],
 'states': [{'value': {'available_actions': {'clickables': ['back to search',
      'next >',
      'b09nds8f4v',
      'b09pvnlvrw',
      'b09rv4txkj',
      'b099wx3cv5',
      'b09q37jqz6',
      'b09qpx97vw',
      'b09nsc5vdg',
      'b09qgk5xhz',
      'b09s632dt3',
      'b09qxf3v3x'],
     'has_search_bar': False},
    'done': False,
    'info': None,
    'obs': "Instruction: [SEP] Find me slim fit, machine wash women's jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B09NDS8F4V [SEP] AODONG Onesie Pajamas for Women Onesies Romper Pajamas Printed Bodycon Jumpsuit Shorts Sexy One Piece Pjs Overall [SEP] $2.99 to $7.99 [SEP] B09PVNLVRW [SEP] Women's V-Neck Rompers Printed Jumpsuit Long Sleeve Homewear Butt Flap Pajamas One-Piece Onesies Nightwear Sexy Bodysuit [SEP] $17.4 to $28.67 [SEP] B09RV4TXKJ [SEP] ORT Bodycon Lingeries for Women,2 Piece 2 pc Sleepwear for Women,Sexy Printed Ugly Valentine Nightdress Loungewear Lingeries Rompers Clubwear [SEP] $13.08 [SEP] B099WX3CV5 [SEP] Women Aesthetic Short Sleeve Jumpsuit Bodycon Sexy V Neck Button Shorts Rompers Knitted One Piece Bodysuit Overall [SEP] $13.99 to $24.89 [SEP] B09Q37JQZ6 [SEP] Women's Sexy Swimsuit One Piece High Neck Halter Bikini Floral Stiching See Through Monokini Tummy Control Beachwear [SEP] $10.99 to $18.99 [SEP] B09QPX97VW [SEP] Sandals For Women Gold Sandals Slippers Sandy From Grease Red Shoes Strap Platforms Golf Shoes Jeans Stretch Short Sleeve Shirts Midi Skirts Women Suede Pumps [SEP] $100.0 [SEP] B09NSC5VDG [SEP] CofeeMO Womens Lingerie Sleep Lounge Everyday Nursing Bras Printed Underwear Seamless Printed Bralette for Sex Naughty Play [SEP] $14.99 [SEP] B09QGK5XHZ [SEP] WENKOMG1 Men's Long Sleeve Undershirt with Mask Turtleneck Hooded T-Shirt Solid Color Workout Tops Zipper Side Slit Shirts Slim Fit Sweatshirt Spring/Summer Tee Shirts(Gray,) [SEP] $8.39 [SEP] B09S632DT3 [SEP] Sleepwear Womens Chemise Nightgown Full Slip Lace Lounge Dress with Briefs Mesh Chemise V Neck Soft Pajama Dress Nightdress [SEP] $11.99 to $14.99 [SEP] B09QXF3V3X [SEP] DEUVOUM Summer Trend Mesh Shoes Men's Sports Shoes Solid Color Lace-Up Sneakers Fashion All-Match Walking Shoes Outdoor Hiking Shoes Non-Slip Shock-Absorbing Casual Sports Shoes [SEP] $100.0",
    'reward': 0.0}},
  {'value': {'available_actions': {'clickables': ['back to search',
      '< prev',
      'description',
      'features',
      'reviews',
      'buy now'],
     'has_search_bar': False},
    'done': False,
    'info': None,
    'obs': "Instruction: [SEP] Find me slim fit, machine wash women's jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Back to Search [SEP] < Prev [SEP] WENKOMG1 Men's Long Sleeve Undershirt with Mask Turtleneck Hooded T-Shirt Solid Color Workout Tops Zipper Side Slit Shirts Slim Fit Sweatshirt Spring/Summer Tee Shirts(Gray,) [SEP] Price: $8.39 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now",
    'reward': 0.0}},
  {'value': {'available_actions': {'clickables': [], 'has_search_bar': False},
    'done': True,
    'info': None,
    'obs': 'Thank you for shopping with us! [SEP] Your code: [SEP] None [SEP] (Paste it in your MTurk interface.) [SEP] Purchased [SEP] asin [SEP] B09QGK5XHZ [SEP] options [SEP] {} [SEP] attrs [SEP] None [SEP] category [SEP] None [SEP] query [SEP] None [SEP] product category [SEP] None [SEP] Target [SEP] asin [SEP] options [SEP] attrs [SEP] price upper [SEP] instuction text [SEP] category [SEP] product category [SEP] query [SEP] Goal [SEP] None [SEP] Reward [SEP] Your score (min 0.0, max 1.0) [SEP] 0.03333333333333333 [SEP] Reward Details [SEP] None',
    'reward': 0.03333333333333333}}],
 'observations': [{'output': 'Instruction: [SEP] Find me slim fit, machine wash women\'s jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B09NDS8F4V [SEP] AODONG Onesie Pajamas for Women Onesies Romper Pajamas Printed Bodycon Jumpsuit Shorts Sexy One Piece Pjs Overall [SEP] $2.99 to $7.99 [SEP] B09PVNLVRW [SEP] Women\'s V-Neck Rompers Printed Jumpsuit Long Sleeve Homewear Butt Flap Pajamas One-Piece Onesies Nightwear Sexy Bodysuit [SEP] $17.4 to $28.67 [SEP] B09RV4TXKJ [SEP] ORT Bodycon Lingeries for Women,2 Piece 2 pc Sleepwear for Women,Sexy Printed Ugly Valentine Nightdress Loungewear Lingeries Rompers Clubwear [SEP] $13.08 [SEP] B099WX3CV5 [SEP] Women Aesthetic Short Sleeve Jumpsuit Bodycon Sexy V Neck Button Shorts Rompers Knitted One Piece Bodysuit Overall [SEP] $13.99 to $24.89 [SEP] B09Q37JQZ6 [SEP] Women\'s Sexy Swimsuit One Piece High Neck Halter Bikini Floral Stiching See Through Monokini Tummy Control Beachwear [SEP] $10.99 to $18.99 [SEP] B09QPX97VW [SEP] Sandals For Women Gold Sandals Slippers Sandy From Grease Red Shoes Strap Platforms Golf Shoes Jeans Stretch Short Sleeve Shirts Midi Skirts Women Suede Pumps [SEP] $100.0 [SEP] B09NSC5VDG [SEP] CofeeMO Womens Lingerie Sleep Lounge Everyday Nursing Bras Printed Underwear Seamless Printed Bralette for Sex Naughty Play [SEP] $14.99 [SEP] B09QGK5XHZ [SEP] WENKOMG1 Men\'s Long Sleeve Undershirt with Mask Turtleneck Hooded T-Shirt Solid Color Workout Tops Zipper Side Slit Shirts Slim Fit Sweatshirt Spring/Summer Tee Shirts(Gray,) [SEP] $8.39 [SEP] B09S632DT3 [SEP] Sleepwear Womens Chemise Nightgown Full Slip Lace Lounge Dress with Briefs Mesh Chemise V Neck Soft Pajama Dress Nightdress [SEP] $11.99 to $14.99 [SEP] B09QXF3V3X [SEP] DEUVOUM Summer Trend Mesh Shoes Men\'s Sports Shoes Solid Color Lace-Up Sneakers Fashion All-Match Walking Shoes Outdoor Hiking Shoes Non-Slip Shock-Absorbing Casual Sports Shoes [SEP] $100.0\nAvailable actions in json\n{"clickables": ["back to search", "next >", "b09nds8f4v", "b09pvnlvrw", "b09rv4txkj", "b099wx3cv5", "b09q37jqz6", "b09qpx97vw", "b09nsc5vdg", "b09qgk5xhz", "b09s632dt3", "b09qxf3v3x"], "has_search_bar": false}',
   'success': False,
   'can_proceed': True},
  {'output': 'Instruction: [SEP] Find me slim fit, machine wash women\'s jumpsuits, rompers & overalls with short sleeve, high waist, polyester spandex for daily wear with color: green stripe, and size: large, and price lower than 50.00 dollars [SEP] Back to Search [SEP] < Prev [SEP] WENKOMG1 Men\'s Long Sleeve Undershirt with Mask Turtleneck Hooded T-Shirt Solid Color Workout Tops Zipper Side Slit Shirts Slim Fit Sweatshirt Spring/Summer Tee Shirts(Gray,) [SEP] Price: $8.39 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now\nAvailable actions in json\n{"clickables": ["back to search", "< prev", "description", "features", "reviews", "buy now"], "has_search_bar": false}',
   'success': False,
   'can_proceed': True},
  {'output': 'Thank you for shopping with us! [SEP] Your code: [SEP] None [SEP] (Paste it in your MTurk interface.) [SEP] Purchased [SEP] asin [SEP] B09QGK5XHZ [SEP] options [SEP] {} [SEP] attrs [SEP] None [SEP] category [SEP] None [SEP] query [SEP] None [SEP] product category [SEP] None [SEP] Target [SEP] asin [SEP] options [SEP] attrs [SEP] price upper [SEP] instuction text [SEP] category [SEP] product category [SEP] query [SEP] Goal [SEP] None [SEP] Reward [SEP] Your score (min 0.0, max 1.0) [SEP] 0.03333333333333333 [SEP] Reward Details [SEP] None\nAvailable actions in json\n{"clickables": [], "has_search_bar": false}',
   'success': True,
   'can_proceed': False}],
 'repetition_rate': 0.0,
 'progress': [0.0, 0.0, 0.03333333333333333]}
```

#### Progress Rate for Webshop

Progress rate signifies how far an agent has reached in solving the goal. For Webshop, we don't have access to the internal states of the gym, but instead we use the reward value returned by the Webshop text environment. But this only applies after an item is bought, which acts as a metric to quantify how good the purchase was for a task.
Look at section 3.1 in the [paper](https://arxiv.org/pdf/2207.01206) for **Instruction and Reward**.

Since there are no clear milestones in buying a product, progress rate for all the intermediates are kept zero.

#### Repetition Rate for Webshop

For Webshop, the commands are the action inputs. To calculate repetition rate, we count how many times a command has been repeated, using Levenshtein distance.

The arguments passed as dictionary in `export()` method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
