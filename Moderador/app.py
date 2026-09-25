import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def analizar_contexto():
    try:
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            print("ERROR: GROQ_API_KEY no encontrada.")
            return jsonify({"decision": "OK", "error": "No API Key"}), 200

        # Obtener los datos enviados por Roblox
        data = request.get_json(force=True, silent=True) or {}
        usuario = str(data.get("usuario", "Jugador"))
        mensaje = str(data.get("prompt", "")).strip()

        # Si el mensaje está vacío, responder OK inmediatamente sin llamar a Groq
        if not mensaje:
            return jsonify({"decision": "OK"}), 200

        # Crear el cliente de Groq
        client = Groq(api_key=api_key)

        system_prompt = (
            "Eres un sistema de moderación de chat para Roblox. "
            "Analiza el mensaje enviado por el usuario.\n\n"
            "REGLAS:\n"
            "1. Si el mensaje es inofensivo, normal o conversación común -> OK\n"
            "2. Si es tóxico, un insulto leve o molestia -> REINICIAR\n"
            "3. Si es acoso grave, insulto muy fuerte, odio o amenazas -> BANEAR\n\n"
            "Responde ÚNICAMENTE con una de las tres palabras: OK, REINICIAR o BANEAR. No agregues nada más."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Usuario: {usuario}\nMensaje: \"{mensaje}\""}
            ],
            temperature=0.1,
        )

        decision = completion.choices[0].message.content.strip().upper()
        
        # Limpiar la respuesta por si el modelo devuelve algo extra
        if "REINICIAR" in decision:
            decision = "REINICIAR"
        elif "BANEAR" in decision:
            decision = "BANEAR"
        else:
            decision = "OK"

        print(f"[{usuario}]: \"{mensaje}\" -> DECISION: {decision}")
        return jsonify({"decision": decision}), 200

    except Exception as e:
        # En caso de cualquier falla imprevista, atrapa el error y responde OK con código HTTP 200
        print("EXCEPCION EN PYTHON:", str(e))
        return jsonify({"decision": "OK", "error": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
