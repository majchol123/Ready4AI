from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import uuid
import os
from typing import Dict

from schemas import QuizQuestion, QuizConfig

load_dotenv()

app = FastAPI(title="Quiz AI Backend")

# Session Store
store: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Initialize LLM
llm = init_chat_model(
    os.getenv("LLM_MODEL"),
    model_provider=os.getenv("LLM_PROVIDER"),
    temperature=float(os.getenv("LLM_TEMPERATURE"))
)
# Initialize LLM with tools
llm_with_tools = llm.bind_tools([QuizQuestion])

# Chain with History
chain_with_history = RunnableWithMessageHistory(
    llm_with_tools,
    get_session_history
)

@app.post("/start")
async def start_quiz(config: QuizConfig):
    session_id = str(uuid.uuid4())
    
    # Initialize history
    history = get_session_history(session_id)
    history.clear() # Ensure clean start
    
    difficulty_prompt = {
        "Łatwy": "Pytania powinny być proste, oparte na powszechnie znanych faktach.",
        "Średni": "Pytania powinny być na umiarkowanym poziomie trudności, wymagające pewnej wiedzy.",
        "Trudny": "Pytania powinny być bardzo trudne, niszowe, wymagające eksperckiej wiedzy lub dużej precyzji."
    }
    
    system_msg = (
        f"Jesteś kreatywnym twórcą quizów. Twoim zadaniem jest generowanie pytań na temat: {config.topic}. "
        f"Poziom trudności: {config.difficulty}. {difficulty_prompt.get(config.difficulty, '')} "
        f"Każde pytanie musi być unikalne. Poruszaj bardzo zróżnicowane aspekty tematu. "
        f"Unikaj pytań zbyt oczywistych i upewnij się, że tylko jedna odpowiedź jest poprawna."
    )
    
    # Add system message to history
    history.add_message(SystemMessage(content=system_msg))
    
    return {"session_id": session_id, "message": "Quiz initialized"}

class QuestionRequest(BaseModel):
    session_id: str

@app.post("/quiz", response_model=QuizQuestion)
async def get_question(req: QuestionRequest):
    if req.session_id not in store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Invoke chain - returns AIMessage
    msg = chain_with_history.invoke(
        [HumanMessage(content="Generuj kolejne pytanie.")],
        config={"configurable": {"session_id": req.session_id}}
    )

    # Handle history and parsing
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        
        # Add ToolMessage to satisfy API requirements (especially Anthropic)
        tool_msg = ToolMessage(
            tool_call_id=tool_call["id"],
            content="Parsed successfully"
        )
        get_session_history(req.session_id).add_message(tool_msg)
        
        # Return clean QuizQuestion instance
        return QuizQuestion(**tool_call["args"])
    
    raise HTTPException(status_code=500, detail="Model failed to generate structured output")

@app.delete("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    if session_id in store:
        del store[session_id]
        return {"message": "Session cleared"}
    return {"message": "Session not found or already cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
