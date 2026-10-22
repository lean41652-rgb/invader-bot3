import os
from flask import Flask, request
import requests

app = Flask(__name__)
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
sesiones = {}

MENSAJE_FINAL = "✅ Perfecto. Registramos: *{ruta}*\n\nEn breve serás conectado con un técnico de Invader Hardware. Quedate en línea."

def enviar_texto(numero, texto):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    h = {"Authorization": f"Bearer {TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": numero, "text": {"body": texto}}
    requests.post(url, headers=h, json=data)

def enviar_lista(numero, titulo, body, opciones):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    h = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": titulo},
            "body": {"text": body},
            "footer": {"text": "Invader Hardware - Comodoro"},
            "action": {
                "button": "Ver opciones",
                "sections": [{"title": "Servicios", "rows": opciones}]
            }
        }
    }
    requests.post(url, headers=h, json=data)

def enviar_botones(numero, texto, botones):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    h = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {"buttons": [{"type": "reply", "reply": b} for b in botones]}
        }
    }
    requests.post(url, headers=h, json=data)

# --- MENÚS ---
def menu_principal(numero):
    opciones = [
        {"id": "1", "title": "1. Computadoras", "description": "Portátiles y Escritorio"},
        {"id": "2", "title": "2. Celulares/Tablets", "description": "Solo Android"},
        {"id": "3", "title": "3. Consolas Portátiles", "description": "Switch, Steam Deck"},
        {"id": "4", "title": "4. Play / Xbox", "description": "Consolas y joysticks"},
        {"id": "5", "title": "5. Televisores", "description": "Smart y LED"},
        {"id": "6", "title": "6. Parlantes", "description": "Bluetooth y equipos"},
        {"id": "7", "title": "7. Electrónica", "description": "Varios"},
        {"id": "8", "title": "8. Impresoras", "description": "Tinta, láser, térmicas"},
        {"id": "9", "title": "9. Hablar con técnico", "description": "Atención directa"},
    ]
    enviar_lista(numero, "Invader Hardware 🔧", "Hola! Te comunicaste con el servicio técnico. ¿Qué servicio necesitas?", opciones)

def menu_computadoras(numero):
    enviar_botones(numero, "💻 COMPUTADORAS - ¿Qué equipo es?", [
        {"id": "1_1", "title": "Portátil"},
        {"id": "1_2", "title": "Escritorio"}
    ])

def menu_fallas_pc(numero):
    opciones = [
        {"id": "f_1", "title": "1. PC lento"}, {"id": "f_2", "title": "2. No da imagen"},
        {"id": "f_3", "title": "3. No enciende"}, {"id": "f_4", "title": "4. Sin sistema"},
        {"id": "f_5", "title": "5. Actualización"}, {"id": "f_6", "title": "6. Mantenimiento"},
        {"id": "f_7", "title": "7. Cambio piezas"}, {"id": "f_8", "title": "8. Revisión técnica"},
        {"id": "f_9", "title": "9. Bisagras"}, {"id": "f_10", "title": "10. Hardware"},
    ]
    enviar_lista(numero, "Falla de PC", "Seleccioná la falla de tu computadora:", opciones)

def menu_celulares(numero):
    enviar_botones(numero, "📱 CELULAR o TABLET? (Solo Android)", [
        {"id": "2_1", "title": "Celular"},
        {"id": "2_2", "title": "Tablet"}
    ])

def menu_fallas_cel(numero):
    opciones = [
        {"id": "c_1", "title": "1. No enciende"}, {"id": "c_2", "title": "2. Pantalla rota"},
        {"id": "c_3", "title": "3. No carga"}, {"id": "c_4", "title": "4. Sin sonido"},
        {"id": "c_5", "title": "5. No conecta WiFi"}, {"id": "c_6", "title": "6. Lento"},
        {"id": "c_7", "title": "7. Reinicia solo"}, {"id": "c_8", "title": "8. No se apaga"},
    ]
    enviar_lista(numero, "Falla de Celular", "Seleccioná la falla de tu equipo:", opciones)

# --- LOGICA ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json['entry'][0]['changes'][0]['value']
    if 'messages' not in data: return "ok", 200
    
    msg = data['messages'][0]
    numero = msg['from']
    
    if msg['type'] == 'interactive':
        if 'list_reply' in msg['interactive']:
            texto = msg['interactive']['list_reply']['id']
        else:
            texto = msg['interactive']['button_reply']['id']
    else:
        texto = msg['text']['body'].strip()

    # LOGICA
    if texto == "0" or texto.lower() == "menu":
        sesiones[numero] = []
        menu_principal(numero)
        return "ok", 200

    if not sesiones.get(numero): # Principal
        if texto == "1":
            sesiones[numero] = ["1"]
            menu_computadoras(numero)
        elif texto == "2":
            sesiones[numero] = ["2"]
            menu_celulares(numero)
        elif texto in ["3","4","5","6","7","8"]:
            sesiones[numero] = [texto]
            enviar_texto(numero, "Anotado. Elegí la falla específica:")
            menu_fallas_pc(numero) # ejemplo
        elif texto == "9":
            enviar_texto(numero, MENSAJE_FINAL.format(ruta="Hablar con técnico directo"))
            sesiones[numero] = []
        else:
            menu_principal(numero)
    
    elif sesiones[numero] == ["1"]: # eligió compu
        sesiones[numero] = ["1", texto] # ["1", "1_1"]
        menu_fallas_pc(numero)

    elif sesiones[numero] == ["2"]: # eligió celular
        sesiones[numero] = ["2", texto]
        menu_fallas_cel(numero)

    else: # Ya es una falla final
        enviar_texto(numero, MENSAJE_FINAL.format(ruta=f"Opción {texto}"))
        sesiones[numero] = []
        enviar_texto(numero, "Si querés volver a iniciar, escribí *MENU*")

    return "ok", 200

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == "invader123":
        return request.args.get("hub.challenge")
    return "error", 403

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
