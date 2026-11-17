from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    """User login form with email and password."""

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please provide a valid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required")],
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """New user registration form."""

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Full name is required"),
            Length(min=2, max=100, message="Name must be between 2 and 100 characters"),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please provide a valid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Create Account")


class ProfileForm(FlaskForm):
    """User profile update form."""

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Full name is required"),
            Length(min=2, max=100),
        ],
    )
    current_password = PasswordField("Current Password")
    new_password = PasswordField("New Password")
    submit = SubmitField("Save Changes")
