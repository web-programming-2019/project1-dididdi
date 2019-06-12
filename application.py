import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
import requests

csv_read=csv.reader(open('books.csv','r'))

app = Flask(__name__)
content=[]


# Check for environment variable
if not os.getenv("DATABASE_URL"):
   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db1: scoped_session = scoped_session(sessionmaker(bind=engine))




###构建连接数据库函数
def get_session():
    return db1
####创建自动事务函数
from contextlib import contextmanager
@contextmanager
def session_scope():
    db = get_session()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

####-------创建数据库字段
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

Base = declarative_base()
# 创建单表
#
###账户表account
class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    pwd = Column(String(16))

    def __init__(self, user_id=None, account_name =None, password=None):
        self.id = user_id
        self.name = account_name
        self.pwd = password
    ###用户表account
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_id_name'),
    )
###地址account
class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    address = Column(String(32))
    phone =  Column(String(32))
    user_id = Column(Integer, ForeignKey('users.id'))

###创建表
Base.metadata.create_all(engine)

##-----------------------------------分割线-------------------------------------##

######开始web脚本部分
import flask
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields import (StringField, PasswordField,)
from wtforms.validators import DataRequired, Length
from flask import Flask, render_template, redirect,session
from os import path
d = path.dirname(__file__)

####定义SECRET_KEY保证安全性
app.config['SECRET_KEY'] = 'my web_test!!'
###定义登录表单字段
#user, password,submit
#再渲染到html页面

class LoginForm(FlaskForm):
    # Text Field类型，文本输入框，必填，用户名长度为4到25之间
    username = StringField('Username', validators=[DataRequired(u'.请输入用户名！！'),Length(min=4, max=25,message=u'请输入4-25个字符！')])
    # Text Field类型，密码输入框，必填，必须同confirm字段一致
    password = PasswordField('Password', validators=[
        DataRequired(u'.请输入密码！！'),
        Length(min=4, max=25,message=u'请输入4-25个字符！'),
    ])
    submit = SubmitField('login')

#####定义搜索页面字段
#key, submit
class SearchForm(FlaskForm):
    key = StringField('Key',validators=[
        DataRequired(),
        Length(min=4, max=255)
    ])
    submit = SubmitField('search')


###定义登录控制器    允许访问的方式 get/post
@app.route('/test/login', methods=['GET','POST'])
def LoginFormViews():
    ###示例登陆类
    form  = LoginForm()
    if flask.request.method == "GET":
        ####get请求就显示表单页面，渲染字段->login.html
        return render_template('login.html',form=form)
    else:
        #print form.image.data   验证通过
        if form.validate_on_submit():
            ###开始check 用户名和密码
            username  =  form.username.data
            password = form.password.data
            with session_scope() as db:
                list = db.query(Account).filter(Account.name==username, Account.pwd==password).first()
                if list:
                    print (list)
                    ####把用户名记入session/cookies
                    session['username'] = username
                    return redirect('/test/search')
                else:
                    new_user = Account(1,username,password)
                    # 添加到session:
                    db.add(new_user)
                    # 提交即保存到数据库:
                    db.commit()
                    return redirect('/test/login')
        else:
            #print form.errors
            ###把错误信息返回到页面
            return render_template('login.html',form=form,error=form.errors)


#######search控制器
@app.route('/test/search', methods=['GET','POST'])
def SearchFormViews():
    form  = SearchForm()
    if flask.request.method == "GET":
            return render_template('search.html',form=form)
    else:
        #print form.image.data
        key = form.key.data
        print(key)
        for tem in csv_read:
            for i in tem:
                if i==key:
                    content.append(tem)
        return render_template('show.html',content=content,num=0)

######注销控制器
@app.route('/test/logout', methods=['GET'])
def logout():
    if flask.request.method == "GET":
        ####开始注销当前用户
        session.pop('username',None)
        return redirect('/test/login')

if __name__ == '__main__':
    app.run(debug=True)

