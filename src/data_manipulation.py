import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from pathlib import Path


def load_and_filter_data_msg(json_msg: dict) -> dict[str, str | pd.DataFrame]:
    dict_info_msg = {}
    chat_name = json_msg.get('senderData', '').get('chatName', '')
    type_message = json_msg.get('messageData', '').get('typeMessage', '')
    
    dict_info_msg['typeMessage'] = type_message
    
    if 'PRAÇA' in chat_name:

        if (type_message == 'textMessage'):
            text_message_data = json_msg.get('messageData', '').get('textMessageData', '').get('textMessage', '')
            
            dict_info_msg['textMessage'] = text_message_data + '\n'
        
        elif (type_message == 'extendedTextMessage'):
            text_extended_message_data = json_msg.get('messageData', '').get('extendedTextMessageData', '').get('text', '')
            
            dict_info_msg['textMessage'] =  text_extended_message_data + '\n'
            
        elif (type_message == 'imageMessage'):
            caption_image_message = json_msg.get('messageData', '').get('fileMessageData').get('caption')
            
            if  len(caption_image_message) > 1:
                dict_info_msg['textMessage'] = caption_image_message + '\n'
        
            else:
                return {'status': f'texto da foto menor que 2 caracteres: {len(caption_image_message)}', 'df': pd.DataFrame()}
        else:
            return {'status': f'tipo da mensagem não está selecionado: {type_message}', 'df': pd.DataFrame()}
    
        dict_info_msg['idMessage'] = json_msg.get('idMessage', '')
        dict_info_msg['timestamp'] = json_msg.get('timestamp', '')
        dict_info_msg['chatId'] = json_msg.get('senderData', '').get('chatId', '')
        dict_info_msg['chatName'] = chat_name
        dict_info_msg['sender'] = json_msg.get('senderData', '').get('sender', '')
        
        dict_info_msg = {k: [v] for k, v in dict_info_msg.items()}
        df = pd.DataFrame(dict_info_msg)
        
        return {'status': 'ok', 'df': df}
    else:
        return {'status': f'grupo não é praça: {chat_name}', 'df': pd.DataFrame()}


def data_processing_msg(df: pd.DataFrame) -> pd.DataFrame:
    fuso_br = ZoneInfo('America/Sao_Paulo')
    df['data_captura'] = datetime.now().astimezone(tz=fuso_br).replace(microsecond=0)
    df['data_mensagem'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
    
    return df


def save_data(df: pd.DataFrame, path: str | Path) -> None:
    mode='w'
    header = True
    if os.path.exists(path):
        mode='a'
        header=False
    
    df.to_csv(path, sep=';', index=False, header=header, mode=mode, encoding='utf-8')


def pipeline_data_processing(json_msg: dict, path: str | Path) -> dict[str, str | pd.DataFrame]:
    dict_data_loaded = load_and_filter_data_msg(json_msg)
    status_registro = dict_data_loaded.get('status', '')
    df_registro = dict_data_loaded.get('df', '')
    
    if status_registro == 'ok': # type: ignore
        df_registro = data_processing_msg(df_registro) # type: ignore
        save_data(df_registro, path)
        return {'status': 'pipeline executada com sucesso', 'df': df_registro}
    else:
        return {'status': f'pipeline não executada: {status_registro}', 'df': pd.DataFrame()}