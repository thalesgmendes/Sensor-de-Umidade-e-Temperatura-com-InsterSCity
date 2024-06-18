#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHT_PIN D7
#define DHT_TYPE DHT11

DHT dht11(DHT_PIN, DHT_TYPE);


const char *ssid = "thales";
const char *password = "123456";

const char *mqtt_broker = "mqtt.eclipseprojects.io";
const char *temperature_topic = "livingroom/temperature";
const char *humidity_topic = "livingroom/humidity";
const int mqtt_port = 1883;

char msg[50];

bool mqttStatus = 0;

WiFiClient espClient;
PubSubClient client(espClient);


void setup() {
  Serial.begin(9600);
  
  dht11.begin();

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.println("Conectando ao WiFi...");
  }
  Serial.println("");
  Serial.println("Conectado à rede Wi-Fi");

  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  reconnect();

}

void loop(){

  if (!client.connected()) {
    reconnect();
  }

  float temperature_C = dht11.readTemperature();
  float humi = dht11.readHumidity();

  if ( isnan(temperature_C) || isnan(humi)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {

    Serial.print("Humidity: ");
    Serial.print(humi);
    Serial.print("%");
    sprintf(msg, "%f", humi);
    client.publish(humidity_topic, msg);

    Serial.print("  |  ");

    Serial.print("Temperature: ");
    Serial.print(temperature_C);
    Serial.print("°C  ~  ");
    sprintf(msg, "%f", temperature_C);
    client.publish(temperature_topic, msg);
  }

  delay(2000);

  client.loop();

}

void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Mensagem no tópico: ");
    Serial.println(topic);
    Serial.print("Conteúdo da mensagem: ");
    for (int i = 0; i < length; i++) {
        Serial.print((char) payload[i]);
    }
    Serial.println();
    Serial.println("-----------------------");
}

void reconnect() {
    while (!client.connected()) {
        String client_id = "esp8266-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("Conectando o cliente %s ao broker MQTT\n", client_id.c_str());
        if (client.connect(client_id.c_str())) {
            Serial.println("Conectado ao broker MQTT!");
            client.subscribe(temperature_topic);
            client.subscribe(humidity_topic);
        } else {
            Serial.print("Falha na conexão: ");
            Serial.print(client.state());
            delay(2000);
        }
    }
}
