import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_database(app):
    # Usar archivo 'axis.db' en la raíz del proyecto
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../axis.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)