from flask import Flask, jsonify

app = Flask(__name__)

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

#import other dependencies
import datetime as dt
import numpy as np
import pandas as pd

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)


@app.route("/")
def homepage():
    
    return(
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    earliest_date =  dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    earliest_date = earliest_date.strftime("%Y-%m-%d")
    # Perform a query to retrieve the data and precipitation scores
    last_12_months = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date <= latest_date,\
                            Measurement.date >= earliest_date).all()

    prcp_data = {row[0]: row[1] for row in last_12_months}

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    station_names = session.query(Station.name).all()

    station_names = [row[0] for row in station_names]

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():

    # Choose the station with the highest number of temperature observations.
    tobs_obs_count = session.query(Measurement.station, func.count(Measurement.tobs).\
                label('Number_of_Obs')).group_by(Measurement.station).\
                order_by(text("Number_of_Obs DESC")).first()
    station_max_obs = tobs_obs_count[0]

    # Query the last 12 months of temperature observation data for this station

    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    earliest_date =  dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    earliest_date = earliest_date.strftime("%Y-%m-%d")

    temp_data = session.query(Measurement.tobs).\
                filter(Measurement.date <= latest_date,\
                Measurement.date >= earliest_date,
                Measurement.station == station_max_obs).all()

    temp_data = [temp[0] for temp in temp_data]

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def date_start(start):

    #most_active_station = most_active_station[0]
    sel = [func.min(Measurement.tobs),\
        func.max(Measurement.tobs),\
        func.avg(Measurement.tobs)
        ]

    selected_data = session.query(*sel).filter(Measurement.date >= start).all()

    selected_data = [row for row in selected_data]

    return jsonify(selected_data)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    #most_active_station = most_active_station[0]
    sel = [func.min(Measurement.tobs),\
        func.max(Measurement.tobs),\
        func.avg(Measurement.tobs)
        ]

    selected_data2 = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all()

    selected_data2 = [row for row in selected_data2]

    return jsonify(selected_data2)

    
if __name__ == "__main__":
    app.run(debug=True)
    
