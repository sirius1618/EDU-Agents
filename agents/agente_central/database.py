import sqlite3
import json
from pathlib import Path
from agents.agente_central.modelos import AlunoProfile, InsightDesempenho

DB_PATH = "central_db.sqlite"

def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de perfis de alunos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY,
        data TEXT NOT NULL
    )''')
    
    # Tabela de insights de desempenho
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS desempenho (
        aluno_id INTEGER,
        disciplina TEXT,
        predicao INTEGER,
        probabilidade REAL,
        features_importantes TEXT,
        timestamp TEXT,
        FOREIGN KEY(aluno_id) REFERENCES alunos(id)
    )''')
    
    conn.commit()
    conn.close()

def salvar_insight(insight: InsightDesempenho):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR IGNORE INTO alunos (id) VALUES (?)
    ''', (insight.aluno_id,))
    
    cursor.execute('''
    INSERT INTO desempenho (
        aluno_id, disciplina, predicao, probabilidade, 
        features_importantes, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        insight.aluno_id,
        insight.disciplina,
        insight.predicao,
        insight.probabilidade,
        json.dumps(insight.features_importantes),
        insight.timestamp
    ))
    
    conn.commit()
    conn.close()

def carregar_perfil(aluno_id: int) -> AlunoProfile:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT data FROM alunos WHERE id = ?', (aluno_id,))
    aluno_data = cursor.fetchone()
    
    if not aluno_data:
        return None
    
    cursor.execute('''
    SELECT disciplina, predicao, probabilidade, features_importantes, timestamp
    FROM desempenho WHERE aluno_id = ?
    ''', (aluno_id,))
    
    desempenho = {}
    for row in cursor.fetchall():
        disciplina, predicao, prob, features, timestamp = row
        desempenho[disciplina] = InsightDesempenho(
            aluno_id=aluno_id,
            disciplina=disciplina,
            predicao=predicao,
            probabilidade=prob,
            features_importantes=json.loads(features),
            timestamp=timestamp
        )
    
    conn.close()
    
    # TO-DO: Constroi perfil (feedback e comportamento serão adicionados posteriormente)
    return AlunoProfile(
        aluno_id=aluno_id,
        desempenho=desempenho,
        recomendacoes=[]
    )

init_db()
