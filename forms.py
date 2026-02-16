from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length

class TextForm(FlaskForm):
    text = TextAreaField('Text', validators=[DataRequired(), Length(max=10000)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])

class FileForm(FlaskForm):
    file = FileField('File', validators=[FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
