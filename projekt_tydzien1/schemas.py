from typing import Literal
from pydantic import BaseModel, Field

class QuizQuestion(BaseModel):
    question: str = Field(description="Treść pytania")
    a: str = Field(description="Opcja A")
    b: str = Field(description="Opcja B")
    c: str = Field(description="Opcja C")
    d: str = Field(description="Opcja D")
    correct_answer: Literal["a", "b", "c", "d"] = Field(description="Litera poprawnej odpowiedzi (a, b, c lub d)")

class QuizConfig(BaseModel):
    topic: str
    difficulty: str = "Średni"
    num_questions: int = 3
