import asyncio
import os
import logging
from dotenv import load_dotenv
from agents.analise_desenpenho.agente_spade import AgenteDesempenho
from agents.agente_central.agente_spade import AgenteCentral

# Configurar logs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

async def executar_agentes():
    # Agente de Desempenho
    agente_desempenho = AgenteDesempenho(
        os.getenv("JID_AGENTE_DESEMPENHO"),
        os.getenv("SENHA_AGENTE_DESEMPENHO")
    )
    await agente_desempenho.start()

    # Agente Central
    agente_central = AgenteCentral(
        os.getenv("JID_AGENTE_CENTRAL"),
        os.getenv("SENHA_AGENTE_CENTRAL")
    )
    await agente_central.start()

    print("Sistema SMAP em execução. Pressione Ctrl+C para encerrar.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agente_desempenho.stop()
        await agente_central.stop()

if __name__ == "__main__":
    asyncio.run(executar_agentes())
