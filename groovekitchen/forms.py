from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import EmailField, PasswordField, StringField, ValidationError


class FormData(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    
    def validate_firstname(self, firstname):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.firstname.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed in firstname.")
    def validate_lastname(self, lastname):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.lastname.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed in lastname.")