from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from dotenv import dotenv_values, load_dotenv
from _Classes._unique.TableDefs import Device
import os


Db = SQLAlchemy()

app = Flask(__name__)

# Load environment variables from .env file
config = dotenv_values()
load_dotenv()
BASE_URL = os.environ.get("BASE_URL")

# Configure database connection
connection_string = config['DBCONNECT']
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
Db.init_app(app)

# Valid = Has a power config and is less than 2 months out
# No config = Does not have a power config
# Unsynced = Has a power config but is MORE than 2 months out

@app.route('/')
def index():
    # Top buttons
    total_devices = Db.session.query(Device).count() # Calculate total number of devices
    noconfig = Db.session.query(Device).filter(Device.automation_yes_no == '0').count()  # Count devices that have no config
    valid = Db.session.query(Device).filter(Device.automation_yes_no == '1', ~Device.sync_time.contains('months ago'), Device.sync_time != 'Unknown').count()  # Count devices with automation_yes_no = 1
    unsynced = Db.session.query(Device).filter(Device.automation_yes_no == '1', or_(Device.sync_time == 'Unknown', Device.sync_time.contains('months ago'))).count()  # Count devices with sync_time = 'Unknown' or 'months ago'
    
    # Table being displayed
    devices = Db.session.query(Device).all()
    return render_template('index.html', devices=devices, total_devices=total_devices, noconfig=noconfig, valid=valid, unsynced=unsynced, BASE_URL=BASE_URL)

@app.route('/valid')
def valid():
    # Top buttons
    total_devices = Db.session.query(Device).count() # Calculate total number of devices
    noconfig = Db.session.query(Device).filter(Device.automation_yes_no == '0').count()  # Count devices with automation_yes_no = 0
    valid = Db.session.query(Device).filter(Device.automation_yes_no == '1', ~Device.sync_time.contains('months ago'), Device.sync_time != 'Unknown').count()  # Count devices with automation_yes_no = 1
    unsynced = Db.session.query(Device).filter(Device.automation_yes_no == '1', or_(Device.sync_time == 'Unknown', Device.sync_time.contains('months ago'))).count()  # Count devices with sync_time = 'Unknown' or 'months ago'
    
    # Table being displayed
    valid_devices = Db.session.query(Device).filter(Device.automation_yes_no == '1', ~Device.sync_time.contains('months ago'), Device.sync_time != 'Unknown').all()
    return render_template('valid.html', total_devices=total_devices, noconfig=noconfig, valid=valid, unsynced=unsynced, valid_devices=valid_devices, BASE_URL=BASE_URL)

@app.route('/noconfig')
def noconfig():
    # Top buttons
    total_devices = Db.session.query(Device).count() # Calculate total number of devices
    noconfig = Db.session.query(Device).filter(Device.automation_yes_no == '0').count()  # Count devices with automation_yes_no = 0
    valid = Db.session.query(Device).filter(Device.automation_yes_no == '1', ~Device.sync_time.contains('months ago'), Device.sync_time != 'Unknown').count()  # Count devices with automation_yes_no = 1
    unsynced = Db.session.query(Device).filter(Device.automation_yes_no == '1', or_(Device.sync_time == 'Unknown', Device.sync_time.contains('months ago'))).count()  # Count devices with sync_time = 'Unknown' or 'months ago'
   
    # Table being displayed
    noconfig_devices = Db.session.query(Device).filter(Device.automation_yes_no == '0').all() # Pull every device where automation_yes_no = 0
    return render_template('noconfig.html', total_devices=total_devices, noconfig=noconfig, valid=valid, unsynced=unsynced, noconfig_devices=noconfig_devices, BASE_URL=BASE_URL)

@app.route('/unsynced')
def unsynced():
    # Top buttons
    total_devices = Db.session.query(Device).count() # Calculate total number of devices
    noconfig = Db.session.query(Device).filter(Device.automation_yes_no == '0').count()  # Count devices with automation_yes_no = 0
    valid = Db.session.query(Device).filter(Device.automation_yes_no == '1', ~Device.sync_time.contains('months ago'), Device.sync_time != 'Unknown').count()  # Count devices with automation_yes_no = 1
    unsynced = Db.session.query(Device).filter(Device.automation_yes_no == '1', or_(Device.sync_time == 'Unknown', Device.sync_time.contains('months ago'))).count()  # Count devices with sync_time = 'Unknown' or 'months ago'
    
    # Table being displayed
    unsynced_devices = Db.session.query(Device).filter(Device.automation_yes_no == '1', or_(Device.sync_time == 'Unknown', Device.sync_time.contains('months ago'))).all()
    return render_template('unsynced.html', total_devices=total_devices, noconfig=noconfig, valid=valid, unsynced=unsynced, unsynced_devices=unsynced_devices, BASE_URL=BASE_URL)

if __name__ == '__main__':
    app.run(debug=True)
