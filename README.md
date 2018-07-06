# DashDev
## Extensible example on how to develop for Tumalow's dashboard.

Before you start using this tool.  Log into the dashboard, click "Devices".  Select the device you'd like to push data to.  Click "Copy Access Token".

Create a file in the top level directory of DashDev called config.yml.  Fill in the details there.  The host should be dashboard.tumalow.com.  The token should be the Access Token you just got.

Next run the telemetry_example.py.  This will connect to the server and push incrementing data.  

You can track any key-value pair of timestamped data.

Tested on python 2.7.  Requires paho-mqtt