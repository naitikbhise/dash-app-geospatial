# dash-app-geospatial
This project is based the word analysis of geographic data and results are projected on the website in a local server. Deployment of this web app was performed on the Google Cloud Platform but it caused a Error 500 which led to the deployment being incomplete on the app server (https://mygeospecial.appspot.com/). But you can download this code on your system and play with the numbers for the streets of New York. The code could be run with this line:

$ python main.py

This causes to open a local site http://127.0.0.1:8050/ (better check it up on the terminal for the exact website name) to open and you can play with the numbers there for the output.

About the project: The project consists of three parts:
First part describes the frequency of peculiar types of streets(street, Avenue, Boulevard, Road, etc) and draws a histogram of them.
Second part explains the Top 20 most commonly named streets or the Top 20 most frequent names of the streets in the region
Third region shows the top 20 weird street names in the area.

There are two regions available but I am working primarily on New York State Data.
