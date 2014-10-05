from flask.ext.wtf import Form
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

class UploadFileForm(Form):
	name = StringField('File Name', validators=[DataRequired()])
	dropboxFile = FileField('File Attachment', validators=[DataRequired()])

