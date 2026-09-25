import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def analizar_contexto():
    # Obtiene la clave justo cuando llega el mensaje de Roblox
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY no encontrada en Render")
        return jsonify({"decision": "OK", "error": "Falta API Key"}), 500

    try:
        data = request.json or {}
        usuario = data.get("usuario", "Jugador")
        mensaje = data.get("prompt", "")

        # Inicializa el cliente únicamente dentro de la petición
        client = Groq(api_key=api_key)

        system_prompt = (
            "Eres un sistema de moderación para un juego de Roblox. "
            "Analiza el mensaje del jugador.\n\n"
            "REGLAS:\n"
            "1. Mensaje normal o inofensivo -> OK\n"
            "2. Mensaje tóxico, insulto o molestia -> REINICIAR\n"
            "3. Acoso grave, insultos muy fuertes u odio -> BANEAR\n\n"
            "Responde ÚNICAMENTE con una de estas palabras: OK, REINICIAR o BANEAR."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{usuario}: {mensaje}"}
            ],
            temperature=0.1,
        )

        decision = completion.choices[0].message.content.strip().upper()
        return jsonify({"decision": decision})

    except Exception as e:
        print("ERROR AL CONECTAR CON GROQ:", str(e))
        return jsonify({"decision": "OK", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
