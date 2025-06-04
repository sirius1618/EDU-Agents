import asyncio
import json
import spade
import logging
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from .nlp_processor import NLPProcessor
from .topic_modeling import TopicModeler

class AgenteFeedback(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.nlp = NLPProcessor()
        self.topic_modeler = TopicModeler()
        self.initialize_models()

    def initialize_models(self):
        # Carregar dados históricos para treinar modelo de tópicos
        try:
            with open("agents/feedback_agent/historic_feedbacks.json") as f:
                historic_data = json.load(f)
            texts = [item['text'] for item in historic_data]
            self.topic_modeler.fit(texts)
        except FileNotFoundError:
            logging.warning("Dados históricos não encontrados. Usando modelo padrão.")

class ProcessarFeedbackBehaviour(CyclicBehaviour):

    async def run(self):

        msg = await self.receive(timeout=30)
        if msg:
            try:
                data = json.loads(msg.body)
                # Processamento NLP
                cleaned_text = self.agent.nlp.preprocess_text(data['texto'])
                sentiment = self.agent.nlp.analyze_sentiment(data['texto'])
                topic = self.agent.topic_modeler.predict_topic(cleaned_text)
                key_phrases = self.agent.nlp.extract_key_phrases(data['texto'])

                # Calcular urgência
                urgency = self.calculate_urgency(sentiment, topic)

                # Estruturar resposta
                insight = {
                    "aluno_id": data.get('aluno_id'),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "texto_original": data['texto'],
                    "texto_processado": cleaned_text,
                    "sentimento": sentiment,
                    "topico": topic,
                    "frases_chave": key_phrases,
                    "urgencia": urgency,
                    "metadados": data.get('metadados', {})
                }

                # Enviar para Agente Central
                response = Message(to="agente_central@localhost")
                response.body = json.dumps({
                    "tipo": "feedback_analisado",
                    "insight": insight
                })
                await self.send(response)

            except Exception as e:
                logging.error(f"Erro ao processar feedback: {str(e)}")


    # Enviar mensagem de erro
    def calculate_urgency(self, sentiment, topic):
        """Calcula urgência de 1-5 baseado em análise"""
        base_score = 3

        # Ajuste por sentimento
        if sentiment['normalized'] < -0.5:
            base_score += 1
        elif sentiment['normalized'] > 0.7:
            base_score -= 1

        # Ajuste por tópico
        if topic['topic_name'] == "Dificuldade Conceitual":
            base_score += 1

        return min(max(base_score, 1), 5)

    async def setup(self):
        logging.info(f"Agente de Feedback {self.jid} inicializado")
        self.add_behaviour(self.ProcessarFeedbackBehaviour())
