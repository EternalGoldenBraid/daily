# Daily: A personal journal and performance tracking web application

## Project Description

The sole purpose of this application for now is to track my daily activities, and the ratings I give to either those activities, or the days themselves as a whole. These ratings coupled with daily events will generate patterns that allow me to find events that have a negative impact on my daily well being (i.e. events that consistently lead to a negative score). 

The project also coincides with my intereset in data and extracting patterns that can be used to support optimization and long term oriented planning. Visualizing data sets is a large component of this and I am keen on adding that in as well.

## Project Status

This project is currently in development. The initial database models are finished, entries that amount to 2-3 months will be inserted shortly alongside a web interface. Useful and insightul trend plots will follow.

## Installation and Setup Instructions

Clone this repository with `git clone git@github.com:EternalGoldenBraid/daily.git`.

Initialize a virtual environment within `daily/` to prevent your main system's python packages from interfering: `python -m venv env`.

Activate the virtual environment with `source /daily/env/bin/activate`.

Install required python packages with from daily/requirements.txt with `pip install -r requirements.txt`.

Set the environmental `FLASK_APP` variable with `export FLASK_APP=daily`.

Run the application with `flask run` and test using the provided URL.

## Task List

Read and setup from SQLAlchemy, Flask and it's plugins' Documentation [x]

Create database models [x]

Implement a web UI with data visualisation []  **In progress**

Deploy to cloud []

Add multi-user suport, and creation of their db models []


