import os
from pathlib import Path

from agents.feedback.feedback_training import train_model
from agents.feedback.nlp_processor import NLPProcessor
from collections import Counter, defaultdict

class FeedbackAnalyzer:
    def __init__(self, model_dir_name="sentiment-model"):
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        models_base_dir = os.path.join(current_file_dir, "models")
        self.model_path = os.path.join(models_base_dir, model_dir_name)

        if not self._modelo_treinado_existe():
            print(f"Modelo não encontrado em '{self.model_path}'. Treinando modelo...")
            train_model(self.model_path)
            print("Modelo treinado com sucesso.")

        # Agora que o modelo existe, podemos carregar o NLPProcessor
        self.nlp = NLPProcessor(self.model_path)

    def _modelo_treinado_existe(self):
        return os.path.isdir(self.model_path) and \
               os.path.exists(os.path.join(self.model_path, "model.safetensors")) and \
               os.path.exists(os.path.join(self.model_path, "tokenizer_config.json"))

    def analisar_feedback(self, texto):
        sentimento = self.nlp.analyze_sentiment(texto)
        embedding = self.nlp.get_semantic_embedding(texto)
        key_phrases = self.nlp.extract_key_phrases(texto)

        return {
            "texto_original": texto,
            "sentimento": sentimento,
            "frases_chave": key_phrases,
            "embedding": embedding.tolist()
        }

    def resumir_feedbacks(self, resultados):
        contador_labels = Counter()
        soma_confiancas = 0
        soma_confianca_por_label = defaultdict(float)
        contagem_por_label = Counter()

        for r in resultados:
            label = r["sentimento"]["label"]
            score = r["sentimento"]["score"]

            contador_labels[label] += 1
            soma_confiancas += score
            soma_confianca_por_label[label] += score
            contagem_por_label[label] += 1

        total_feedbacks = len(resultados)
        percentuais = {
            label: f"{(qtd / total_feedbacks) * 100:.2f}%"
            for label, qtd in contador_labels.items()
        }

        media_confianca_geral = soma_confiancas / total_feedbacks
        media_confianca_por_label = {
            label: soma_confianca_por_label[label] / contagem_por_label[label]
            for label in contador_labels
        }

        # --- Resultado final ---
        resumo = {
            "total_feedbacks": total_feedbacks,
            "distribuicao_labels": dict(contador_labels),
            "percentual_por_label": percentuais,
            "media_confiança_geral": round(media_confianca_geral, 4),
            "media_confiança_por_label": {
                k: round(v, 4) for k, v in media_confianca_por_label.items()
            }
        }

        return resumo