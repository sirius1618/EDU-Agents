import pandas as pd
import os
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split # Importar para a divisão estratificada
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def train_model(model_path):
    # --- 1. Carrega sua base e prepara os dados ---
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(current_script_dir, "models", "bertimbau", "feedback_treinamento.json")
    print("Path usado:", base_path)
    df = pd.read_json(base_path)

    # Mapeia rótulos para números
    # Mantenha a ordem que faz mais sentido para você, mas seja consistente
    label2id = {"Negativo": 0, "Neutro": 1, "Positivo": 2}
    id2label = {v: k for k, v in label2id.items()}

    # Adiciona a coluna numérica 'labels' (nome esperado pelo Trainer)
    df["labels"] = df["sentimento"].map(label2id)

    # --- CORREÇÃO CHAVE AQUI: Dividir o DataFrame com stratify antes de converter para Dataset ---
    # Isso garante que a proporção de cada sentimento seja a mesma em ambos os conjuntos
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        stratify=df['labels'], # <--- AQUI ESTÁ A ESTRATIFICAÇÃO!
        random_state=42 # Para reprodutibilidade
    )

    # Converte os DataFrames para objetos Dataset do Hugging Face
    # Agora, os datasets já estão divididos e estratificados
    train_dataset = Dataset.from_pandas(train_df[["texto", "labels"]])
    test_dataset = Dataset.from_pandas(test_df[["texto", "labels"]])

    # --- 2. Tokenização ---
    model_name = "neuralmind/bert-large-portuguese-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize(batch):
        # 'texto' é o nome da coluna no seu DataFrame original.
        # O tokenizer espera uma lista de textos.
        return tokenizer(batch["texto"], padding=True, truncation=True)

    # Aplica a tokenização aos datasets
    # O 'remove_columns=["texto"]' é importante para remover a coluna de texto original
    # e manter apenas as colunas que o modelo espera (input_ids, attention_mask, token_type_ids, labels)
    tokenized_train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=["texto"])
    tokenized_test_dataset = test_dataset.map(tokenize, batched=True, remove_columns=["texto"])

    # Define o formato dos tensores para PyTorch (opcional, mas boa prática)
    tokenized_train_dataset.set_format("torch")
    tokenized_test_dataset.set_format("torch")

    # --- 3. Modelo com cabeçote de classificação ---
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label2id), # Usa o número de rótulos do seu dicionário
        id2label=id2label,
        label2id=label2id
    )

    # --- 4. Métricas de avaliação ---
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1) # Pega o índice da maior probabilidade como a previsão

        # Usar 'weighted' para f1, precision e recall, pois as classes podem estar desbalanceadas
        # Adicionado 'zero_division=0' para lidar com classes que podem não ter previsões ou rótulos
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    # --- 5. Configura o treinamento ---
    training_args = TrainingArguments(
        output_dir=model_path,
        eval_strategy="epoch",  # Avalia no final de cada época
        save_strategy="epoch",        # Salva no final de cada época
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir="./logs",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy", # Você pode mudar para 'f1' se preferir otimizar o F1-score
        report_to="tensorboard" # Opcional: para visualizar o progresso com TensorBoard
    )

    # --- 6. Trainer ---
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset, # Passa os datasets tokenizados
        eval_dataset=tokenized_test_dataset,
        tokenizer=tokenizer, # É bom passar o tokenizer também
        compute_metrics=compute_metrics
    )

    # --- 7. Treinamento ---
    print("Iniciando o treinamento do modelo de sentimento...")
    trainer.train()
    print("Treinamento concluído.")

    # --- 8. Salvar modelo ---
    # Garante que o modelo e o tokenizador do Trainer são salvos no diretório especificado
    trainer.save_model(model_path)
    # O tokenizador já é salvo com o modelo pelo trainer.save_model(), mas manter a linha não é prejudicial
    tokenizer.save_pretrained(model_path)
    print("Modelo de sentimento finetunado e tokenizador salvos em: " + model_path)

    # --- Testando o modelo salvo ---
    print("\n--- Testando o modelo finetunado ---")
    from transformers import pipeline

    # Carregar o modelo e o tokenizador salvos
    loaded_tokenizer = AutoTokenizer.from_pretrained(model_path)
    loaded_model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Criar a pipeline com o modelo finetunado
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=loaded_model,
        tokenizer=loaded_tokenizer
    )

    test_feedbacks = [
        "A aula foi fantástica e o professor explicou muito bem, aprendi muito!", # Positivo
        "Não entendi nada do conteúdo, foi péssimo e muito confuso.",          # Negativo
        "A apresentação estava ok, nada de especial, mas cumpriu o objetivo.",   # Neutro
        "A cadeira estava quebrada e o ar condicionado não funcionava.",       # Negativo
        "O material de apoio era bem completo e atualizado.",                  # Positivo
        "A aula de hoje foi sobre história da computação.",                   # Neutro
        "O professor faltou na última aula sem aviso."                        # Negativo
    ]

    for text in test_feedbacks:
        result = sentiment_pipeline(text)
        print(f"Texto: '{text}'")
        # O resultado agora virá com os rótulos 'Negativo', 'Neutro', 'Positivo'
        print(f"Sentimento: {result[0]['label']}, Confiança: {result[0]['score']:.4f}")
        print("-" * 50)