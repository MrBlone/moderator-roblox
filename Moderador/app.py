import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def analizar_contexto():
    try:
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            return jsonify({"decision": "OK", "error": "No API Key"}), 200

        data = request.get_json(force=True, silent=True) or {}
        usuario = str(data.get("usuario", "Jugador"))
        mensaje = str(data.get("prompt", "")).strip()

        print(f"--> MENSAJE RECIBIDO DE ROBLOX | Usuario: {usuario} | Texto: '{mensaje}'")

        if not mensaje:
            return jsonify({"decision": "OK"}), 200

        client = Groq(api_key=api_key)

        system_prompt = (
            "Eres un moderador estricto para un juego de Roblox. "
            "Clasifica el mensaje del jugador en una de las siguientes categorías:\n\n"
            "- OK: Saludos, charla normal, juego o frases inofensivas.\n"
            "- REINICIAR: Insultos leves, groserías, toxicidad o molestias.\n"
            "- BANEAR: Amenazas de muerte, acoso grave, discriminación o insultos muy fuertes.\n\n"
            "REGLA OBLIGATORIA: Responde ÚNICAMENTE con la palabra exacta: OK, REINICIAR o BANEAR. No escribas nada más."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Mensaje de {usuario}: {mensaje}"}
            ],
            temperature=0.0,
        )

        respuesta_raw = completion.choices[0].message.content.strip().upper()
        print(f"--> RESPUESTA DE GROQ: '{respuesta_raw}'")

        if "BANEAR" in respuesta_raw:
            decision = "BANEAR"
        elif "REINICIAR" in respuesta_raw:
            decision = "REINICIAR"
        else:
            decision = "OK"

        return jsonify({"decision": decision}), 200

    except Exception as e:
        print("EXCEPCION EN PYTHON:", str(e))
        return jsonify({"decision": "OK", "error": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
