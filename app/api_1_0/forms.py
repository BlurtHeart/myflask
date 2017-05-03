# -*- coding: utf-8 -*-
from wtforms import SubmitField, StringField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    title = StringField("Title", validators=[Required()])
    body = PageDownField("Body", validators=[Required()])
    submit = SubmitField(u'提交')


class CommentForm(FlaskForm):
    body = StringField('Write your opinion', validators=[Required()])
    submit = SubmitField(u'提交评论')