# Daily: A personal journal and performance tracking web application

## Project Description

The sole puprose of the application for now is to track my daily activities and ratings I give to either those activities or the days themselves as a whole. These ratings coupled with daily events will generate patters that allow me to find events that have a negative impact on my daily well being. 

The project is also relevant for me to play around with machine learning algorithms and/or generate them myself, once I have attained the prerequisites of the mathematics required for that.

## Project Status

This project is currently in development. The initial database models are finished, entries that amount to 2-3 months will be inserted shortly alongside a web interface. Useful and insightul trend plots will follow.

## Installation and Setup Instructions

Clone this repository with `git clone git@github.com:EternalGoldenBraid/daily.git`.

Initialize a virtual environment within `daily/` to exclude your main system's python modules from interfering: `python -m venv env`

Activate the virtual environment with `source /daily/env/bin/activate`

Set the environmental `FLASK_APP` variable with `export FLASK_APP=daily`

Run the application with `flask run` and test using the provided URL

## Task List
Create database models [x]

Implement login []

Implement promts for user daily input []

Implement index for browsing user input []
