from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class InsightDesempenho(BaseModel):
    aluno_id: int
    disciplina: str
    predicao: int
    probabilidade: float
    features_importantes: Dict[str, float]
    timestamp: str

class Recomendacao(BaseModel):
    aluno_id: int
    acoes: List[str]
    prioridade: int  # 1-5 (5 = máxima urgência)
    fundamento: str

class AlunoProfile(BaseModel):
    aluno_id: int
    desempenho: Dict[str, InsightDesempenho]  # disciplina: insight
    feedback: Optional[Dict[str, Any]] = None
    comportamento: Optional[Dict[str, Any]] = None
    recomendacoes: List[Recomendacao] = []
