import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Lee la clave guardada en la pestaña 'Environment' de Render
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

historial_chat = []

@app.route('/chat', methods=['POST'])
def analizar_contexto():
    global historial_chat
    data = request.json or {}
    usuario = data.get("usuario", "Jugador")
    mensaje = data.get("prompt", "")

    # Mantiene los últimos 6 mensajes del historial
    historial_chat.append(f"{usuario}: {mensaje}")
    if len(historial_chat) > 6:
        historial_chat.pop(0)

    contexto_texto = "\n".join(historial_chat)

    system_prompt = (
        "Eres un sistema de moderación silencioso para un juego de Roblox. "
        "Tu única tarea es analizar el último mensaje enviado dentro del contexto de la conversación reciente.\n\n"
        "REGLAS DE EVALUACIÓN:\n"
        "1. Si el último mensaje es normal, juego limpio, broma sana o inofensivo -> Responde: OK\n"
        "2. Si el mensaje es tóxico, insultante, busca hacer sentir mal a alguien o se malinterpreta con mala intención -> Responde: REINICIAR\n"
        "3. Si el mensaje contiene acoso grave, insultos muy fuertes u odio -> Responde: BANEAR\n\n"
        "Responde ÚNICAMENTE con una de las tres palabras: OK, REINICIAR o BANEAR. No agregues explicaciones."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"HISTORIAL RECIENTE:\n{contexto_texto}\n\nEVALUAR ÚLTIMO MENSAJE DE {usuario}: \"{mensaje}\""}
            ],
            temperature=0.1,
        )
        
        decision = completion.choices[0].message.content.strip().upper()
        return jsonify({"decision": decision})
    except Exception as e:
        print("ERROR DE GROQ:", str(e))
        return jsonify({"decision": "OK", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
