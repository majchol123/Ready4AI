from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

# Inicjalizacja modelu
model = init_chat_model("claude-haiku-4-5", model_provider="anthropic")


# Magazyn sesji w pamięci
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        store[session_id].add_message(SystemMessage(content="Jesteś wesołym i pomocnym asystentem"))
    return store[session_id]

model_with_history = RunnableWithMessageHistory(model, get_session_history)

config = {"configurable": {"session_id": "user1"}}

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    response = model_with_history.invoke(input = user_input, config=config)
    print("Assistant:", response.content)
