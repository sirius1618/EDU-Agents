import os
import json
import asyncio
import pandas as pd
import shap
import datetime
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
        self.explainer = None
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
            
            # 1. Gerar/obter dados
            if not os.path.exists(self.agent.caminho_dados):
                generate_sample_data(100, self.agent.caminho_dados)
            
            # 2. Processar dados
            df = pd.read_csv(self.agent.caminho_dados)
            student_ids = df['student_id']  # Preservar IDs
            df_sem_id = df.drop(columns=['student_id'])
            
            processador = ProcessadorDados(df_sem_id)
            X, y = processador.preparar_dados()
            X_treino, X_teste, y_treino, y_teste = processador.dividir_dados()
            
            # 3. Treinar modelo
            self.agent.modelo = ModeloDesempenho()
            self.agent.modelo.treinar(X_treino, y_treino)
            self.agent.modelo.salvar_modelo(self.agent.caminho_modelo)
            
            # 4. Criar explainer SHAP (uma vez por treinamento)
            self.agent.explainer = shap.TreeExplainer(self.agent.modelo.model)
            
            # 5. Processar cada aluno individualmente
            for idx, row in X_teste.iterrows():
                aluno_id = student_ids.iloc[idx]
                aluno_df = pd.DataFrame([row])
                
                # Fazer previsão individual
                predicao, probabilidade = self.agent.modelo.prever_dificuldades(aluno_df)
                
                # Obter features importantes com SHAP
                shap_values = self.agent.explainer.shap_values(aluno_df)[0]
                feature_names = aluno_df.columns
                feature_imp = {feature_names[i]: float(shap_values[i]) 
                              for i in range(len(feature_names))}
                top_features = dict(sorted(
                    feature_imp.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )[:3])  # Top 3 features
                
                # Construir insight detalhado
                insight = {
                    "tipo": "insight_desempenho",
                    "aluno_id": int(aluno_id),
                    "disciplina": "matematica",
                    "predicao": int(predicao[0]),
                    "probabilidade": float(probabilidade[0][1]),
                    "features_importantes": top_features,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Enviar para Agente Central
                msg = Message(to="agente_central@localhost")
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps(insight)
                await self.send(msg)
            
            # 6. Enviar notificação de conclusão
            msg_final = Message(to="agente_central@localhost")
            msg_final.set_metadata("performative", "inform")
            msg_final.body = json.dumps({
                "tipo": "analise_concluida",
                "status": "sucesso",
                "total_alunos": len(X_teste)
            })
            await self.send(msg_final)

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
                    
                    # Se existir explainer, obter features importantes
                    features_importantes = {}
                    if hasattr(self.agent, 'explainer') and self.agent.explainer:
                        shap_values = self.agent.explainer.shap_values(aluno_df)[0]
                        feature_names = aluno_df.columns
                        features_importantes = {
                            feature_names[i]: float(shap_values[i]) 
                            for i in range(len(feature_names))
                        }

                    resposta = {
                        "id_aluno": dados['id_aluno'],
                        "predicao": int(predicao[0]),
                        "probabilidade": float(probabilidade[0][1]),
                        "features_importantes": features_importantes,
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
