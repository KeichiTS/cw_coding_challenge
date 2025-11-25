import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Crew, Process
from supabase import create_client, Client
from src.agents import InfinitePayAgents
from src.tasks import InfinitePayTasks
from src.guardrails import input_guardrail
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class MessageInput(BaseModel):
    message: str
    user_id: str = "client789"
    session_id: str = "default_session"

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

def log_message(session_id: str, user_id: str, direction: str, message: str):
    try:
        supabase.table("chat_logs").insert({
            "session_id": session_id,
            "user_id": user_id,
            "direction": direction,
            "message": message
        }).execute()
    except Exception as e:
        print(f"ERRO DE LOG: {e}")

@app.post("/api/chat")
async def chat_endpoint(payload: MessageInput, background_tasks: BackgroundTasks):
    try:
        
        is_safe, refusal_message = input_guardrail(payload.message)
        
        if not is_safe:
            background_tasks.add_task(
                log_message, payload.session_id, payload.user_id, "user", payload.message
            )
            background_tasks.add_task(
                log_message, payload.session_id, payload.user_id, "assistant", f"[BLOCKED]: {refusal_message}"
            )
            
            return {
                "response": refusal_message,
                "status": "blocked"
            }
        
        background_tasks.add_task(
            log_message, 
            payload.session_id, 
            payload.user_id, 
            "user", 
            payload.message
        )
        
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
        final_response = str(result)

        background_tasks.add_task(
            log_message, 
            payload.session_id, 
            payload.user_id, 
            "assistant", 
            final_response
        )

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

@app.get("/api/history/{session_id}")
async def get_history(session_id: str, user_id: str):
    """
    Recupera o histórico se o session_id pertencer ao user_id informado.
    """
    try:
        response = supabase.table("chat_logs")\
            .select("direction, message")\
            .eq("session_id", session_id)\
            .eq("user_id", user_id)\
            .order("created_at", desc=False)\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)