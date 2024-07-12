from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm): 
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=1, max=128)])
    password = StringField('Password',
                           validators=[DataRequired(), Length(min=1, max=64)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')