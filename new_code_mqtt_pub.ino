#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include<ArduinoJson.h>
#include <PubSubClient.h>+

// Replace with your network credentials
const char* ssid     = "Redmi Note 10";
const char* password = "123456789";

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 19800, 60000);  // UTC timezone, update every 60 seconds

const char* mqttServer="broker.emqx.io";
const int mqttPort=1883;
const char* mqttTopic="Esp32data";

WiFiClient espClient;
PubSubClient client(espClient);

//variable declaration
char message[516];
int count=1;
int loopcount=1;
void setup() {
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize NTP Client
  client.setServer(mqttServer,mqttPort);
  delay(1000);
  timeClient.begin();
}
void reconnect(){
  while(!client.connected()){
    Serial.print(" Attempting to connect mqtt broker... ");
    if(client.connect("ESP32Client")){
      Serial.print(" Mqtt broker connected ");
      Serial.println(" ");
    }
    else{
      Serial.print(" Mqtt failed,rc= ");
      Serial.print(client.state());
      Serial.println("");
      delay(5000);
    }
  }
 }
void loop() {
  Serial.print("Loop count is :");
  Serial.println(loopcount);
  loopcount+=1;
  // Update the NTP client
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  if(!client.connected()){
      reconnect();
    }
  String dateTime = getFormattedDateTime();
  String macAddress = WiFi.macAddress();
  
  JsonDocument doc;
  doc["Gateway time"]=dateTime;
  doc["Count"]=count;
  doc["MAC ID"]=macAddress;
  doc["IP"]=WiFi.localIP();
  doc["RSSI"]=WiFi.RSSI();
  serializeJson(doc,message);
  Serial.print("JSON data is :");
  Serial.print(message);
  bool publishstatus=client.publish(mqttTopic,message);
  if(publishstatus==true){
    Serial.println("Data published successfully");
  }
  else{
    Serial.println("Data published failed");
  }
  delay(500);
  count+=1;
  client.loop();
  
}

// Function to format the epoch time into DD/MM/YYYY HH:MM:SS
String getFormattedDateTime() {
  // Update NTP time
  timeClient.update();

  // Get raw epoch time (seconds since 1970)
  unsigned long epochTime = timeClient.getEpochTime()-9;

  // Calculate current date and time
  int currentYear = 1970;
  unsigned long secondsInAYear = 365 * 24 * 3600;

  while (epochTime >= secondsInAYear) {
    epochTime -= secondsInAYear;
    currentYear++;
    // Handle leap years
    if (currentYear % 4 == 0 && (currentYear % 100 != 0 || currentYear % 400 == 0)) {
      secondsInAYear = 366 * 24 * 3600;  // Leap year has 366 days
    } else {
      secondsInAYear = 365 * 24 * 3600;  // Regular year has 365 days
    }
  }

  // Get month, day, hour, minute, second
  int currentMonth = 1;
  int daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

  if (currentYear % 4 == 0 && (currentYear % 100 != 0 || currentYear % 400 == 0)) {
    daysInMonth[1] = 29;  // Leap year February
  }

  int currentDay = epochTime / (24 * 3600);
  epochTime %= 24 * 3600;

  for (int i = 0; i < 12; i++) {
    if (currentDay < daysInMonth[i]) {
      currentMonth = i + 1;
      break;
    }
    currentDay -= daysInMonth[i];
  }
  
  currentDay++;  // Adjust because day starts at 1
  
  int currentHour = epochTime / 3600;
  epochTime %= 3600;
  
  int currentMinute = epochTime / 60;
  int currentSecond = epochTime % 60;

  // Format the date and time
  char dateTimeBuffer[30];
  sprintf(dateTimeBuffer, "%04d/%02d/%02d %02d:%02d:%02d", 
          currentYear, currentMonth, currentDay, 
          currentHour, currentMinute, currentSecond);

  return String(dateTimeBuffer);
}
