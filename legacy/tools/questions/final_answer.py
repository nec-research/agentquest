from pydantic import BaseModel, Field

answer_prompt = """You are a generative agent.
Given a question and the relative answer, check if the guessed answer is correct or not.

Question: {question}
Answer: {answer}

Guess: {guess}
"""


class CheckCorrect(BaseModel):
    is_correct: bool = Field(...)


class FinalAnswer(BaseModel):
    """Provide the final answer to a question."""

    answer: str = Field(...)

    def check(self, question, answer, llm):
        system_prompt = answer_prompt.format(
            question=question, answer=answer, guess=self.answer
        )
        out = llm.invoke(response_model=CheckCorrect, system_prompt=system_prompt)

        return out


# llm = LLMClient(OPENAI_KEY, model='gpt-4o')
# tool = FinalAnswer(answer='three studio albums')
# output = tool.check(
#    question=game['question'],
#    answer=game['final_answer'],
#    llm=llm
# )
#
# print(output.is_correct)
