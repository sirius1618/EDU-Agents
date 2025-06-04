from agents.feedback.feedback_analyzer import FeedbackAnalyzer

analisador = FeedbackAnalyzer()

# Lista de feedbacks a serem analisados
feedbacks = [
    "As atividades em grupo foram muito bem conduzidas pelo professor.",
    "Não gostei da abordagem usada na explicação do conteúdo.",
    "A aula estava razoável, nem boa nem ruim.",
    "Excelente apresentação, tudo muito claro e didático.",
    "O professor faltou e não avisou ninguém.",
    "A estrutura da sala estava boa, mas o conteúdo foi raso.",
    "Gostei do material utilizado nas atividades práticas.",
    "Achei a explicação meio confusa e apressada.",
    "Não tenho muito o que dizer, foi normal.",
    "Parabéns pela didática!"
]

resumo = analisador.resumir_feedbacks(feedbacks)

from pprint import pprint
pprint(resumo)
