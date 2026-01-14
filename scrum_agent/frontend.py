import gradio as gr
import requests
import json

# URL de ton serveur FastAPI
API_URL = "http://localhost:8000"

def run_agile_ai(project_id, description):
    """Appelle le serveur FastAPI pour générer le projet."""
    if not project_id or not description:
        return "⚠️ Veuillez remplir tous les champs.", None, None
    
    payload = {
        "project_id": project_id,
        "description": description
    }
    
    try:
        response = requests.post(f"{API_URL}/scrum/analyze", json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extraction des données structurées
        data = result["data_summary"]
        
        # Formatage pour l'affichage
        epics_text = "\n".join([f"• {e.get('title', 'Epic')}" for e in data.get('epics', [])])
        
        backlog_md = "### 📋 Product Backlog\n\n"
        for story in data.get('stories', []):
            backlog_md += f"**{story.get('title')}** ({story.get('points')} pts)\n"
            backlog_md += f"*{story.get('story')}*\n"
            backlog_md += f"- Tasks: {', '.join(story.get('tasks', []))}\n\n"
            
        return "✅ Analyse terminée !", epics_text, backlog_md
        
    except Exception as e:
        return f"❌ Erreur: {str(e)}", None, None

def get_existing_project(project_id):
    """Récupère les données d'un projet existant."""
    try:
        response = requests.get(f"{API_URL}/scrum/project/{project_id}")
        if response.status_code == 200:
            data = response.json()
            # Logique d'affichage similaire à run_agile_ai...
            return "📂 Projet chargé", str(data.get('epics')), str(data.get('backlog'))
        return "🔍 Projet non trouvé", "", ""
    except:
        return "❌ Connexion serveur impossible", "", ""

# --- CONSTRUCTION DE L'INTERFACE GRADIO ---

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# 🚀 AgriConnect - AI Scrum Master")
    gr.Markdown("Transformez vos idées brutes en un projet Agile complet (Epics, Stories, Tasks).")
    
    with gr.Row():
        with gr.Column(scale=1):
            project_id = gr.Textbox(label="ID du Projet", placeholder="ex: AgriConnect_V2")
            description = gr.Textbox(
                label="Description du besoin", 
                placeholder="Décrivez votre idée ici...",
                lines=5
            )
            btn_generate = gr.Button("⚡ Générer le Backlog", variant="primary")
            status = gr.Textbox(label="Statut", interactive=False)
            
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("📊 Vue d'ensemble (Epics)"):
                    output_epics = gr.Textbox(label="Grands thèmes identifiés", lines=5)
                
                with gr.TabItem("📝 Backlog Détaillé"):
                    output_backlog = gr.Markdown()

    # Événements
    btn_generate.click(
        fn=run_agile_ai,
        inputs=[project_id, description],
        outputs=[status, output_epics, output_backlog]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)