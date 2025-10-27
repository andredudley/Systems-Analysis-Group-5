from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this'
# MySQL Configuration
app.config['MYSQL_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'yourusername'
app.config['MYSQL_PASSWORD'] = 'your_database_password'
app.config['MYSQL_DB'] = 'yourusername$farm_management'
mysql = MySQL(app)