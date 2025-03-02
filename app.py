# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Msr = Base.classes.measurement
Stn = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB

    session = Session(engine)

    # Calculate the date one year ago from the most recent date in the dataset

    recent = session.query(func.max(Msr.date)).scalar()
    year_ago = dt.datetime.strptime(recent, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Get precipitation for last 12 months

    results = session.query(Msr.date, Msr.prcp).filter(Msr.date >= year_ago).all()
    session.close()
    
    # Convert to dict: date == key, prcp == value

    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)



# Stations route

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB

    session = Session(engine)

    # Query all stations

    results = session.query(Stn.station).all()
    session.close()
    
    # Convert list of tuples into normal list

    stations = [station[0] for station in results]
    
    return jsonify(stations)



# Temperature observations route

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB

    session = Session(engine)

    # Calculate date one year ago from the most recent date

    most_recent_date = session.query(func.max(Msr.date)).scalar()
    year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Get most active station

    most_activity = session.query(Msr.station).group_by(Msr.station).\
                          order_by(func.count(Msr.station).desc()).first()[0]
    
    # Get temperature observations for most active station

    results = session.query(Msr.date, Msr.tobs).\
              filter(Msr.station == most_activity).\
              filter(Msr.date >= year_ago).all()
    session.close()
    
    # Make list

    tobs_data = [{"date": date, "temperature": temp} for date, temp in results]
    
    return jsonify(tobs_data)



# Temperature statistics route

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # If only start, calculate TMIN, TAVG, and TMAX for all dates >= start

    if end is None:
        results = session.query(func.min(Msr.tobs), 
                                func.avg(Msr.tobs), 
                                func.max(Msr.tobs)).\
                  filter(Msr.date >= start).all()
    # If both start and end, calculate TMIN, TAVG, and TMAX for dates in range

    else:
        results = session.query(func.min(Msr.tobs), 
                                func.avg(Msr.tobs), 
                                func.max(Msr.tobs)).\
                  filter(Msr.date >= start).filter(Msr.date <= end).all()
    
    session.close()
    
    # Make dictionary

    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_stats)


# Run the app

if __name__ == '__main__':
    app.run(debug=True)