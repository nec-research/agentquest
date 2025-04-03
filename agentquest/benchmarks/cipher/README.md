# Cipher
AgentQuest Cipher is a benchmark where you can test an agent's deciphering capabilities against various classical ciphers. The agent's job is to decipher a ciphertext given only the name of encryption algorithm without the encryption parameters.

## AgentQuest Implementation of Cipher

Agentquest provides a small dataset of 115 synthetically generated meaningful plaintext sentences. On average each sentence has 223 characters. An agent is benchmarked by providing cipher texts produced by encrypting these plaintexts against various supported cipher algorithms with random parameters.

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                        |
| ------------------- | ----------- | -------- | ------------------------------------------------------------------------------------------------------ |
| **State**           | value       | str      | Last guess input to the benchmark                                                                      |
| **Action**          | value       | str      | Guess text                                                                                           |
| **Observation**     | output      | str      | Feedback to the agent by the benchmark (if the guess text matches the original plain text or not.)                                                             |
|                     | success     | bool     | True, if target plain text is guessed correctly, False otherwise                                            |
|                     | can_proceed | bool     | True, if further guesses can be made, False otherwise                                                   |
| **Repetition Rate** | -           | float    | Metric on how guessed texts (actions) are repeated. Based on Levenshtein ratio of two guess texts. |
| **Progress Rate**   | -           | float    | Levenshtein ratio between a guess text with the original plain text (goal)|

### Running Cipher with agentquest

```python
from agentquest.benchmarks.cipher import CipherAction, CipherDriver, CipherUtils
data = CipherUtils.load_data()

driver = CipherDriver(goal=data[0], algorithm="caesar", match_threshold=0.90)
obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input() # Replace with agent call
    obs = driver.step(CipherAction(value=human_input))
    print(obs.output)
```
When initializing the driver, the argument `goal` is the original plain text in string. The `algorithm` argument allows user to choose from one of the six cipher algorithms supported. The values can be `caesar`, `atbash`, `affine`, `vigenere`, `railfence` and `adfgvx`. `match_threshold` is the parameter which is used to determine if a task is completed. When an agent tries to decipher a cipher text, there can be some characters missing here and there, but still if there is large match between original text and deciphered text we can consider the text deciphered. So, everytime the `step` function is called, the agent's output guess text is compared with original plain text and Levenshtein ratio is calculated. If this ratio is greater than the `match_threshold`, then we consider the deciphering task completed and the observation object will have `success` attribute True.


The `reset()` method initializes the Cipher game (encrypts the plaintext with provided algorithm) and gives the agent instructions about the game. Here is the initial instruction for a Cipher game instance.

```
You are a deciphering agent. Your task is to decipher a ciphertext produced from a Caesar cipher and return meaningful plain text. Caesar cipher is a type of substitution cipher in which each alphabetical letter in the plaintext is replaced by a letter some fixed number of position shifts down the alphabet. The shift can be either left shift of right shift. The plain texts are always meaningful sentences in English language.
Here is the cipher text to decrypt:
Ocz nft rvn kvdiozy di cpzn ja jmvibz viy kdif vn ocz npi ydkkzy wzgjr ocz cjmduji. Wdmyn agzr di kzmazxo ajmhvodji, oczdm ntixcmjiduzy hjqzhzion v hvmqzg oj wzcjgy. Zqzidib wmjpbco v xjjg wmzzuz, hvfdib ocz hjhzio azzg hvbdxvg.
Your response must be in the following format:
Plain Text: <decrypted_text>
```

While, the example code above shows human input, an LLM agent is expected to produce an output in the format `Plain text: <decrypted_text>` according to the instruction. This can be parsed by the developer manually and `step` method can be called with `CipherAction` object. Another option is to call the `step_raw` method which can take the raw agent output in string format, parse it and call `step` method out of the box.

The `step` method call advances the game forward with agent's input (action) and benchmark provides feedback to the action (observation).

```python
obs = driver.step_raw(
    "Plain text: The sky was panted in hues of orange and pink as the sun dipped below the horizon. Birds flew in perfect formation, their synchronized movements a marvel to behold. Evening brought a cool breeze, making the. moment feel magicals."
)
print(obs.output)
```

The step_raw method calls a parser with regex that parses the agent's output searching for `Plain text: <decrypted_text>`. The developer can pass their own custom parser to step_raw method. Also, the developers are free to process the initial observation output and send it to their agents as they prefer.

Observation output for a `step` method call with above plain text value is as follows.

```
You've won !!!. Cipher text successfully decrypted.
```

If the provided text was wrong, the feedback would have been as follows.

```
Wrong answer!!! The text does not match with the original plain text. Try again.
```

See `example.ipynb` for the example code to see how to run Cipher benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

Metrics output example for an instance of Cipher game in AgentQuest:

