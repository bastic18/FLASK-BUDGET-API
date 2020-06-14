
from flask_wtf import FlaskForm
from flask import Flask, session,request
from flask_wtf import validators
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField 
from wtforms.validators import DataRequired, Length, Email,EqualTo, ValidationError
from flask_mysqldb import MySQL,MySQLdb
import MySQLdb.cursors
from flask_wtf.file import FileField, FileAllowed









class LoginForm(FlaskForm):
       
    email= StringField('Email', validators=[DataRequired(), Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember= BooleanField('Remember Me')
    submit= SubmitField('Login')