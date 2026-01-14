import json
import os
import operator
from typing import Annotated, List, TypedDict, Union, Sequence
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# --- 1. DÉFINITION DE L'ÉTAT DU PROJET ---
class AgileState(TypedDict):
    project_id: str
    raw_input: str
    structured_data: dict  # Contient Epics, Stories, Tasks
    messages: Annotated[Sequence[BaseMessage], operator.add]
    status: str

# --- 2. LA CLASSE LOGIQUE UNIVERSELLE ---
class AgileScrumEngine:
    def __init__(self, model_name: str = "llama3"):
        self.llm = ChatOllama(model=model_name, temperature=0.1, format="json")
        self.projects_dir = "agile_projects"
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

    def _get_project_path(self, project_id: str):
        return os.path.join(self.projects_dir, f"{project_id}.json")

    # --- NOEUD 1 : LE PRODUCT OWNER (Extraction des Epics & Stories) ---
    def node_product_owner(self, state: AgileState):
        prompt = (
            "Tu es un Product Owner Expert. Analyse la description brute et décompose-la en : \n"
            "1. Epics (Grands thèmes)\n"
            "2. User Stories (En tant que... je veux... afin de...)\n"
            "3. Critères d'acceptation pour chaque story.\n"
            "Réponds UNIQUEMENT sous forme de JSON structuré."
        )
        
        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Projet: {state['project_id']}\nDescription: {state['raw_input']}")
        ])
        
        return {"structured_data": json.loads(response.content), "status": "analyzed"}

    # --- NOEUD 2 : LE SCRUM MASTER (Estimation & Tâches Techniques) ---
    def node_scrum_master(self, state: AgileState):
        # On reprend les données du PO pour ajouter les points et les tâches
        current_data = state["structured_data"]
        
        prompt = (
            "Tu es un Scrum Master et Architecte. Pour chaque User Story fournie :\n"
            "1. Assigne des Story Points (Fibonacci: 1, 2, 3, 5, 8, 13).\n"
            "2. Décompose chaque Story en 'Technical Tasks' concrètes pour le développeur.\n"
            "3. Détermine une priorité (High, Medium, Low).\n"
            "Réponds UNIQUEMENT sous forme de JSON complété."
        )
        
        response = self.llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=json.dumps(current_data))
        ])
        
        return {"structured_data": json.loads(response.content), "status": "refined"}

    # --- NOEUD 3 : PERSISTENCE (Écriture JSON) ---
    def node_persistence(self, state: AgileState):
        project_id = state["project_id"]
        path = self._get_project_path(project_id)
        
        new_data = state["structured_data"]
        
        # Gestion de l'historique (Merge avec l'existant si nécessaire)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            # Logique de fusion simple : on ajoute au backlog existant
            old_data["backlog"].extend(new_data.get("stories", []))
            final_json = old_data
        else:
            final_json = {
                "project_id": project_id,
                "epics": new_data.get("epics", []),
                "backlog": new_data.get("stories", []),
                "sprints": [],
                "definition_of_done": ["Tests unitaires OK", "Code review faite", "Doc à jour"]
            }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=4, ensure_ascii=False)
            
        return {"status": "persisted"}

    # --- ORCHESTRATION LANGGRAPH ---
    def create_workflow(self):
        workflow = StateGraph(AgileState)

        # Ajout des nœuds
        workflow.add_node("analyze_requirements", self.node_product_owner)
        workflow.add_node("refine_and_estimate", self.node_scrum_master)
        workflow.add_node("save_to_json", self.node_persistence)

        # Liaison des nœuds (Le Flux Agile)
        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", "refine_and_estimate")
        workflow.add_edge("refine_and_estimate", "save_to_json")
        workflow.add_edge("save_to_json", END)

        return workflow.compile()

    # --- FONCTION UTILITAIRE POUR LE SERVEUR ---
    def run_scrum_cycle(self, project_id: str, text: str):
        app = self.create_workflow()
        inputs = {"project_id": project_id, "raw_input": text, "messages": []}
        return app.invoke(inputs)