# imports
import time
import pandas as pd
from google.colab import drive
from datetime import datetime
import pytz
import numpy as np
import requests
import json

# Inicializa o DataFrame para armazenar os dados
data = {'Datetime': [], 'Topic': [], 'Payload': [], 'Capacidade': []}
df = pd.DataFrame(data)

# Fuso horário desejado ('America/Sao_Paulo')
desired_timezone = 'America/Sao_Paulo'

# Cria um objeto de fuso horário
local_timezone = pytz.timezone(desired_timezone)

# Endereço para a API InterSCity
api = 'http://cidadesinteligentes.lsdi.ufma.br'

# Endereço do CSV que será salvo no Google Drive
csv_path = '/content/drive/My Drive/dados_mqtt.csv'

topicos_capacidades = {
  "esp8266/inputs/a": "vagaA",
  "esp8266/inputs/b": "vagaB",
  "esp8266/inputs/c": "vagaC",
  "esp8266/inputs/d": "vagaD",
  "esp8266/inputs/e": "vagaE"
}

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

def prepare_API():
    # Lista de topicos únicos do DATAFRAME
    capacidades_list = np.array(df.Capacidade.tolist())
    capacidades_unique = np.unique(capacidades_list)

    print("Preparando a API...")
    time.sleep(1)
    print("Lista de tópicos da esp8266:")
    print(capacidades_unique)
    time.sleep(1)

    # Armazena se a capacidade foi criada ou não
    capabilidade_criada = False

    # Criação das capacidades na API
    for nomeCapacidade in capacidades_unique:
      print("="*20)
      print("Criando a capacidade para '"+nomeCapacidade+"' na API "+api+"...")
      time.sleep(1)
      capabilidade_criada = create_capability(nomeCapacidade,"sensor", "Vaga disponível ou ocupada")
      time.sleep(1)
      if capabilidade_criada == False:
        return ""

    # Criação do recurso na API
    print("Criando recurso 'Estacionamento_A' na API "+api+"...")
    time.sleep(1)
    uuid_resource = create_resource("Estacionamento_A", -2.55972052497871, -44.31196495361665, topics_unique)
    time.sleep(1)
    return uuid_resource

def addData_API(uuid_resource):
    # Lê o CSV do Google Drive
    df = pd.read_csv(csv_path)

    # Salva as colunas do CSV em listas
    dates = df.Datetime.tolist()
    capacidades_ = df.Capacidade.tolist()
    payloads = df.Payload.tolist()

    # Converte os dados das capacidades em JSON
    capability_data_json = {
      "data": [{capacidade: value, 'timestamp': date.isoformat()} for capacidade, value, date in zip(capacidades_, payloads, dates)]
    }

    print("Exibindo dados das capacidades salvos no dataframe...")
    time.sleep(1)
    print(capability_data_json);
    time.sleep(1)

    print("Adicionando dados das capacidades ao recurso 'Estacionamento_A' da API "+api+"...")
    time.sleep(1)
    # Adiciona dados das 'capabilities' ao 'resource'
    r = requests.post(api+'/adaptor/resources/'+uuid_resource+'/data/environment_monitoring', json=capability_data_json)
    if(r.status_code == 201):
      print('OK!')
    else:
      print('Status code: '+str(r.status_code))
      return False

    print("Exibindo dados do recurso 'Estacionamento_A'...")
    time.sleep(1)
    # Exibe dados do 'resource'
    r = requests.post(api+'/collector/resources/'+uuid_resource+'/data')
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

    return True
