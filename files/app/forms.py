from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired

# The WTForm used for the create a task page
# outlines all the inputs and the validators 
# along with any other information such as placeholders and format
class CreateTaskForm(FlaskForm):
    title = StringField('inputTitle', validators=[DataRequired()], render_kw={"placeholder": "e.g. Coursework 1"})
    date = DateField('inputDueDate', validators=[DataRequired()])
    description = TextAreaField('inputDescription', validators=[DataRequired()], render_kw={"placeholder": "Description (Max 500 Characters)", "maxlength": 500})
    group = SelectField('inputGroup', validators=[DataRequired()])

class CreateGroupForm(FlaskForm):
    name = StringField('inputGroupName', validators=[DataRequired()], render_kw={"placeholder": "Group Name"})
    code = StringField('inputGroupCode', validators=[DataRequired()], render_kw={"placeholder": "Secure Group Code (For others to join)"})

class JoinGroupForm(FlaskForm):
    code = StringField('inputGroupCode', validators=[DataRequired()], render_kw={"placeholder": "Secure Group Code"})