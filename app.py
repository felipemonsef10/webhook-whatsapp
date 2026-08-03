from flask import Flask, request, abort, jsonify
import os
from pathlib import Path
import json
from dotenv import load_dotenv
from src.data_manipulation import pipeline_data_processing
load_dotenv()

app = Flask(__name__)

OUTPUT_DIR = os.getenv('OUTPUT_DIR', '')
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '')


def obter_dados_json(dir_output: str, path_output: str) -> list:
    abs_path_output =  Path(dir_output)/ path_output
    
    lista_dados = []
    
    if os.path.exists(abs_path_output):
        with open(abs_path_output, 'r+', encoding='utf-8') as list_json_file:
            lista_dados = json.load(list_json_file)
    
    return lista_dados


def salvar_json(dict_json: dict, dir_output: str, path_output: str) -> None:
    Path(dir_output).mkdir(exist_ok=True)
    abs_path_output =  Path(dir_output)/ path_output
    
    if os.path.exists(abs_path_output):
        lista_dados = obter_dados_json(dir_output, path_output)
        lista_dados.append(dict_json)
    else:
        lista_dados = [dict_json]
        
    with open(abs_path_output, 'w+', encoding='utf-8') as json_file:
        json.dump(lista_dados, json_file, indent=4, ensure_ascii=False)


@app.route('/webhook', methods=['POST'])
def receber_dados_whatsapp():
    if request.method == 'POST':
        body = request.json
        typeWebhook = body.get('typeWebhook', '')
    
        if typeWebhook == 'incomingMessageReceived':
            try:
                salvar_json(body, OUTPUT_DIR, OUTPUT_PATH)
            except Exception as e:
                return 'requisição inválida', abort(500)
            
        return 'dados salvos com sucesso', 200
    else:
        return 'requisição inválida', abort(400)


@app.route('/api', methods=['GET'])
def enviar_dados_whatsapp():
    if request.method == 'GET':
        dados_json = obter_dados_json(OUTPUT_DIR, OUTPUT_PATH)
        if len(dados_json) > 0:
            return jsonify(dados_json), 200
        else:
            return jsonify(['sem dados']), 200
    else:
        return 'requisição inválida', abort(400)
    

if __name__ == '__main__':
    app.run(debug=True)