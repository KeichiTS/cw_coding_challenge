import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Crew, Process, LLM
from src.agents import InfinitePayAgents
from src.tasks import InfinitePayTasks
from dotenv import load_dotenv

load_dotenv()

manager_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

class MessageInput(BaseModel):
    message: str
    user_id: str = "client789"

app = FastAPI(
    title="InfinitePay Agent Swarm",
    description="API do Desafio Técnico - Arquitetura de Agentes"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_endpoint(payload: MessageInput):
    try:
        agents_factory = InfinitePayAgents()
        tasks_factory = InfinitePayTasks()

        router = agents_factory.router_agent()
        knowledge = agents_factory.knowledge_agent()
        support = agents_factory.support_agent()

        main_task = tasks_factory.router_task(router, payload.message, payload.user_id)

        crew = Crew(
            agents=[router, knowledge, support],
            tasks=[main_task],
            process=Process.hierarchical, 
            manager_llm=manager_llm,
            verbose=True,
            memory=False 
        )

        result = crew.kickoff()

        return {
            "response": result,
            "processed_by": "InfinitePay Swarm",
            "status": "success"
        }

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)