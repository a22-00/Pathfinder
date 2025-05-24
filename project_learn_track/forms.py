from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    profession = StringField('Current Profession', validators=[Length(max=100)])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select Experience Level'),
        ('Entry', 'Entry Level (0-2 years)'),
        ('Junior', 'Junior (2-4 years)'),
        ('Mid', 'Mid-Level (4-7 years)'),
        ('Senior', 'Senior (7-10 years)'),
        ('Lead', 'Lead/Principal (10+ years)'),
        ('Executive', 'Executive/C-Level')
    ])
    location = StringField('Location', validators=[Length(max=100)])
    career_goals = TextAreaField('Career Goals', validators=[Length(max=1000)])
    skills = TextAreaField('Skills (comma-separated)', validators=[Length(max=500)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match")
    ])
    submit = SubmitField('Change Password')

class QuickSetupForm(FlaskForm):
    """Quick setup form for new users"""
    profession = StringField('What\'s your current profession?', validators=[DataRequired(), Length(max=100)])
    experience_level = SelectField('Experience Level', validators=[DataRequired()], choices=[
        ('Entry', 'Entry Level (0-2 years)'),
        ('Junior', 'Junior (2-4 years)'),
        ('Mid', 'Mid-Level (4-7 years)'),
        ('Senior', 'Senior (7-10 years)'),
        ('Lead', 'Lead/Principal (10+ years)'),
        ('Executive', 'Executive/C-Level')
    ])
    career_goals = TextAreaField('What are your main career goals?', validators=[Length(max=500)])
    submit = SubmitField('Complete Setup') 