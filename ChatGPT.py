import openai
import os

# Set up OpenAI API key
from envparse import Env

env = Env()
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class OpenAIWrapper:

    def __init__(self):
        self.model = "text-davinci-003"
        self.temperature = 0.9
        self.max_tokens = 256
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.6
        self.stop = ["\n", " Human:", " AI:"]

    def get_answer(self, prompt):
        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens#,
            #top_p=self.top_p,
            # frequency_penalty=self.frequency_penalty,
            # presence_penalty=self.presence_penalty
        )
        return response['choices'][0]['text']

# oai = OpenAIWrapper()
# prompt = "Сколько рогов у коровы?:"
# print(f'Тестовый вопрос: {prompt}')
# print(f'Тестовый ответ: {oai.get_answer(prompt)}')

#  -------------- examples
# import openai
# import os
#
# # Set up OpenAI API key
# from envparse import Env
#
# env = Env()
# OPENAI_KEY = env.str("OPENAI_KEY")
# openai.api_key = OPENAI_KEY

# # Define prompt and parameters for text generation
# prompt = "What is the meaning of life?"
# model = "text-davinci-002"
# temperature = 0.7
# max_tokens = 50
#
# # Generate text
# response = openai.Completion.create(
#     engine=model,
#     prompt=prompt,
#     temperature=temperature,
#     max_tokens=max_tokens
# )
#
# # Print generated text
# print(response.choices[0].text)
# answer ver. - The meaning of life is an elusive question that has yet to be fully understood. The answer may never be fully known, but it can be said that the meaning of life is an attempt to find an answer to the ultimate question. There is no sure way to find an answer to the question
# answer ver. - The meaning of life is a question that has been asked by people throughout history. There is no one correct answer to this question.
# answer ver. - There is much debate over what the meaning of life is, or whether it exists at all. Unfortunately, I cannot answer this question definitively.
# ----------- end examples
