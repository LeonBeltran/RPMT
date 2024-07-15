from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, DateField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Optional, InputRequired, NumberRange

class LoginForm(FlaskForm): 
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=128)])
    password = StringField('Password',
                           validators=[DataRequired(), Length(max=64)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class ProjectForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired(), Length(max=256)])
    abstract = TextAreaField('Abstract',
                           validators=[Optional(), Length(max=512)])
    authors = StringField('Authors',
                          validators=[DataRequired(), Length(max=512)])
    type = StringField('Type',
                       validators=[DataRequired(), Length(max=64)])
    date_published = DateField('Date Published',
                               validators=[DataRequired()])
    publication_name = StringField('Publication Name',
                                   validators=[DataRequired(), Length(max=128)])
    publisher = StringField('Publisher',
                            validators=[DataRequired(), Length(max=64)])
    publisher_type = StringField('Publisher Type',
                                 validators=[DataRequired(), Length(max=32)])
    publisher_location = StringField('Publisher Location',
                                     validators=[DataRequired(), Length(max=16)])
    editors = StringField('Editors',
                          validators=[DataRequired(), Length(max=512)])
    vol_issue_no = IntegerField('Volume/Issue No',
                                validators=[InputRequired(), NumberRange(min=0)])
    doi_url = StringField('DOI URL',
                          validators=[DataRequired(), Length(max=256)])
    isbn_issn = SelectField('ISBN/ISSN',
                            choices=[('NONE', 'None'), ('ISBN', 'ISBN'), ('ISSN', 'ISSN')],
                            validators=[DataRequired()])
    web_of_science = BooleanField('Web of Science')
    elsevier_scopus = BooleanField('Elsevier Scopus')
    elsevier_sciencedirect = BooleanField('Elsevier ScienceDirect')
    pubmed_medline = BooleanField('PubMed/Medline')
    ched_recognized = BooleanField('CHED Recognized')
    other_database = StringField('Other Database',
                                 validators=[Optional(), Length(max=128)])
    publication_proof = FileField('Publication Proof',
                                    validators=[Optional()])
    citations = IntegerField('Citations',
                             validators=[InputRequired(), NumberRange(min=0)])
    utilization_proof = FileField('Utilization Proof',
                                    validators=[Optional()])
    submit = SubmitField('Submit')