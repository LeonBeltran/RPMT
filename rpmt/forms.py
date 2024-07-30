from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, DateField, SubmitField, TextAreaField, SelectField, FileField, EmailField
from wtforms.validators import DataRequired, Length, Optional, InputRequired, NumberRange, EqualTo
from flask_wtf.file import FileAllowed

class UserForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=128)])
    email = EmailField('Email Address',
                       validators=[DataRequired(), Length(max=64)])
    password = StringField('Password',
                           validators=[DataRequired(), Length(max=64)])
    confirm_password = StringField('Confirm Password',
                           validators=[DataRequired(), Length(max=64), EqualTo('password', message='Passwords must match')])
    new_password = StringField('New Password',
                           validators=[Optional(), Length(max=64)])
    confirm_new_password = StringField('Confirm New Password',
                           validators=[Optional(), Length(max=64), EqualTo('new_password', message='Passwords must match')])
    role = SelectField('Role',
                       choices=[('Faculty', 'Faculty'), ('Admin', 'Admin'), ('Chair', 'Chair'), ('Dev', 'Dev')],
                       validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm): 
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=128)])
    password = StringField('Password',
                           validators=[DataRequired(), Length(max=64)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    title = StringField('Search Title',
                        validators=[Optional(), Length(max=256)])
    author = StringField('Search Author',
                         validators=[Optional(), Length(max=128)])
    submit = SubmitField('Search')
    
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
                                 validators=[DataRequired(), Length(max=128)])
    publication_proof = FileField('Publication Proof',
                                    validators=[DataRequired(), FileAllowed(['png', 'jpg', 'jpeg'])])
    clear_publication_proof = BooleanField('Remove Publication Proof Image (Ignore if new project or adding new image)')
    citations = IntegerField('Citations',
                             validators=[InputRequired(), NumberRange(min=0)])
    utilization_proof = FileField('Utilization Proof',
                                    validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg'])])
    clear_utilization_proof = BooleanField('Remove Utilization Proof Image (Ignore if new project or adding new image)')
    pdf = FileField('PDF File of Project',
                    validators=[Optional(), FileAllowed(['pdf'])])
    clear_pdf = BooleanField('Remove PDF (Ignore if new project or adding new PDF)')
    submit = SubmitField('Submit')