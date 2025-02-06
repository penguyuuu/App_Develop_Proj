from wtforms import Form, SelectField, TextAreaField, validators
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class BubbleTeaForm(Form):
    size = SelectField('Size', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
                       validators=[DataRequired()])
    sweetness = SelectField('Sweetness Level',
                            choices=[('0%', '0%'), ('30%', '30%'), ('50%', '50%'), ('70%', '70%'), ('100%', '100%')],
                            validators=[DataRequired()])
    temperature = SelectField('Hot or Cold', choices=[('hot', 'Hot'), ('cold', 'Cold')], validators=[DataRequired()])
    remarks = TextAreaField('Remarks', [validators.Optional()])
    submit = SubmitField('Customize Your Drink')