```python
{'algorithm': 'caesar',
 'cipher_text': 'Pda ogu swo lwejpaz ej dqao kb knwjca wjz lejg wo pda oqj zellaz xahks pda dknevkj. Xenzo bhas ej lanbayp bkniwpekj, pdaen oujydnkjevaz ikraiajpo w iwnrah pk xadkhz. Arajejc xnkqcdp w ykkh xnaava, iwgejc pda ikiajp baah iwceywh.',
 'algorithm_parameters': {'shift': 4, 'shift_direction': 'left'},
 'match_threshold': 0.9,
 'goal': 'The sky was painted in hues of orange and pink as the sun dipped below the horizon. Birds flew in perfect formation, their synchronized movements a marvel to behold. Evening brought a cool breeze, making the moment feel magical.',
 'success': False,
 'actions': [{'value': 'the sky was panted in hues of orange and pink as the sun dipped below the horizon. birds flew in perfect formation, their synchronized movements a marvel to behold. evening brought a cool breeze, making the. moment feel magicals.'}],
 'states': [{'value': 'the sky was panted in hues of orange and pink as the sun dipped below the horizon. birds flew in perfect formation, their synchronized movements a marvel to behold. evening brought a cool breeze, making the. moment feel magicals.'}],
 'observations': [{'output': "You've won !!!. Cipher text successfully decrypted.",
   'success': True,
   'can_proceed': False}],
 'repetition_rate': 0.0,
 'progress': [0.98]}
```

The metrics records not just the action, states, observation values but also the cipher algorithm and parameters used for encryption.

#### Progress Rate for Cipher

Progress rate signifies how far an agent has reached in solving the goal. For Cipher, it is the levenshtein ratio between an agent's last guess and original plain text (goal).

#### Repetition Rate for Cipher

Repetition rate quantifies how actions are repeated in solving a task. To calculate repetition rate for Cipher, similarity scores is calculated between two Cipher actions using Levenshtein ratio. Then, the repetition rate is calculated based on this similarity score as explained in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_).


## Supported Ciphers
Agentquest Cipher benchmark supports 6 classical ciphers.

### 1. Caesar Cipher
[Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher). It is one of the simplest encryption techniques in which a plain text message is transformed into encrypted text message by shifting the alphabets by certain number of positions. For example if the plain text is "apple", with right shift of 1 the encrypted text is "bqqmf". Notice that each letter is mapped to shifted alphabet set.

Mathematically, it can be represented by modular arithmetic if we represent A --> 0, B --> 1, ..., Z --> 25, encryption of a letter x by a shift of n is represented as follows:
```
E_n(x) = (x + n) mod 26
```
Decryption is performed similarly as follows:
```
D_n(x) = (x - n) mod 26
```

Here are similar brief markdown documents for the requested ciphers:

### 2. Affine Cipher
[Affine cipher](https://en.wikipedia.org/wiki/Affine_cipher) is a type of substitution cipher where each letter in an alphabet is mapped to its numeric equivalent, encrypted using a mathematical function, and then converted back to a letter. The encryption function is defined as:
```
E(x) = (a*x + b) mod 26
```
Here, `a` and `b` are keys of the cipher, where `a` must be coprime to 26 to ensure the cipher is reversible. Decryption is performed using:
```
D(y) = a_inv * (y - b) mod 26
```
Where `a_inv` is the modular multiplicative inverse of `a` modulo 26.

### 3. Atbash Cipher
[Atbash cipher](https://en.wikipedia.org/wiki/Atbash) is a substitution cipher where each letter is replaced with its reverse counterpart in the alphabet. For example, A becomes Z, B becomes Y, and so on.
- Plaintext: "HELLO"
- Ciphertext: "SVOOL"
This cipher is a simple monoalphabetic substitution cipher with no key, making it easy to decipher.

### 4. Vigenère Cipher
[Vigenère cipher](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher) is a polyalphabetic substitution cipher that uses a keyword to determine the shift for each letter. Encryption is performed as:
```
E(x_i) = (x_i + k_i) mod 26
```
Where `x_i` is the position of the plaintext letter, and `k_i` is the position of the corresponding keyword letter. Decryption is performed as:
```
D(y_i) = (y_i - k_i) mod 26
```
For example, with plaintext "ATTACKATDAWN" and keyword "LEMON", the ciphertext becomes "LXFOPVEFRNHR".

### 5. Railfence Cipher
[Railfence cipher](https://en.wikipedia.org/wiki/Rail_fence_cipher) is a transposition cipher where plaintext letters are written diagonally across rows (rails), then read off row by row to create the ciphertext.

For example:
- Plaintext: "HELLOWORLD"
- Rails: 3
  ```
  H . . . O . . . L .
  . E . L . W . R . D
  . . L . . . O . . .
  ```
- Ciphertext: "HOLELWRDLO"

### 6. ADFGVX Cipher
[ADFGVX cipher](https://en.wikipedia.org/wiki/ADFGVX_cipher) is a field cipher used in WWI by the German army. It combines a substitution cipher and transposition cipher. The steps are:
1. Substitution: A Polybius square encrypts plaintext into the letters A, D, F, G, V, and X.
2. Transposition: The resulting ciphertext is rearranged based on a keyword.

