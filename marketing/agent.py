from typing import TypedDict, Optional, List
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# State enrichi,c est comme ton cahier de note, tu mets les info du cours laba et tu adapte au fur et a mesure
class MarketingState(TypedDict):
    question: str
    plan: Optional[str]
    ads: Optional[str]
    feedback: Optional[str]
    final_output: Optional[str]

# NODE 1 : LE STRATÈGE 
def strategy_node(state: MarketingState):
    llm = ChatOllama(model='llama3', temperature=0.2)
    prompt = (
        "Tu es un Stratège Marketing. Crée un plan macro (Cible, Canal, Budget).\n"
        "Exemple : Question: 'Vente de vélos' -> [Plan] Cible: Cyclistes urbains. Canal: Instagram. Budget: 500€/mois."
    )
    res = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=state['question'])])
    return {"plan": res.content}

#NODE 2 : LE COPYWRITER (Automatique) 
def copywriter_node(state: MarketingState):
    llm = ChatOllama(model='llama3', temperature=0.7) # Plus créatif
    prompt = f"Tu es un Copywriter. Basé sur ce plan : {state['plan']}, rédige 2 annonces percutantes."
    res = llm.invoke([SystemMessage(content=prompt)])
    return {"ads": res.content}

# NODE 3 : L'ANALYSTE CRITIQUE 
def analyst_node(state: MarketingState):
    llm = ChatOllama(model='llama3', temperature=0.1)
    prompt = f"Tu es un Analyste. Fusionne le plan et les annonces dans un rapport final structuré. Sois critique."
    res = llm.invoke([SystemMessage(content=prompt), 
                      HumanMessage(content=f"Plan: {state['plan']}\nAds: {state['ads']}")])
    return {"final_output": res.content}

#  CONSTRUCTION DU GRAPH:l orchestration de ces agents
workflow = StateGraph(MarketingState)

workflow.add_node("strategist", strategy_node)
workflow.add_node("copywriter", copywriter_node)
workflow.add_node("analyst", analyst_node)

# Flux de travail automatisé
workflow.set_entry_point("strategist")
workflow.add_edge("strategist", "copywriter")
workflow.add_edge("copywriter", "analyst")
workflow.add_edge("analyst", END)

app = workflow.compile()

result = app.invoke({'question': 'Je vends des voitures d’occasion haut de gamme à Casablanca'})
print(result['final_output'])