import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration (Ces valeurs seront sur Render)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "votre_code_secret")
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

def envoyer_message(destinataire, texte):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": destinataire,
        "type": "text",
        "text": {"body": texte}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route("/webhook", methods=["GET"])
def verifier():
    # Validation exigée par Meta
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erreur de token", 403

@app.route("/webhook", methods=["POST"])
def reception():
    data = request.get_json()
    
    try:
        # On vérifie si c'est bien un message texte
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            message = entry['messages'][0]
            expediteur = message['from']
            texte = message['text']['body'].lower().strip()

            # Logique simple de commande
            if texte == "menu":
                reponse = "Voici notre catalogue :\n- Pizza (10$)\n- Burger (8$)\n- Soda (2$)\n\nTapez le nom de l'article pour commander."
            elif texte in ["pizza", "burger", "soda"]:
                reponse = f"✅ Commande enregistrée : 1 {texte}. Nous vous contacterons pour la livraison."
            else:
                reponse = "Bienvenue ! Envoyez 'Menu' pour voir nos produits."

            envoyer_message(expediteur, reponse)
    except:
        pass



    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 
