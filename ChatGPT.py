import openai
import os

# Set up OpenAI API key

openai.api_key = см в бот

# Define prompt and parameters for text generation
prompt = "What is the meaning of life?"
model = "text-davinci-002"
temperature = 0.7
max_tokens = 5

# Generate text
response = openai.Completion.create(
    engine=model,
    prompt=prompt,
    temperature=temperature,
    max_tokens=max_tokens
)

# Print generated text
print(response.choices[0].text)
# answer ver. - The meaning of life is an elusive question that has yet to be fully understood. The answer may never be fully known, but it can be said that the meaning of life is an attempt to find an answer to the ultimate question. There is no sure way to find an answer to the question
# answer ver. - The meaning of life is a question that has been asked by people throughout history. There is no one correct answer to this question.
