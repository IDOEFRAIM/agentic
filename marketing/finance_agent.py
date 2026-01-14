from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

class FinanceState(TypedDict):
    raw_data: str
    ratios: Optional[str]
    risks: Optional[str]
    final_report: Optional[str]

# NODE 1 : L'ANALYSTE QUANTITATIF 
def quantitative_node(state: FinanceState):
    llm = ChatOllama(model='llama3', temperature=0) # Précision maximale (0)
    system_prompt = (
        "Tu es un Analyste Quantitatif. Ta mission est d'extraire les chiffres clés et "
        "calculer les ratios : Marge Net, Ratio de Liquidité, et Endettement.\n"
        "Exemple: 'CA: 100k, Profit: 20k' -> Ratios: Marge 20%."
    )
    res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=state['raw_data'])])
    return {"ratios": res.content}

# NODE 2 : LE RISK MANAGER (Audit interne) 
def risk_node(state: FinanceState):
    llm = ChatOllama(model='llama3', temperature=0.1)
    system_prompt = (
        "Tu es un Risk Manager. Analyse les ratios fournis pour détecter des anomalies ou des risques de faillite."
    )
    res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=f"Ratios: {state['ratios']}")])
    return {"risks": res.content}

# NODE 3 : LE CONSEILLER EN INVESTISSEMENT
def advisor_node(state: FinanceState):
    llm = ChatOllama(model='llama3', temperature=0.5)
    system_prompt = (
        "Tu es un Conseiller Financier. Basé sur les ratios et les risques, "
        "rédige une recommandation d'investissement finale (Acheter / Conserver / Vendre)."
    )
    content = f"Analyse Tech: {state['ratios']}\nAnalyse Risque: {state['risks']}"
    res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=content)])
    return {"final_report": res.content}

# CONSTRUCTION DU WORKFLOW FINANCIER 
workflow = StateGraph(FinanceState)

workflow.add_node("quant", quantitative_node)
workflow.add_node("risk", risk_node)
workflow.add_node("advisor", advisor_node)

workflow.set_entry_point("quant")
workflow.add_edge("quant", "risk")
workflow.add_edge("risk", "advisor")
workflow.add_edge("advisor", END)

app = workflow.compile()

# Simulation avec des données brutes de l'entreprise
raw_finances = "CA 2025: 500M$, Dette: 450M$, Cash flow: -10M$, Secteur: AgriTech"
result = app.invoke({"raw_data": raw_finances})

print(result['final_report'])