from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

# Define the structured output model
class QuizQuestion(BaseModel):
    question: str = Field(description="Treść pytania")
    a: str = Field(description="Opcja A")
    b: str = Field(description="Opcja B")
    c: str = Field(description="Opcja C")
    d: str = Field(description="Opcja D")
    correct_answer: Literal["a", "b", "c", "d"] = Field(description="Litera poprawnej odpowiedzi (a, b, c lub d)")

def main():
    # Initialize the model
    # Note: Using the model name from lc1.py
    llm = init_chat_model("claude-haiku-4-5", model_provider="anthropic")
    structured_llm = llm.with_structured_output(QuizQuestion)

    print("--- Generator Quizu AI ---")
    
    # Get user input
    try:
        num_questions = int(input("Ile pytań chcesz wygenerować? (max 10): "))
        if num_questions > 10:
            print("Maksymalna liczba pyatń to 10. Ustawiam na 10.")
            num_questions = 10
        elif num_questions < 1:
            print("Minimalna liczba pytań to 1. Ustawiam na 1.")
            num_questions = 1
    except ValueError:
        print("Nieprawidłowa wartość. Ustawiam 3 pytania.")
        num_questions = 3

    topic = input("Podaj tematykę quizu: ")

    messages = [
        SystemMessage(content=f"Jesteś twórcą quizów. Generujesz pytania na temat: {topic}. "
                              f"Każde pytanie musi być unikalne i nie powtarzać się z poprzednimi."
                              f"Upewnij się, że tylko jedna odpowiedź na pytanie jest poprawna")
    ]

    questions_data = []
    user_answers = []

    for i in range(num_questions):
        print(f"\nGeneruję pytanie {i+1}...")
        
        # Invoke LLM to get a structured question
        # We pass the history of messages which includes previous questions (as AIMessages)
        response = structured_llm.invoke(messages + [HumanMessage(content="Generuj kolejne pytanie.")])
        
        # Save question data
        questions_data.append(response)
        
        # Add to history to avoid duplicates
        # We store it as a string representation of the question content so the model sees it
        messages.append(AIMessage(content=f"Pytanie {i+1}: {response.question} (Opcje: {response.a}, {response.b}, {response.c}, {response.d}. Poprawna: {response.correct_answer})"))

        # Ask the user
        print(f"\nPytanie {i+1}: {response.question}")
        print(f"a) {response.a}")
        print(f"b) {response.b}")
        print(f"c) {response.c}")
        print(f"d) {response.d}")
        
        while True:
            ans = input("Twoja odpowiedź (a/b/c/d): ").lower().strip()
            if ans in ["a", "b", "c", "d"]:
                user_answers.append(ans)
                break
            print("Wybierz jedną z opcji: a, b, c lub d.")

    # Show results
    print("\n" + "="*20)
    print("KONIEC QUIZU")
    print("="*20)
    
    correct_count = 0
    incorrect_questions = []

    for idx, (question, user_ans) in enumerate(zip(questions_data, user_answers)):
        if user_ans == question.correct_answer:
            correct_count += 1
        else:
            incorrect_questions.append((idx + 1, question, user_ans))

    print(f"Poprawne odpowiedzi: {correct_count}")
    print(f"Błędne odpowiedzi: {len(questions_data) - correct_count}")

    if incorrect_questions:
        print("\nPodsumowanie błędnych odpowiedzi:")
        for num, q, ans in incorrect_questions:
            print(f"\nPytanie {num}: {q.question}")
            print(f"Twoja odpowiedź: {ans}")
            print(f"Poprawna odpowiedź: {q.correct_answer} ({getattr(q, q.correct_answer)})")

if __name__ == "__main__":
    main()
