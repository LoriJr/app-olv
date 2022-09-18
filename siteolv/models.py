from flask import redirect, url_for, flash, request, render_template
from flask_admin.contrib.sqla import ModelView
from siteolv import database, login_manager, routes
from datetime import datetime
from flask_login import UserMixin, current_user, login_required
from siteolv import adm
from flask_admin import BaseView, expose

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    nickname = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    instrumento = database.Column(database.Integer, database.ForeignKey('instrumentos.id'), nullable=False)
    anodeentrada = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='https://res.cloudinary.com/hkyww4zdf/image/upload/v1662451890/default_xk2hq0.png')
    posts = database.relationship('Post', backref='autor', lazy=True)
    admin = database.Column(database.Boolean, default=False)


class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)


class Validaemail(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    valida_email = database.Column(database.String, nullable=False, unique=True)


class Instrumentos(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome_instrumento = database.Column(database.String, nullable=False)
    musico = database.relationship('Usuario', backref='instru_ativo', lazy=True)


def admin_access(f):
    def wrapper():
        usuario = Usuario.query.filter_by(admin=True).first()
        if f(usuario):
            redirect(url_for('home'))
            flash("Usuario sem acesso")
    return wrapper


class Controller(ModelView):
    def is_accessible(self):
        if current_user.admin:
            return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class ModelViewValidaemail(Controller):
    column_list = ["valida_email"]


def format_user(self, request, Usuario, *args):
    return Usuario.instru_ativo.nome_instrumento


def format_part(self, request, Partituras, *args):
    return Partituras.instrumento


class ModelViewUsuario(Controller):
    column_list = ["username", "nickname", "email", "instrumento", "admin"]
    column_formatters = {"instrumento": format_user}


class ModelViewInstrumentos(Controller):
    column_list = ["id", "nome_instrumento"]


class ModelviewExitAdmin(BaseView):
    @expose("/")
    def home(self):
        return render_template('home.html')


adm.add_view(ModelViewUsuario(Usuario, database.session))
adm.add_view(ModelViewValidaemail(Validaemail, database.session))
adm.add_view(ModelViewInstrumentos(Instrumentos, database.session))
adm.add_view(ModelviewExitAdmin(name='Logout'))


