from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model("claude-haiku-4-5", model_provider="anthropic")

messages = [
    SystemMessage("Jesteś wesołym i pomocnym asystentem")
]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit" or user_input.lower() == "quit" or user_input.lower() == "q":
        break
    messages.append(HumanMessage(content=user_input))
    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))
    print("Assistant:", response.content)

