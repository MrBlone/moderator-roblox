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

        # Ver mensaje en los logs de Render
        print(f"--> MENSAJE RECIBIDO DE ROBLOX | Usuario: {usuario} | Texto: '{mensaje}'")

        if not mensaje:
            return jsonify({"decision": "OK"}), 200

        client = Groq(api_key=api_key)

        system_prompt = (
            "Eres un moderador estricto de chat para un juego de Roblox. "
            "Clasifica el mensaje en una sola palabra:\n\n"
            "- REINICIAR: Si el mensaje contiene insultos, palabras tóxicas, groserías o faltas de respeto leves/moderadas.\n"
            "- BANEAR: Si el mensaje contiene amenazas, deseos de muerte, acoso grave o discriminación.\n"
            "- OK: ÚNICAMENTE si el mensaje es completamente inofensivo o charla normal del juego.\n\n"
            "REGLA OBLIGATORIA: Responde SOLO con una de las palabras: OK, REINICIAR o BANEAR."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Mensaje de {usuario}: {mensaje}"}
            ],
            temperature=0.0,
        )

        respuesta = completion.choices[0].message.content.strip().upper()
        print(f"--> DECISION DE GROQ: '{respuesta}'")

        if "BANEAR" in respuesta:
            decision = "BANEAR"
        elif "REINICIAR" in respuesta:
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
