from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

class TopicModeler:
    def __init__(self, n_topics=5):
        self.n_topics = n_topics
        self.vectorizer = CountVectorizer(max_df=0.95, min_df=2)
        self.lda = LatentDirichletAllocation(
            n_components=n_topics,
            learning_method='online'
        )
        self.topic_names = {
            0: "Dificuldade Conceitual",
            1: "Problemas com Materiais",
            2: "Questões Pedagógicas",
            3: "Feedback Positivo",
            4: "Sugestões"
        }

    def fit(self, texts):
        """Treina o modelo LDA com uma lista de textos."""
        tf = self.vectorizer.fit_transform(texts)
        self.lda.fit(tf)
        self._is_fitted = True
        return self

    def predict_topic(self, text: str):
        """Prediz o tópico dominante de um texto dado."""
        if not self._is_fitted:
            raise ValueError("O modelo precisa ser treinado com `.fit(texts)` antes de prever tópicos.")

        tf = self.vectorizer.transform([text])
        topic_dist = self.lda.transform(tf)[0]
        dominant_topic = int(np.argmax(topic_dist))

        return {
            "topic_id": dominant_topic,
            "topic_name": self.topic_names.get(dominant_topic, "Outros"),
            "confidence": float(topic_dist[dominant_topic])
        }
