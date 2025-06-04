import asyncio
import os
import logging
import threading
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
from agents.analise_desenpenho.agente_spade import AgenteDesempenho
from agents.agente_central.agente_spade import AgenteCentral
from flask_cors import CORS

# Configurar logs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/dashboard/')
def serve_dashboard_index():
    return send_from_directory('dashboard', 'index.html')

@app.route('/dashboard/api')
def dashboard_api():
    try:
        df = pd.read_csv('sample_data.csv')
        if df.empty:
            return jsonify({"error": "Arquivo CSV vazio"}), 400
        
        # calcular estatísticas básicas
        stats = {
            'math_avg': df['math_score'].mean(),
            'language_avg': df['language_score'].mean(),
            'total_students': len(df),
            'high_absences': len(df[df['absences'] > 5]),
            'low_homework': len(df[df['homework_completion'] < 0.7])
        }

        dist = df['homework_completion'].value_counts(bins=5, sort=False)
        homework_dict = {str(interval): count for interval, count in dist.items()}

        # preparar dados para gráficos
        return jsonify({
            'stats': stats,
            'scatter_absences': df[['absences', 'math_score']].rename(
                columns={'absences': 'x', 'math_score': 'y'}).to_dict('records'),
            'scatter_participation': df[['participation', 'math_score']].rename(
                columns={'participation': 'x', 'math_score': 'y'}).to_dict('records'),
            'comparison': {
                'math': df['math_score'].tolist(),
                'language': df['language_score'].tolist(),
                'previous': df['previous_performance'].tolist()
            },
            'correlation': df.corr().round(2).to_dict(),
            'top_students': df.nlargest(10, 'math_score')[['student_id', 'math_score']].to_dict('records'),
            'homework_distribution': homework_dict
        })
        
    except Exception as e:
        logging.exception("erro ao processar dados do csv")
        return jsonify({
            "error": str(e),
            "details": "verifique o formato do arquivo csv"
        }), 500

@app.route('/dashboard/<path:path>')
def serve_static(path):
    return send_from_directory('dashboard', path)

def run_flask_app():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)@app.route('/dashboard/<path:path>')
def serve_static(path):
    return send_from_directory('dashboard', path)

async def executar_agentes():
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    logging.info("Servidor dashboard iniciado em http://localhost:5000/dashboard")

    agente_desempenho = AgenteDesempenho(
        os.getenv("JID_AGENTE_DESEMPENHO"),
        os.getenv("SENHA_AGENTE_DESEMPENHO")
    )
    await agente_desempenho.start()

    agente_central = AgenteCentral(
        os.getenv("JID_AGENTE_CENTRAL"),
        os.getenv("SENHA_AGENTE_CENTRAL")
    )
    await agente_central.start()

    print("\n" + "="*60)
    print("Sistema SMAP em execução")
    print(f"Dashboard disponível em: http://localhost:5000/dashboard")
    print("Pressione Ctrl+C para encerrar")
    print("="*60 + "\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agente_desempenho.stop()
        await agente_central.stop()


# A função executar_agentes foi modificada para apenas iniciar o Flask
async def executar_aplicacao_dashboard_apenas():
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    logging.info("Servidor dashboard iniciado em http://localhost:5000/dashboard")

    print("\n" + "=" * 60)
    print("Sistema SMAP em execução (Apenas Dashboard)")
    print(f"Dashboard disponível em: http://localhost:5000/dashboard")
    print("Pressione Ctrl+C para encerrar")
    print("=" * 60 + "\n")

    try:
        # Mantém o programa rodando para que o Flask continue ativo
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Aplicação encerrada pelo usuário.")
        # Não há agentes para parar aqui, então não é necessário chamar stop()

@app.route('/dashboard/api/student/<int:student_id>')
def student_dashboard_api(student_id):
    try:
        df = pd.read_csv('sample_data.csv')
        if df.empty:
            return jsonify({"error": "Arquivo CSV vazio"}), 400

        df['student_id'] = df['student_id'].astype(int)

        student_data = df[df['student_id'] == student_id].to_dict('records')
        if not student_data:
            return jsonify({"error": f"Aluno com ID {student_id} não encontrado"}), 404

        student = student_data[0]

        class_avg = df.mean(numeric_only=True).to_dict()

        return jsonify({
            'student_info': {
                'id': student['student_id'],
                'math_score': student['math_score'],
                'language_score': student['language_score'],
                'absences': student['absences'],
                'participation': student['participation'],
                'homework_completion': student['homework_completion'],
                'previous_performance': student['previous_performance']
            },
            'class_avg': {
                'math_score': class_avg['math_score'],
                'language_score': class_avg['language_score'],
                'absences': class_avg['absences'],
                'participation': class_avg['participation'],
                'homework_completion': class_avg['homework_completion'],
                'previous_performance': class_avg['previous_performance']
            }
        })
    except Exception as e:
        logging.exception(f"Erro ao processar dados do aluno {student_id}: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    # asyncio.run(executar_agentes())
    asyncio.run(executar_aplicacao_dashboard_apenas())

