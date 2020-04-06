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

    
if __name__ == "__main__":
    app.run(debug=True)
    
