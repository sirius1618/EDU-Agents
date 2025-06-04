import json
import logging
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from feedback_analyzer import FeedbackAnalyzer
from topic_modeling import TopicModeler

class AgenteFeedback(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.analyzer = FeedbackAnalyzer()
        self.topic_modeler = TopicModeler()
        self.initialize_models()

    def initialize_models(self):
        try:
            with open("agents/feedback_agent/historic_feedbacks.json") as f:
                historic_data = json.load(f)
            texts = [item['text'] for item in historic_data]
            self.topic_modeler.fit(texts)
        except FileNotFoundError:
            logging.warning("Dados históricos não encontrados. Usando modelo padrão.")


def calculate_urgency(sentimento, topico):
    base_score = 3

    if sentimento['normalized'] < -0.5:
        base_score += 1
    elif sentimento['normalized'] > 0.7:
        base_score -= 1

    if topico['topic_name'] == "Dificuldade Conceitual":
        base_score += 1

    return min(max(base_score, 1), 5)


class ProcessarFeedbackBehaviour(CyclicBehaviour):
    async def on_start(self):
        logging.info("Comportamento ProcessarFeedbackBehaviour iniciado")

    async def run(self):
        msg = await self.receive(timeout=30)
        if msg:
            try:
                data = json.loads(msg.body)
                feedbacks = data.get("feedbacks", [])
                if not feedbacks:
                    logging.warning("Nenhum feedback recebido na mensagem.")
                    return

                resultados_individuais = []
                for item in feedbacks:
                    resultado = self.agent.analyzer.analisar_feedback(item["texto"])
                    resultado["aluno_id"] = item.get("aluno_id")
                    resultado["timestamp"] = datetime.datetime.now().isoformat()
                    resultado["topico"] = self.agent.topic_modeler.predict_topic(
                        self.agent.analyzer.nlp.preprocess_text(item["texto"])
                    )
                    resultado["urgencia"] = calculate_urgency(resultado["sentimento"], resultado["topico"])

                    resultados_individuais.append(resultado)

                resumo_geral = self.agent.analyzer.resumir_feedbacks(resultados_individuais)

                # Enviar para Agente Central
                response = Message(to="agente_central@localhost")
                response.body = json.dumps({
                    "tipo": "feedbacks_analisados",
                    "resumo": resumo_geral,
                    "detalhado": resultados_individuais
                })
                await self.send(response)

            except Exception as e:
                logging.error(f"Erro ao processar feedbacks: {str(e)}")


async def setup(self):
    logging.info(f"Agente de Feedback {self.jid} inicializado")
    self.add_behaviour(self.ProcessarFeedbackBehaviour())
