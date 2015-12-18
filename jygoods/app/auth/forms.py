# *-*coding: utf-8 *-*

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from app.models import User


class LoginForm(Form):
    email = StringField(u'邮箱', validators=[
        Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住登录状态')
    submit = SubmitField(u'登录')


class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名',
                           validators=[Required(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters,''numbers, dots or underscores')])
    password = PasswordField(u'输入密码', validators=[Required(), EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'提交注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经存在')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'原密码', validators=[Required()])
    password = PasswordField(u'新密码',
                             validators=[Required(), EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'提交申请')


class PasswordResetRequestForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField(u'提交申请')


class PasswordRestForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'新密码',
                             validators=[Required(), EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'提交申请')


class ChangeEmailForm(Form):
    email = StringField(u'新邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'提交申请')

    def validate_email(self, field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError(u'邮箱已经注册')