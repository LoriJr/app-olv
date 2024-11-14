from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_cors import CORS
import boto3
from siteolv.config_s3 import S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import cloudinary
import os
import psycopg2


app = Flask(__name__)

session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, )
s3 = session.resource('s3')

app.config['SECRET_KEY'] = '814a54e45292ee641c68e96e1afcab76'

if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_olv.db'

app.config['FLASK_ADMIN_SWATCH'] = "cerulean"

database = SQLAlchemy(app)

bcrypt = Bcrypt(app)
CORS(app)

cloudinary.config(cloud_name='hkyww4zdf', api_key='247446249213895',api_secret='3IWWfpTUacu51u43ldrbAd4OIlE')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'
login_manager.login_message = 'Para acessar essa página é necessário fazer login'
adm = Admin(app, name="OLV Admin", template_mode='bootstrap3')

from siteolv import routes




