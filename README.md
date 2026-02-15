# Kurs Ready4AI - Rozwiązania zadań

Repozytorium zawierające rozwiązania zadań, kody testowe oraz projekty realizowane w ramach kursu **Ready4AI**.

## Struktura repozytorium

Folder ten jest zorganizowany według tygodni kursu:

*   `tydzienX/` – mniejsze zadania, ćwiczenia i kod testowy z poszczególnych lekcji
*   `projekt_tydzienX/` – projekt podsumowujący dany tydzień

## Zawartość kursu

### Tydzień 1: Podstawy AI, REST API, LangChain i proste Chatboty
*   **Zadania (`tydzien1/`)**:
    *   `lc1.py`: Prosty chatbot z nieskończoną pętlą rozmowy.
    *   `lc2.py`: Chatbot wykorzystujący `InMemoryChatMessageHistory` do zarządzania stanem rozmowy.
    *   `tydzien1.py`: Konsolowy generator quizów wykorzystujący `with_structured_output` do tworzenia pytań w formacie JSON.
    *   `tydzien1_st.py`: Implementacja generatora quizów w Streamlit.
*   **Projekt Tygodniowy (`projekt_tydzien1/`)**:
    *   **Quiz AI App**: Generator quizów z podziałem na warstwę **Backend** (FastAPI) i **Frontend** (Streamlit). Aplikacja pozwala na generowanie pytań na dowolny temat.

## Jak korzystać z repozytorium?

1.  Sklonuj repozytorium na swój komputer (git clone https://github.com/majchol123/Ready4AI.git).
2.  Zainstaluj wymagane zależności (często znajdują się w `requirements.txt` wewnątrz folderów projektowych).
3.  Upewnij się, że posiadasz odpowiednie klucze API (np. Anthropic, OpenAI) i skonfiguruj pliki `.env` zgodnie z przykładami (`.env.example`).

---
*Repozytorium stworzone na potrzeby kursu Ready4AI.*
