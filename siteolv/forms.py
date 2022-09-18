from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from siteolv.models import Usuario, Post, Validaemail, Instrumentos
from flask_login import current_user
import datetime


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(message='Digite um e-mail válido')])
    senha = PasswordField('senha', validators=[DataRequired(), Length(6, 50)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(6, 50)])
    nickname = StringField('Primeiro nome ou Apelido', validators=[DataRequired(), Length(3, 20)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    instrumento = SelectField('Qual instrumento você toca', choices=[(i.id, i.nome_instrumento) for i in Instrumentos.query.order_by('nome_instrumento')])
    anodeentrada = SelectField('Em que ano entrou na Orquestra', choices=[a for a in range(1980, datetime.date.today().year + 1)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 50)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        valida = Validaemail.query.filter_by(valida_email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado.')
        if not valida:
            raise ValidationError('E-mail não autorizado.')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    nickname = StringField('Apelido', validators=[DataRequired(), Length(3, 20)])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'],'Arquivo não permitido, use extensões .jpg ou .png')])
    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com esse e-mail. Cadastre outro e-mail')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui...', validators=[DataRequired(), Length(2, 400)])
    botao_submit = SubmitField('Criar Post')


class FormPesquisaPasta(FlaskForm):
    pasta_instrumento = SelectField('Instrumento', choices=[i.nome_instrumento for i in Instrumentos.query.order_by('nome_instrumento')])
    botao_submit_pesquisa = SubmitField('Pesquisar')


class FormUpload(FlaskForm):
    pesquisa_instrumento = SelectField('Instrumento', choices=[i.nome_instrumento for i in Instrumentos.query.order_by('nome_instrumento')])
    arquivo = FileField('Instrumento', validators=[FileAllowed(['jpg', 'jpeg', 'pdf'], 'Arquivo não permitido, use extensões jpg ou pdf')])
    botao_submit = SubmitField('Upload')



