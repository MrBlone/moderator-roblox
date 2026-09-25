import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def analizar_contexto():
    # Obtiene la variable guardada en Render
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("ERROR: No se encontró la variable GROQ_API_KEY en Render")
        return jsonify({"decision": "OK", "error": "Falta la API Key"}), 500

    try:
        # Crea el cliente con la clave
        client = Groq(api_key=api_key)

        data = request.json or {}
        usuario = data.get("usuario", "Jugador")
        mensaje = data.get("prompt", "")

        system_prompt = (
            "Eres un sistema de moderación silencioso para Roblox. "
            "Analiza el mensaje recibido.\n\n"
            "REGLAS:\n"
            "1. Mensaje normal o inofensivo -> OK\n"
            "2. Mensaje tóxico o insultante -> REINICIAR\n"
            "3. Acoso grave o insultos fuertes -> BANEAR\n\n"
            "Responde ÚNICAMENTE con una palabra: OK, REINICIAR o BANEAR."
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
        print("ERROR EXPLICITO DE GROQ:", str(e))
        return jsonify({"decision": "OK", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
