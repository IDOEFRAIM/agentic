import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# On importe la classe logique que l'on vient de créer
from agent import AgileScrumEngine

app = FastAPI(
    title="Agile Scrum AI Server",
    description="API de gestion de projet automatisée via LangGraph et Llama 3",
    version="1.0.0"
)

# Initialisation de l'agent (on le crée une seule fois au lancement)
scrum_engine = AgileScrumEngine(model_name="llama3")

# --- MODÈLES DE DONNÉES (Pydantic) ---

class ProjectRequest(BaseModel):
    project_id: str
    description: str

class TaskUpdate(BaseModel):
    project_id: str
    story_id: str
    new_status: str

# --- ROUTES API ---

@app.get("/")
async def root():
    return {"message": "Serveur Agile Scrum AI opérationnel. Allez sur /docs pour Swagger."}

@app.post("/scrum/analyze", tags=["Agile Management"])
async def analyze_project(request: ProjectRequest):
    """
    Déclenche le cycle complet : Product Owner -> Scrum Master -> Persistance JSON.
    """
    try:
        # Lancement du graphe LangGraph
        result = scrum_engine.run_scrum_cycle(
            project_id=request.project_id, 
            text=request.description
        )
        
        return {
            "status": "success",
            "project_id": request.project_id,
            "data_summary": result["structured_data"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")

@app.get("/scrum/project/{project_id}", tags=["Project Data"])
async def get_project_data(project_id: str):
    """
    Récupère le fichier JSON actuel d'un projet.
    """
    import os
    import json
    
    path = f"agile_projects/{project_id}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Projet non trouvé")
        
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- LANCEMENT ---

if __name__ == "__main__":
    # Lancement du serveur sur le port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)