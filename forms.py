from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, StringField, TextAreaField, FloatField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    type = SelectField('Type', choices=[('select', 'Select Property Type'), ('tanah', 'Tanah'), ('rumah', 'Rumah'), ('ruko', 'Ruko')], validators=[DataRequired()])
    images = MultipleFileField('Images')
    submit = SubmitField('Submit')
