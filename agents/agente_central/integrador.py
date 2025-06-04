import datetime
from agents.agente_central.modelos import AlunoProfile, Recomendacao, InsightDesempenho
from agents.agente_central.database import carregar_perfil, salvar_insight

class IntegradorCentral:
    def __init__(self):
        self.recomendacoes_padrao = {
            "matematica": [
                "Sessões de reforço duas vezes por semana",
                "Atividades complementares de lógica",
                "Tutoria individual"
            ],
            "portugues": [
                "Clube de leitura",
                "Exercícios de redação",
                "Oficina de interpretação de texto"
            ]
        }

    def processar_insight_desempenho(self, insight: InsightDesempenho):
        # Salva no banco de dados
        salvar_insight(insight)
        
        # Carrega perfil existente
        perfil = carregar_perfil(insight.aluno_id) or AlunoProfile(
            aluno_id=insight.aluno_id,
            desempenho={}
        )
        
        # Atualiza perfil
        perfil.desempenho[insight.disciplina] = insight
        
        # Gera recomendações iniciais
        if insight.predicao == 1:  # Dificuldade detectada
            novas_recomendacoes = [
                Recomendacao(
                    aluno_id=insight.aluno_id,
                    acoes=[acao],
                    prioridade=3 if insight.probabilidade < 0.7 else 4,
                    fundamento=f"Dificuldade em {insight.disciplina} (prob: {insight.probabilidade:.2f})"
                ) for acao in self.recomendacoes_padrao.get(insight.disciplina, [])
            ]
            
            # Filtra recomendações duplicadas
            acoes_existentes = {r.acoes[0] for r in perfil.recomendacoes}
            for rec in novas_recomendacoes:
                if rec.acoes[0] not in acoes_existentes:
                    perfil.recomendacoes.append(rec)
        
        # TODO: Adicionar lógica mais complexa de recomendação
        
        return perfil

    def gerar_resumo_turma(self):
        # TODO: Implementar análise consolidada
        return {
            "status": "Em desenvolvimento",
            "alunos_com_dificuldade": 0,
            "disciplinas_criticas": []
        }
