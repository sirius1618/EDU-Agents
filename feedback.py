from agents.feedback.feedback_analyzer import FeedbackAnalyzer
from agents.feedback.topic_modeling import TopicModeler
from agents.feedback.agente_spade import calculate_urgency
from pprint import pprint
import datetime

# Inicializa os componentes
analisador = FeedbackAnalyzer()
topic_modeler = TopicModeler()

# Simula dados históricos para treinar o modelo de tópicos
historico_exemplo = [
    "A explicação foi difícil de entender.",
    "Gostei bastante da dinâmica com os colegas.",
    "Faltou aprofundamento no conteúdo.",
    "A sala estava muito barulhenta.",
    "Material muito bom, ajudou bastante.",
]
topic_modeler.fit(historico_exemplo)
analisador.topic_modeler = topic_modeler  # vincula os modelos

# Feedbacks com estrutura esperada
feedbacks = [
    {"aluno_id": 1, "texto": "As atividades em grupo foram muito bem conduzidas pelo professor."},
    {"aluno_id": 2, "texto": "Não gostei da abordagem usada na explicação do conteúdo."},
    {"aluno_id": 3, "texto": "A aula estava razoável, nem boa nem ruim."},
    {"aluno_id": 4, "texto": "Excelente apresentação, tudo muito claro e didático."},
    {"aluno_id": 5, "texto": "O professor faltou e não avisou ninguém."},
    {"aluno_id": 6, "texto": "A estrutura da sala estava boa, mas o conteúdo foi raso."},
    {"aluno_id": 7, "texto": "Gostei do material utilizado nas atividades práticas."},
    {"aluno_id": 8, "texto": "Achei a explicação meio confusa e apressada."},
    {"aluno_id": 9, "texto": "Não tenho muito o que dizer, foi normal."},
    {"aluno_id": 10, "texto": "Parabéns pela didática!"}
]

# Análise detalhada
resultados_individuais = []
for fb in feedbacks:
    resultado = analisador.analisar_feedback(fb["texto"])
    resultado["aluno_id"] = fb["aluno_id"]
    resultado["timestamp"] = datetime.datetime.now().isoformat()
    resultado["topico"] = topic_modeler.predict_topic(analisador.nlp.preprocess_text(fb["texto"]))
    resultado["urgencia"] = calculate_urgency(resultado["sentimento"], resultado["topico"])
    resultados_individuais.append(resultado)

# Gera o resumo geral (dashboard)
resumo_geral = analisador.resumir_feedbacks(resultados_individuais)

# Exibe resultado
pprint({
    "resumo": resumo_geral,
    "detalhado": resultados_individuais
})
