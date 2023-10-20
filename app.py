from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# connect to database
Base = SQLAlchemy(app)

# Database Model
class Audit(Base.Model):
    __tablename__ = 'Audit'
    
    Audit_id = Base.columnInteger(primary=True)
    time_created = Base.columnDateTime()
    data_title = Base.columnString(255)
    device_type = Base.columnString(35)
    lab = Base.columnString(50)
    model_number = Base.columnString(50)
    serial_number = Base.columnString(25)
    manufacturer = Base.columnString(50)
    eitms = Base.columnString(25)
    sync_time = Base.columnString(25)
    power_policy = Base.columnString(25)
    power_status = Base.columnString(25)



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()