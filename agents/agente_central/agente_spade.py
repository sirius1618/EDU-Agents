import asyncio
import json
import logging
import spade
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from agents.agente_central.database import carregar_perfil
from agents.agente_central.integrador import IntegradorCentral
from agents.agente_central.modelos import InsightDesempenho

class AgenteCentral(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.integrador = IntegradorCentral()

    async def setup(self):
        logging.info(f"Agente Central {self.jid} inicializado")
        self.add_behaviour(self.ReceberInsightsBehaviour())
        self.add_behaviour(self.AtenderSolicitacoesBehaviour())

    class ReceberInsightsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=30)
            if msg:
                try:
                    corpo = json.loads(msg.body)
                    tipo = corpo.get("tipo")
                    
                    if tipo == "insight_desempenho":
                        insight = InsightDesempenho(
                            aluno_id=corpo["aluno_id"],
                            disciplina=corpo["disciplina"],
                            predicao=corpo["predicao"],
                            probabilidade=corpo["probabilidade"],
                            features_importantes=corpo["features_importantes"],
                            timestamp=datetime.datetime.now().isoformat()
                        )
                        
                        perfil_atualizado = self.agent.integrador.processar_insight_desempenho(insight)
                        logging.info(f"Insight processado para aluno {insight.aluno_id}")
                        
                        # Notificar agentes interessados
                        notificacao = Message(
                            to="agente_planejamento@localhost"  # Substituir pelo JID real
                        )
                        notificacao.body = json.dumps({
                            "tipo": "perfil_atualizado",
                            "aluno_id": insight.aluno_id
                        })
                        await self.send(notificacao)
                    
                    elif tipo == "feedback_analisado":
                        # TODO: Implementar processamento de feedback
                        pass
                        
                except Exception as e:
                    logging.error(f"Erro ao processar mensagem: {str(e)}")
                    
                    # Enviar resposta de erro
                    erro_msg = msg.make_reply()
                    erro_msg.body = json.dumps({
                        "status": "erro",
                        "detalhes": str(e)
                    })
                    await self.send(erro_msg)

    class AtenderSolicitacoesBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    corpo = json.loads(msg.body)
                    solicitacao = corpo.get("solicitacao")
                    
                    if solicitacao == "obter_perfil":
                        aluno_id = corpo["aluno_id"]
                        perfil = carregar_perfil(aluno_id)
                        
                        resposta = msg.make_reply()
                        resposta.body = perfil.json() if perfil else json.dumps({"erro": "Perfil não encontrado"})
                        await self.send(resposta)
                    
                    elif solicitacao == "resumo_turma":
                        resumo = self.agent.integrador.gerar_resumo_turma()
                        resposta = msg.make_reply()
                        resposta.body = json.dumps(resumo)
                        await self.send(resposta)
                    
                except Exception as e:
                    logging.error(f"Erro ao atender solicitação: {str(e)}")
                    
                    erro_msg = msg.make_reply()
                    erro_msg.body = json.dumps({
                        "status": "erro",
                        "detalhes": str(e)
                    })
                    await self.send(erro_msg)
