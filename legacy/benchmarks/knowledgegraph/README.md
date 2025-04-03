# Knowledge Graph

This benchmark revolves around a knowledge graph framework designed to navigate a structured database utilizing various functions tailored for associative reasoning. The goal is to deduce answers to questions by exploring connections, relationships, and numerical attributes within the graph.

## Associative Reasoning

The reasoning type category for this benchmark is associative reasoning. It involves drawing connections or relationships between disparate pieces of information to derive conclusions. Within this benchmark, players leverage a set of tools to traverse the knowledge graph, forming associations between entities, identifying patterns, and deducing solutions by analyzing relationships and attributes.

## Rules of the Benchmark

Players aim to derive answers or conclusions to queries by navigating the knowledge graph using the provided functions and reasoning based on associations and attributes within the graph.

### How Players Engage in Associative Reasoning

Players use a series of functions specifically designed for this task:

- `get_relations(variable: var) -> list of relations`: To explore relationships of entities in the graph.
- `get_neighbors(variable: var, relation: str) -> variable`: To traverse relationships and gather linked entities based on specific relations.
- `intersection(variable1: var, variable2: var) -> variable`: To find common elements between variables of the same type, aiding in narrowing down associations.
- `get_attributes(variable: var) -> list of attributes`: This function helps to find all numerical attributes of the variable. Please only use it if the question seeks for a
superlative accumulation (i.e., argmax or argmin).
- `argmax(variable: var, attribute: str) -> variable`: Given a variable, this function returns the entity with the maximum value of the given attribute. It can only be used
after `get_attributes()` is used to find a set of viable attributes.
- `argmin(variable: var, attribute: str) -> variable`: Given a variable, this function returns the entity with the minimum value of the given attribute. It can only be used
after `get_attributes()` is used to find a set of viable attributes.
- `count(variable: var) -> int`: To quantify the number of entities associated with a variable, providing context for the scale of associations.

### Providing Final Answers

Upon deriving a conclusive solution, players should specify the answer as follows:
`FINAL ANSWER: #id` (where `id` represents the variable ID considered the final answer).
