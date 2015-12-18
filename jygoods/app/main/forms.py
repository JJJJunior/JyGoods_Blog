#*-*coding: utf-8 *-*

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import Length, Regexp, Required
from flask.ext.pagedown.fields import PageDownField
import re


class EditProfileForm(Form):
    name = StringField(u'昵称', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'简述')
    submit = SubmitField(u'提交')



class PostForm(Form):
    body = PageDownField(u"发表话题?", validators=[Required()])
    submit = SubmitField(u'发布文章')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField(u'提交评论')