# Daily: A personal journal and performance tracking web application

## Project Description

The sole purpose of this application for now is to track my daily activities, and the ratings I give to either those activities, or the days themselves as a whole. These ratings coupled with daily events will generate patters that allow me to find events that have a negative impact on my daily well being (i.e. events that consistently lead to a negative sore). 

The project is also relevant for me to learn machine learning in the near future in the form of predictive machine learning algorithms. Paired with learning to graph clear and insightful graphs with the dataset.

## Project Status

This project is currently in development. The initial database models are finished, entries that amount to 2-3 months will be inserted shortly alongside a web interface. Useful and insightul trend plots will follow.

## Installation and Setup Instructions

Clone this repository with `git clone git@github.com:EternalGoldenBraid/daily.git`.

Initialize a virtual environment within `daily/` to exclude your main system's python modules from interfering: `python -m venv env`.

Activate the virtual environment with `source /daily/env/bin/activate`.

Set the environmental `FLASK_APP` variable with `export FLASK_APP=daily`.

Run the application with `flask run` and test using the provided URL.

## Task List

Read and implement from SQLAlchemy Documentation [x]

Create database models [x]

Implement a web UI with data visualisation []

Deploy to cloud []

Add multi-user suport, and creation of their db models []


