import gradio as gr
import requests

def ask_fastapi(question):
    # L'URL de ton backend FastAPI
    url = "http://localhost:8000/analyze"
    
    try:
        # Envoi de la requête à FastAPI
        payload = {"question": question}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Erreur Serveur: {response.status_code}"
    except Exception as e:
        return f"Connexion impossible au Backend : {e}"

# Interface Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌐 Client Interface - Marketing AI-TANKA IDO")
    gr.Markdown("Cette interface communique avec un serveur FastAPI distant via HTTP:-)")
    
    with gr.Row():
        input_text = gr.Textbox(label="Votre projet", placeholder="Entrez votre idée...")
        output_text = gr.Markdown(label="Réponse de l'expert")
    
    submit_btn = gr.Button("Envoyer au Serveur")
    submit_btn.click(fn=ask_fastapi, inputs=input_text, outputs=output_text)

if __name__ == "__main__":
    demo.launch()