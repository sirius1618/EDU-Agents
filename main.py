import asyncio
import os
import logging
from dotenv import load_dotenv
from agents.analise_desenpenho.agente_spade import AgenteDesempenho

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("spade")
logger.setLevel(logging.DEBUG)

load_dotenv() 

async def executar_agentes():
    agente = AgenteDesempenho(
        os.getenv("JID_AGENTE_DESEMPENHO"),
        os.getenv("SENHA_AGENTE_DESEMPENHO"),
    )
    
    await agente.start()
    print("Agente em execução. Pressione Ctrl+C para encerrar.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agente.stop()

if __name__ == "__main__":
    asyncio.run(executar_agentes())
