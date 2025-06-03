
import pandas as pd
import numpy as np

def generate_sample_data(num_students=100, output_path='sample_data.csv'):
    """Gera dados fictícios de desempenho de alunos"""
    num_students = int(num_students) 
    np.random.seed(42)
    
    data = {
        'student_id': range(1, num_students + 1),
        'math_score': np.clip(np.random.normal(6.5, 1.5, num_students), 0, 10),
        'language_score': np.clip(np.random.normal(7.0, 1.2, num_students), 0, 10),
        'absences': np.random.randint(0, 15, num_students),
        'participation': np.random.uniform(0.4, 1.0, num_students),
        'homework_completion': np.random.uniform(0.3, 1.0, num_students),
        'previous_performance': np.clip(np.random.normal(6.8, 1.3, num_students), 0, 10)
    }
    
    df = pd.DataFrame(data)

    # Aplicar penalidade nas notas de matemática para simular dificuldades
    for i in range(min(20, num_students)):
        df.at[i, 'math_score'] = max(0, df.at[i, 'math_score'] - np.random.uniform(1.5, 3.0))
    
    # Marcar dificuldades
    df['has_difficulty'] = df['math_score'].apply(lambda x: 1 if x < 5 else 0)
    
    df.to_csv('sample_data.csv', index=False)
    return df

if __name__ == "__main__":
    generate_sample_data()
