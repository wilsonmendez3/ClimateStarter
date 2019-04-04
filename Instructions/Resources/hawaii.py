import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
hawaii = Flask(__name__)
#################################################
# Flask Routes
#################################################

@hawaii.route("/")
def welcome():
    
    return (
        f"~All available api routes.~<P>"
        f"Welcome to Hawaii climate api!<p>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]"
    )


@hawaii.route("/api/v1.0/precipitation")
def precipitation():
    """ JSON list of precipitation data as dictionary with date as key and precipitation as value"""
    # query all precipitation
    precipitationresult = session.query(Measurement.date, Measurement.prcp).all()
    precipitationresults_l = list(np.ravel(precipitationresult))

    # create a dictionary
    dates = precipitationresults_l[0::2]
    prcp = precipitationresults_l[1::2]   
    precipitationd = dict(zip(dates, prcp))

    return jsonify(precipitationd)

@hawaii.route("/api/v1.0/station")
def station():
    """ JSON list of station data"""
    # query all precipitation
    stationsresult = session.query(Station.name).all()
    allstations = list(np.ravel(stationsresult))
    return jsonify(allstations)

@hawaii.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of Temperature Observations for the last year."""
    # Query all tobs between 2016-08-23 and 2017-08-23
    tobs = session.query(Measurement.tobs).filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()
    # Convert list of tuples into normal list
    alltobs = list(np.ravel(tobs))
    return jsonify(alltobs)

@hawaii.route("/api/v1.0/<start>")
def tobs_start(start):
    # query the database to get the maximum date
    maxdate = session.query(func.max(Measurement.date)).scalar()
    # reformat using datetime
    maxdateformatted = dt.datetime.strptime(maxdate, '%Y-%m-%d').date()

    """ Return TMIN, TAVE, and TMAX for all dates greater than and equal to startDate."""
    # query  tobs greater than and equal to startDate
    dailys =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= maxdateformatted).all()

    # convert list of tuples into normal list
    dailylist = list(np.ravel(dailys))
    
    stmin = dailylist[0]
    stave = dailylist[1]
    stmax = dailylist[2]

    return jsonify(stmin, stave, stmax)

@hawaii.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    """ Return TMIN, TAVE, and TMAX for dates between startDate and endDate inclusive."""
    # query all tobs between start and end
    dailystrip = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # convert list of tuples
    dailystrip_list = list(np.ravel(dailystrip))

    trmin = dailystrip_list[0]
    trave = dailystrip_list[1]
    trmax = dailystrip_list[2]

    return jsonify(trmin, trave, trmax)


if __name__ == '__main__':
    hawaii.run(debug=True)