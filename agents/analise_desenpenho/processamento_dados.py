import pandas as pd
from sklearn.model_selection import train_test_split

class ProcessadorDados:
    """
    1. Cria features significativas como overall_score e attendance_rate
    2. Garante balanceamento adequado entre treino e teste
    3. Prepara dados para diferentes algoritmos de ML
    """


    def __init__(self, data):  # Altere o parâmetro para um nome genérico
        if isinstance(data, pd.DataFrame):
            self.df = data  # Usa o DataFrame diretamente
        elif isinstance(data, str):
            self.df = pd.read_csv(data)  # Lê de um arquivo se for string
        else:
            raise ValueError("Parâmetro deve ser um DataFrame ou caminho de arquivo")
    def preparar_dados(self):
        """Prepara os dados para modelagem"""
        # 1. Engenharia de features
        self.df['overall_score'] = (self.df['math_score'] + self.df['language_score']) / 2
        self.df['attendance_rate'] = 1 - (self.df['absences'] / 30)  # Supondo 30 dias
        
        # 2. Seleção de features relevantes
        features = [
            'math_score', 'language_score', 'absences', 
            'participation', 'homework_completion', 
            'previous_performance', 'attendance_rate'
        ]
        
        # 3. Definir target
        self.features = self.df[features]
        self.target = self.df['has_difficulty']
        
        return self.features, self.target
    
    def dividir_dados(self, test_size=0.2):
        """Divide os dados em conjuntos de treino e teste"""
        return train_test_split(
            self.features, 
            self.target, 
            test_size=test_size, 
            stratify=self.target,  # Mantém proporção de dificuldades
            random_state=42
        )
