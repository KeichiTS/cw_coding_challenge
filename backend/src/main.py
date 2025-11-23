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

app = FastAPI(title="InfinitePay Agent")

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
        inputs = {
            "query": payload.message,
            "user_id": payload.user_id
        }

        agents_factory = InfinitePayAgents()
        universal_agent = agents_factory.universal_agent()

        tasks_factory = InfinitePayTasks()
        task = tasks_factory.handle_user_request_task(universal_agent)

        crew = Crew(
            agents=[universal_agent],
            tasks=[task],
            process=Process.sequential, 
            verbose=True,
            memory=False
        )

        result = crew.kickoff(inputs=inputs)

        return {
            "response": result,
            "status": "success"
        }

    except Exception as e:
        print(f"ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)