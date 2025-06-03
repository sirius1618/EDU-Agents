
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import shap
import matplotlib.pyplot as plt
import joblib
import os

class ModeloDesempenho:
    """
    1. Modelo otimizado para classificação binária (dificuldade vs não dificuldade)
    2. SHAP fornece transparência sobre quais features influenciam as previsões
    3. Visualizações ajudam educadores a entender os padrões detectados
    """
    def __init__(self):
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        self.explainer = None
    
    def treinar(self, X_train, y_train):
        """Treina o modelo"""
        self.model.fit(X_train, y_train)
        return self.model
    
    def evaluate(self, X_test, y_test):
        """Avalia o desempenho do modelo"""
        y_pred = self.model.predict(X_test)
        print("Acurácia:", accuracy_score(y_test, y_pred))
        print("\nRelatório de Classificação:")
        print(classification_report(y_test, y_pred))
        return y_pred
    
    def explain(self, X, save_dir='agents/performance_agent'):
        """Gera explicações SHAP para as previsões e salva gráficos"""
        os.makedirs(save_dir, exist_ok=True)
        
        self.explainer = shap.TreeExplainer(self.model)
        shap_values = self.explainer.shap_values(X)
        
        # Importância global das features
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, show=False)
        plt.savefig(os.path.join(save_dir, 'feature_importance.png'))
        plt.close()
        
        # Explicação individual (exemplo: primeiro registro)
        plt.figure()
        shap.force_plot(
            self.explainer.expected_value, 
            shap_values[0], 
            X.iloc[0],
            show=False,
            matplotlib=True
        )
        plt.savefig(os.path.join(save_dir, 'individual_explanation.png'))
        plt.close()
        
        return shap_values
    
    def prever_dificuldades(self, new_data):
        """Faz previsões para novos dados"""
        return self.model.predict(new_data), self.model.predict_proba(new_data)
    
    def salvar_modelo(self, caminho_arquivo):
        """Salva o modelo treinado em disco"""
        joblib.dump(self.model, caminho_arquivo)
        print(f"Modelo salvo em {caminho_arquivo}")
    
    def carregar_modelo(self, caminho_arquivo):
        """Carrega um modelo salvo de disco"""
        self.model = joblib.load(caminho_arquivo)
        print(f"Modelo carregado de {caminho_arquivo}")
