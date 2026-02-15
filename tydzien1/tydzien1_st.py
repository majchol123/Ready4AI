import streamlit as st
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

# Load env from parent directory as requested
load_dotenv()

# Define the structured output model
class QuizQuestion(BaseModel):
    question: str = Field(description="Treść pytania")
    a: str = Field(description="Opcja A")
    b: str = Field(description="Opcja B")
    c: str = Field(description="Opcja C")
    d: str = Field(description="Opcja D")
    correct_answer: Literal["a", "b", "c", "d"] = Field(description="Litera poprawnej odpowiedzi (a, b, c lub d)")

def init_llm():
    # Increase temperature to 0.8 for more variety/randomness
    llm = init_chat_model("claude-haiku-4-5", model_provider="anthropic", temperature=0.8)
    return llm.with_structured_output(QuizQuestion)

def main():
    st.set_page_config(page_title="Generator Quizu AI", page_icon="❓")
    st.title("--- Generator Quizu AI ---")

    # Initialize session state to handle the app flow
    if "step" not in st.session_state:
        st.session_state.step = "setup"
        st.session_state.questions = []
        st.session_state.user_answers = []
        st.session_state.messages = []
        st.session_state.num_questions = 3
        st.session_state.topic = ""
        st.session_state.difficulty = "Średni"

    # Setup Phase
    if st.session_state.step == "setup":
        st.session_state.topic = st.text_input("Podaj tematykę quizu:", value=st.session_state.topic)
        
        col_q, col_d = st.columns(2)
        with col_q:
            st.session_state.num_questions = st.number_input("Ile pytań?", min_value=1, max_value=10, value=st.session_state.num_questions)
        with col_d:
            st.session_state.difficulty = st.radio("Poziom trudności:", ["Łatwy", "Średni", "Trudny"], index=["Łatwy", "Średni", "Trudny"].index(st.session_state.difficulty), horizontal=True)

        if st.button("Rozpocznij Quiz"):
            if not st.session_state.topic:
                st.error("Proszę podać tematykę!")
            else:
                st.session_state.step = "quiz"
                difficulty_prompt = {
                    "Łatwy": "Pytania powinny być proste, oparte na powszechnie znanych faktach.",
                    "Średni": "Pytania powinny być na umiarkowanym poziomie trudności, wymagające pewnej wiedzy.",
                    "Trudny": "Pytania powinny być bardzo trudne, niszowe, wymagające eksperckiej wiedzy lub dużej precyzji."
                }
                
                st.session_state.messages = [
                    SystemMessage(content=f"Jesteś kreatywnym twórcą quizów. Twoim zadaniem jest generowanie pytań na temat: {st.session_state.topic}. "
                                          f"Poziom trudności: {st.session_state.difficulty}. {difficulty_prompt[st.session_state.difficulty]} "
                                          f"Każde pytanie musi być unikalne. Staraj się poruszać bardzo zróżnicowane aspekty tematu: "
                                          f"zarówno fakty ogólne, niszowe ciekawostki, jak i konkretne dane techniczne lub historyczne. "
                                          f"Unikaj pytań zbyt oczywistych i upewnij się, że tylko jedna odpowiedź jest poprawna.")
                ]
                st.rerun()

    # Quiz Phase
    elif st.session_state.step == "quiz":
        current_idx = len(st.session_state.user_answers)
        
        # Guard: If all questions answered, go to results
        if current_idx >= st.session_state.num_questions:
            st.session_state.step = "results"
            st.rerun()

        # Generate question if not already in session_state
        if len(st.session_state.questions) <= current_idx:
            with st.spinner(f"Generuję pytanie {current_idx + 1}..."):
                try:
                    structured_llm = init_llm()
                    response = structured_llm.invoke(st.session_state.messages + [HumanMessage(content="Generuj kolejne pytanie.")])
                    st.session_state.questions.append(response)
                    # Add to history to avoid duplicates (same logic as CLI)
                    st.session_state.messages.append(AIMessage(content=f"Pytanie {current_idx + 1}: {response.question} (Opcje: {response.a}, {response.b}, {response.c}, {response.d}. Poprawna: {response.correct_answer})"))
                except Exception as e:
                    st.error(f"Błąd podczas generowania pytania: {e}")
                    return

        # Display current question
        q = st.session_state.questions[current_idx]
        st.subheader(f"Pytanie {current_idx + 1} z {st.session_state.num_questions}")
        st.markdown(f"### {q.question}")
        
        # Use radio buttons for options
        answer = st.radio("Wybierz odpowiedź:", 
                          options=["a", "b", "c", "d"], 
                          format_func=lambda x: f"{x.upper()}) {getattr(q, x)}",
                          key=f"q_{current_idx}")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            button_label = "Następne" if current_idx < st.session_state.num_questions - 1 else "Zakończ"
            if st.button(button_label, type="primary"):
                st.session_state.user_answers.append(answer)
                st.rerun()

    # Results Phase
    elif st.session_state.step == "results":
        st.header("KONIEC QUIZU")
        
        correct_count = 0
        incorrect_questions = []
        
        for idx, (q, user_ans) in enumerate(zip(st.session_state.questions, st.session_state.user_answers)):
            if user_ans == q.correct_answer:
                correct_count += 1
            else:
                incorrect_questions.append((idx + 1, q, user_ans))
        
        if correct_count == len(st.session_state.questions):
            st.balloons()
        
        st.metric("Twój wynik", f"{correct_count} / {len(st.session_state.questions)}")
        
        if incorrect_questions:
            st.subheader("Podsumowanie błędnych odpowiedzi:")
            for num, q, ans in incorrect_questions:
                with st.expander(f"Pytanie {num}: {q.question}"):
                    st.write(f"Twoja odpowiedź: **{ans.upper()}**")
                    st.write(f"Poprawna odpowiedź: **{q.correct_answer.upper()}** ({getattr(q, q.correct_answer)})")
        else:
            st.success("Brawo! Wszystkie odpowiedzi poprawne!")

        if st.button("Zacznij nowy quiz"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
