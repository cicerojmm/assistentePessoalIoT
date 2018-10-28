// --- WIFI ---
#include <ESP8266WiFi.h>
const char* ssid     = "";
const char* password = "";
WiFiClient esp8266Client;

// --- MQTT ---
//Adicionar dados para a conexão
#include <PubSubClient.h>
PubSubClient client(esp8266Client);
const char* mqtt_Broker = "iot.eclipse.org";
const int   mqtt_port = 1883;
const char* topico = "iluminacao/status";
const char* mqtt_ClientID = "veronica";

#define LEDVERDE D1
#define PINRELE D7

// --- Conecta ao WIFI ---
void conectarWifi(){
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

// --- Conecta ao MQTT ---
void conectarMQTT() {
  while (!client.connected()) {
    client.connect(mqtt_ClientID);
    if(client.connected()) {
      client.subscribe(topico); 
    }
  }
}

void controleLuz(String payload) {
  Serial.println(payload);
  if(payload == "1") {
     digitalWrite(LEDVERDE, HIGH);
     digitalWrite(PINRELE, HIGH);
  } else {
    digitalWrite(LEDVERDE, LOW);
    digitalWrite(PINRELE, LOW);
  }
}

String mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;
 
    //obtem a string do payload recebido
    for(int i = 0; i < length; i++) 
    {
       char c = (char)payload[i];
       msg += c;
    }

  Serial.println(msg);
  if(msg == "1") {
     digitalWrite(LEDVERDE, HIGH);
     digitalWrite(PINRELE, LOW);
  } else {
    digitalWrite(LEDVERDE, LOW);
    digitalWrite(PINRELE, HIGH);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LEDVERDE, OUTPUT);
  pinMode(PINRELE, OUTPUT);
  digitalWrite(PINRELE, HIGH);
  digitalWrite(LEDVERDE, LOW);
  conectarWifi();
  client.setServer(mqtt_Broker, mqtt_port);
  client.setCallback(mqtt_callback);
}

void loop() {
  if (!client.connected()) {
    conectarMQTT();
  }
  client.loop();
}


