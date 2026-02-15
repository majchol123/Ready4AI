import streamlit as st
import requests
import os
from schemas import QuizQuestion, QuizConfig

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def start_quiz_session(topic: str, num_questions: int, difficulty: str):
    config = QuizConfig(topic=topic, num_questions=num_questions, difficulty=difficulty)
    try:
        response = requests.post(f"{BACKEND_URL}/start", json=config.model_dump())
        response.raise_for_status()
        return response.json()["session_id"]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {e}")
        return None

def get_next_question(session_id: str):
    try:
        response = requests.post(f"{BACKEND_URL}/quiz", json={"session_id": session_id})
        response.raise_for_status()
        return QuizQuestion(**response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching question: {e}")
        return None

def cleanup_session(session_id: str):
    if not session_id:
        return
    try:
        requests.delete(f"{BACKEND_URL}/cleanup/{session_id}")
    except:
        pass

def main():
    st.set_page_config(page_title="Generator Quizu AI", page_icon="📝")
    st.title("--- Generator Quizu AI (Backend/Frontend) ---")

    if "step" not in st.session_state:
        st.session_state.step = "setup"
        st.session_state.session_id = None
        st.session_state.questions = []
        st.session_state.user_answers = []
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
                session_id = start_quiz_session(st.session_state.topic, st.session_state.num_questions, st.session_state.difficulty)
                if session_id:
                    st.session_state.session_id = session_id
                    st.session_state.step = "quiz"
                    st.rerun()

    # Quiz Phase
    elif st.session_state.step == "quiz":
        current_idx = len(st.session_state.user_answers)
        
        # Check completion
        if current_idx >= st.session_state.num_questions:
            st.session_state.step = "results"
            st.rerun()

        # Fetch question if needed
        if len(st.session_state.questions) <= current_idx:
            with st.spinner(f"Generuję pytanie {current_idx + 1}..."):
                q = get_next_question(st.session_state.session_id)
                if q:
                    st.session_state.questions.append(q)
                else:
                    st.stop() # Stop if failed to get question

        # Display Question
        q = st.session_state.questions[current_idx]
        st.subheader(f"Pytanie {current_idx + 1} z {st.session_state.num_questions}")
        st.markdown(f"### {q.question}")
        
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
            cleanup_session(st.session_state.session_id)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
