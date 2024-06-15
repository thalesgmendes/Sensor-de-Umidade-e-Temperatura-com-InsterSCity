import time
import pandas as pd
from datetime import datetime
from paho.mqtt import client as mqtt_client

# Configurações de conexão ao Broker
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic_subscribe = "livingroom/temperature"
client_id = 'python-client-unique-id'  # ID do cliente Python (deve ser único)

data = []

# Realiza conexão ao Broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT")
        else:
            print("Falha ao conectar, código de retorno %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Realiza subscribe ao Tópico
def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Recebido o dado `{msg.payload.decode()}` do tópico `{msg.topic}`")
        data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": msg.topic,
        "payload": msg.payload.decode()
        })

    client.subscribe(topic_subscribe)
    client.on_message = on_message

def save_data_to_csv(filename='mqtt_data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Dados salvos no arquivo {filename}")

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
   
    
    try:
        while True:
            time.sleep(60)  # Ajuste o intervalo conforme necessário
            save_data_to_csv()
    except KeyboardInterrupt:
        print("Interrompido pelo usuário")
        client.loop_stop()
        save_data_to_csv()

if __name__ == '__main__':
    run()

