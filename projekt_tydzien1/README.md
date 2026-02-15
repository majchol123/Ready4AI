# Quiz AI Project

Samodzielna aplikacja quizowa z podziałem na backend i frontend.

## Instalacja

1. Wejdź do katalogu projektu:
   ```bash
   cd projekt_tydzien1
   ```

2. (Opcjonalnie) Stwórz i aktywuj wirtualne środowisko:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Zainstaluj wymagane zależności:
   ```bash
   pip install -r requirements.txt
   ```

4. Upewnij się, że plik `.env` istnieje i zawiera klucz API.

## Uruchomienie

### Backend
Uruchom serwer w pierwszym terminalu:
```bash
./run_backend.sh
```
Lub ręcznie: `uvicorn backend:app --reload`

### Frontend
Uruchom aplikację v drugim terminalu:
```bash
./run_frontend.sh
```
Lub ręcznie: `streamlit run frontend.py`

## Struktura
- `backend.py`: Serwer API
- `frontend.py`: Klient Streamlit
- `schemas.py`: Modele danych
- `requirements.txt`: Zależności
- `.env`: (należy utworzyć i dodać klucz API)
- `.env.example`: Przykładowy plik konfiguracyjny (można go wykorzystać do stworzenia `.env`)
