# Daily: A personal journal and performance tracking web application

## Project Status

This project is currently in development. The initial database models are finished, entries that amount to 2-3 months will be inserted shortly along side a web interface. Useful and insightul trend plots will follow.

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
