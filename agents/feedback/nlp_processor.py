import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer

class NLPProcessor:
    def __init__(self):
        self.nlp_pt = spacy.load("pt_core_news_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis",model="neuralmind/bert-large-portuguese-cased")
        self.sentence_model = SentenceTransformer("rufimelo/bert-large-portuguese-cased-sts")

    def preprocess_text(self, text):
        doc = self.nlp_pt(text)
        return " ".join([
            token.lemma_.lower() for token in doc
            if not token.is_stop and not token.is_punct
        ])

    def analyze_sentiment(self, text):
        result = self.sentiment_analyzer(text)[0]
        print(self.sentiment_analyzer(text))
        return {
            "label": result['label'],
            "score": result['score'],
            "normalized": self._normalize_sentiment(result)
        }

    def _normalize_sentiment(self, result):
        """Converte saída para escala -1 (neg) a 1 (pos)"""
        if result['label'] == 'LABEL_1':
            return result['score']
        return -result['score']

    def get_semantic_embedding(self, text):
        return self.sentence_model.encode(text)

    def extract_key_phrases(self, text):
        doc = self.nlp_pt(text)
        return [chunk.text for chunk in doc.noun_chunks]