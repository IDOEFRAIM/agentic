from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

app = FastAPI()

class MarketingState(TypedDict):
    question: str
    final_output: Optional[str]

# --- Logique simplifiée pour l'exemple ---
def marketing_workflow(state: MarketingState):
    llm = ChatOllama(model='llama3', temperature=0.2)
    res = llm.invoke([SystemMessage(content="Tu es une agence marketing complète."), 
                      HumanMessage(content=state['question'])])
    return {"final_output": res.content}

builder = StateGraph(MarketingState)
builder.add_node("agent", marketing_workflow)
builder.set_entry_point("agent")
builder.add_edge("agent", END)
graph = builder.compile()

class Query(BaseModel):
    question: str

@app.post("/analyze")
async def analyze(query: Query):
    result = graph.invoke({"question": query.question})
    return {"response": result["final_output"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)