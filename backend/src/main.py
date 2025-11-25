import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Crew, Process
from src.agents import InfinitePayAgents
from src.tasks import InfinitePayTasks
from dotenv import load_dotenv

load_dotenv()

class MessageInput(BaseModel):
    message: str
    user_id: str = "client789"

app = FastAPI(
    title="InfinitePay Agent Swarm",
    description="API do Desafio Técnico - Arquitetura Sovereign Router"
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
        
        main_task = tasks_factory.router_task(router, payload.message, payload.user_id)

        crew = Crew(
            agents=[router], 
            tasks=[main_task],
            process=Process.sequential, 
            verbose=True,
            memory=False 
        )

        result = crew.kickoff()

        return {
            "response": str(result),
            "processed_by": "InfinitePay Swarm (Router -> Tool)",
            "status": "success"
        }

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)