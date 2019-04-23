# Overview Alarm
Overview Alarm can warning the IT room if a host goes down, by enabling an alarm light, and speak a warning message like "Warning, the host geoserver is down"   
Its based on Overview Back project   

![Alt text](https://github.com/vaidis/overview-alarm/blob/master/images/overview_alarm_final.jpg?raw=true)
![Alt text](https://github.com/vaidis/overview-alarm/blob/master/images/overview_alarm_connections.jpg?raw=true)
![Alt text](https://github.com/vaidis/overview-alarm/blob/master/images/overview_alarm_bb.png?raw=true)

## Setup
* *Edit the language
* Edit the Leading and Tail mp3's of the messages 

## Voice messages
It uses the gTTS google library to create an mp3 for the first time, and after that is plays the message from local mp3  

## Hardware depentencies
* Raspberry PI
* Box
* Alarm light
* Speakers
* Step Up 5V to 12V
* Relay board
* SDCard Class 10


