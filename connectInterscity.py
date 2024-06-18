# pip installs
!pip install requests

# imports
import time
import pandas as pd
from google.colab import drive
import requests
import json

# Inicializa o DataFrame para armazenar os dados
data = {'Datetime': [], 'Topic': [], 'Payload': [], 'Capacidade': []}
df = pd.DataFrame(data)

# Endereço para a API InterSCity
api = 'http://cidadesinteligentes.lsdi.ufma.br'

# Endereço do CSV que será salvo no Google Drive
csv_path = '/content/drive/My Drive/mqtt_data.csv'


def show_capacidades():
    r = requests.get(api+'/catalog/capabilities')

    # Retorno da API
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

def show_resources():
    r = requests.get(api+'/catalog/resources')

    # Retorno da API
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

# Função para criar uma capacidade na API
def create_capability(nome, tipo, descricao):
    capability_json = {
      "name": nome,
      "description": descricao,
      "capability_type": tipo
    }

    #Faz uma request para a API e salvar a capacidade
    r = requests.post(api+'/catalog/capabilities/', json=capability_json)

    # Retorna se a capacidade foi "postada" com sucesso ou não
    if(r.status_code == 201):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
      return True
    else:
      print('Status code: '+str(r.status_code))
      return False

def create_resource(descricao, latitude, longitude, capacidades):
    # Cria o recurso do estacionamento
    resource_json = {
      "data": {
        "description": descricao,
        "capabilities": capacidades,
        "status": "active",
        "city": "SLZ",
        "country": "BR",
        "state":"MA",
        "lat": latitude,
        "lon": longitude
      }
    }

    # "Post" do recurso na API
    r = requests.post(api+'/catalog/resources', json=resource_json)

    # Retorna sucesso ou fracasso da "postagem" do recurso de estacionamento, também salva seu UUID.
    uuid = ''
    if(r.status_code == 201):
      resource = json.loads(r.text)
      uuid = resource['data']['uuid']
      print(json.dumps(resource, indent=2))
    else:
      print('Status code: '+str(r.status_code))
    return uuid


def addData_API(uuid_resource):
    # Lê o CSV do Google Drive
    df = pd.read_csv(csv_path)

    # Salva as colunas do CSV em listas
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    dates = df.timestamp.tolist()
    capacidades_ = df.topic.tolist()
    payloads = df.payload.tolist()

    # Converte os dados das capacidades em JSON
    capability_data_json = {
      "data": [{capacidade: value, 'timestamp': date.isoformat()} for capacidade, value, date in zip(capacidades_, payloads, dates)]
    }

    time.sleep(1)
    # Adiciona dados das 'capabilities' ao 'resource'
    r = requests.post(api+'/adaptor/resources/'+uuid_resource+'/data/environment_monitoring', json=capability_data_json)
    if(r.status_code == 201):
      print('OK!')
    else:
      print('Status code: '+str(r.status_code))
      return False

    time.sleep(1)
    # Exibe dados do 'resource'
    r = requests.post(api+'/collector/resources/'+uuid_resource+'/data')
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

    return True
