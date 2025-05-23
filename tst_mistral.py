import os

from mistralai import Mistral, UserMessage

os.environ["MISTRAL_API_KEY"] = "ELCHNSVzP5eRkZPCXejfMDVryanviNmV"
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

messages = [
    {
        "role": "user",
        "content": "What is the best French cheese?",
    },
]
# Or using the new message classes
# messages = [
#     UserMessage(content="What is the best French cheese?"),
# ]

chat_response = client.chat.complete(
    model=model,
    messages=messages,
)

print(chat_response.choices[0].message.content)

