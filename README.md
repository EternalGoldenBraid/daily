# Daily: A personal journal and performance tracking web application

## Project Description

The sole purpose of this application for now is to track my daily activities, and the ratings I give to either those activities, or the days themselves as a whole. These ratings coupled with daily events will generate patterns that allow me to find events that have a negative impact on my daily well being (i.e. events that consistently lead to a negative score). 

The project also coincides with my intereset in data and extracting patterns that can be used to support optimization and long term oriented planning. Visualizing data sets is a large component of this and I am keen on adding that in as well.

## Project Status

A minimal web interface is up and running [here](http://dailyapp.eu.pythonanywhere.com/) using pythonanywhere. The application currently only supports adding data for a single user. A demo account is available with username: demo, password: demo

## Installation and Setup Instructions

Clone this repository with `git clone git@github.com:EternalGoldenBraid/daily.git`.

Initialize a virtual environment within `daily/` to prevent your main system's python packages from interfering: `python -m venv env`.

Activate the virtual environment with `source /daily/env/bin/activate`.

Install required python packages with from daily/requirements.txt with `pip install -r requirements.txt`.

Set the environmental `FLASK_APP` variable with `export FLASK_APP=daily`.

Run the application with `flask run` and test using the provided URL.

## Task List

- [x] Read and setup from SQLAlchemy, Flask and it's plugins' Documentation

- [x] Create database models

- [x] Deploy to cloud

- [x] Implement a web UI 

- [ ] Add timestamps for event inputs and edits.

- [ ] Add data visualization
      
- [ ] Add multi-user support

- [ ] Add an about page

- [x] Configure Database backups

- [ ] Integrate easybacklog.com API into Daily

