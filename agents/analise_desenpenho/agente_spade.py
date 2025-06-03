
import os
import json
import asyncio
import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message

from agents.analise_desenpenho.data_set_teste import generate_sample_data
from agents.analise_desenpenho.processamento_dados import ProcessadorDados
from agents.analise_desenpenho.modelo_treinado_xgboost import ModeloDesempenho


class AgenteDesempenho(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.modelo = None
        self.caminho_dados = 'agents/analise_desenpenho/sample_data.csv'
        self.caminho_modelo = 'agents/analise_desenpenho/modelo_xgboost.json'

    async def setup(self):
        print(f"Agente {self.jid} inicializado!")

        os.makedirs(os.path.dirname(self.caminho_dados), exist_ok=True)
        os.makedirs(os.path.dirname(self.caminho_modelo), exist_ok=True)

        self.add_behaviour(self.ComportamentoAnalise(period=10))
        self.add_behaviour(self.ComportamentoPrevisao())

    class ComportamentoAnalise(PeriodicBehaviour):
        async def run(self):
            print(f"[{self.agent.jid}] Iniciando análise periódica...")

            if not os.path.exists(self.agent.caminho_dados):
                generate_sample_data(100, self.agent.caminho_dados)

            processador = ProcessadorDados(self.agent.caminho_dados)
            X, y = processador.preparar_dados()
            X_treino, X_teste, y_treino, y_teste = processador.dividir_dados()

            self.agent.modelo = ModeloDesempenho()
            self.agent.modelo.treinar(X_treino, y_treino)
            self.agent.modelo.salvar_modelo(self.agent.caminho_modelo)

            msg = Message(to="agente_central@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps({
                "tipo": "analise_concluida",
                "status": "sucesso",
                "caminho_modelo": self.agent.caminho_modelo
            })
            await self.send(msg)

    class ComportamentoPrevisao(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    dados = json.loads(msg.body)
                    aluno_df = pd.DataFrame([dados['dados_aluno']])

                    if not hasattr(self.agent, 'modelo') or self.agent.modelo is None:
                        self.agent.modelo = ModeloDesempenho()
                        self.agent.modelo.carregar_modelo(self.agent.caminho_modelo)

                    predicao, probabilidade = self.agent.modelo.prever_dificuldades(aluno_df)

                    resposta = {
                        "id_aluno": dados['id_aluno'],
                        "predicao": int(predicao[0]),
                        "probabilidade": float(probabilidade[0][1]),
                        "explicacao": "Necessita reforço em matemática" if predicao[0] else "Desempenho satisfatório"
                    }

                    reply = msg.make_reply()
                    reply.body = json.dumps(resposta)
                    await self.send(reply)

                except Exception as e:
                    print(f"Erro ao processar mensagem: {e}")
                    erro = msg.make_reply()
                    erro.body = json.dumps({"erro": str(e)})
                    await self.send(erro)
