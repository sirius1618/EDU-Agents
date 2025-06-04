from typing import Counter

import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer


class NLPProcessor:
    def __init__(self, model_path):
        self.nlp_pt = spacy.load("pt_core_news_sm")

        # Carrega o modelo de sentimento treinado por você
        self.sentiment_model_path = model_path
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=AutoModelForSequenceClassification.from_pretrained(self.sentiment_model_path),
            tokenizer=AutoTokenizer.from_pretrained(self.sentiment_model_path)
        )

        # Você ainda pode manter o modelo de embeddings sem mudar
        self.sentence_model = SentenceTransformer("rufimelo/bert-large-portuguese-cased-sts")

    def preprocess_text(self, text):
        doc = self.nlp_pt(text)
        return " ".join([
            token.lemma_.lower() for token in doc
            if not token.is_stop and not token.is_punct
        ])

    def analyze_sentiment(self, text):
        result = self.sentiment_analyzer(text)[0]
        return {
            "label": result['label'],  # Agora pode retornar 'Positivo', 'Neutro', 'Negativo'
            "score": result['score'],
            "normalized": self._normalize_sentiment(result)
        }

    def _normalize_sentiment(self, result):
        """Converte saída para escala -1 (Negativo) a 1 (Positivo), 0 para Neutro"""
        label_map = {"Negativo": -1, "Neutro": 0, "Positivo": 1}
        return label_map.get(result['label'], 0) * result['score']

    def get_semantic_embedding(self, text):
        return self.sentence_model.encode(text)

    def extract_key_phrases(self, text):
        doc = self.nlp_pt(text)
        return [chunk.text for chunk in doc.noun_chunks]
