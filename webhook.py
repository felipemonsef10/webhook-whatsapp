from flask import Flask, request, abort
from src.data_manipulation import pipeline_data_processing

app = Flask(__name__)


@app.route('/', methods=['POST'])
def receber_dados_whatsapp():
    if request.method == 'POST':
        body = request.json
        typeWebhook = body.get('typeWebhook', '')
    
        if typeWebhook == 'incomingMessageReceived':
            print(body)
            
        return 'ok', 200
    else:
        return abort(400)


if __name__ == '__main__':
    app.run(debug=True)