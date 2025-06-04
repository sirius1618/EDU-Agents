def calculate_urgency(sentimento, topico):
    base_score = 3

    if sentimento['normalized'] < -0.5:
        base_score += 1
    elif sentimento['normalized'] > 0.7:
        base_score -= 1

    if topico['topic_name'] == "Dificuldade Conceitual":
        base_score += 1

    return min(max(base_score, 1), 5)