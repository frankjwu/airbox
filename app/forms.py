from flask.ext.wtf import Form
from wtforms import StringField, FileField, IntegerField
from wtforms.validators import DataRequired

class BuyForm(Form):
	name = StringField('File Name', validators=[DataRequired()])
	dropboxFile = FileField('File Attachment', validators=[DataRequired()])

class SellForm(Form):
	space = IntegerField('Space Remaining', validators=[DataRequired()])

