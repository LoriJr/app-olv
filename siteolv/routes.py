import cloudinary.uploader
from flask import render_template, redirect, url_for, flash, request, Response
from siteolv import app, database, bcrypt, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from siteolv.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, FormPesquisaPasta, FormUpload
from siteolv.models import Usuario, Post, Instrumentos
from flask_login import login_user, logout_user, current_user, login_required
from flask_cors import cross_origin
from flask import jsonify
import secrets
from PIL import Image
import os
import boto3
from werkzeug.utils import secure_filename


@app.route("/admin")
@login_required
def admin():
    return render_template("index.html")


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/usuarios")
def usuarios():
    lista_usuarios = Usuario.query.order_by('username')

    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/download', methods=['POST', 'GET'])
@login_required
def download():
    key = request.form['key']
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)

    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/pain',
        headers={"Content-Disposition": "attachment; filename={}".format(key)}
    )


@app.route('/viewer', methods=('GET', 'POST'))
def viewer():
    key = request.form['keys']

    url = boto3.client('s3').generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600)
    return redirect(url)


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(key).delete()
    flash(f'Arquivo ( {key} ) REMOVIDO com sucesso', 'alert-danger')

    return redirect(url_for('pasta_consultar'))


@app.route('/partitura-incluir', methods=['POST', 'GET'])
@login_required
def partitura_incluir():
    formupload = FormUpload()

    if formupload.validate_on_submit():
        item_drop_down = formupload.pesquisa_instrumento.data
        arquivo = formupload.arquivo.data

        if not arquivo:
            flash('Arquivo não selecionado', 'alert-danger')
            return render_template('partitura-incluir.html', formupload=formupload)
        try:
            file = secure_filename(arquivo.filename)
            arquivo.save(file)
            s3_client = boto3.client('s3')

            jj = arquivo.filename.split(".")[1]

            if jj == "pdf":
                s3_client.upload_file(
                    file,
                    S3_BUCKET,
                    item_drop_down + '/{}'.format(arquivo.filename),
                    ExtraArgs={'ContentType': 'application/pdf'}
                )
            elif jj == "jpeg" or "jpg":
                s3_client.upload_file(
                    file,
                    S3_BUCKET,
                    item_drop_down + '/{}'.format(arquivo.filename),
                    ExtraArgs={'ContentType': 'image/jpeg'}
                )

            flash(f'Incluído {arquivo.filename} na pasta {item_drop_down.capitalize()}', 'alert-success')

            return redirect(url_for('pasta_consultar'))
        except Exception as error:
            print(error)

    return render_template('partitura-incluir.html', formupload=formupload)


@app.route('/pasta-consultar')
@login_required
def pasta_consultar():
    form = FormPesquisaPasta()

    lista = Instrumentos.query.order_by('nome_instrumento')

    return render_template('pasta-consultar.html', form=form, lista=lista)


@app.route('/pasta-instrumento-usuario', methods=['GET', 'POST'])
@login_required
def pasta_instrumento_usuario():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)

    return render_template('pasta-instrumento-usuario.html', my_bucket=my_bucket)


@app.route('/pasta-instrumento-admin', methods=['POST', 'GET'])
@login_required
def pasta_instrumento_admin():
    formpesquisa = FormPesquisaPasta()

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    item_drop_down = formpesquisa.pasta_instrumento.data
    '''item_drop_down é variável de Prefix'''

    return render_template('pasta-instrumento-admin.html', my_bucket=my_bucket, item_drop_down=item_drop_down)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()

    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode('utf-8'), form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Bem vindo {current_user.nickname.capitalize()}!', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no Login, e-mail ou senha incorretos', 'alert-danger')

    return render_template('login.html', form_login=form_login)


@app.route('/criarconta', methods=['GET', 'POST'])
def criarconta():
    form_criarconta = FormCriarConta()

    if form_criarconta.validate_on_submit():
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript,
                          instrumento=form_criarconta.instrumento.data, nickname=form_criarconta.nickname.data,
                          anodeentrada=form_criarconta.anodeentrada.data, admin=False)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarconta.html', form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso', 'alert-success')
    return redirect(url_for('login'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = current_user.foto_perfil
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def link_foto(imagem):
    upload_cloud = cloudinary.uploader.upload(imagem)
    dic = jsonify(upload_cloud).json
    for indice, chave in dic.items():
        if 'secure_url' in indice:
            link = chave
    return link


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
@cross_origin()
def perfil_editar():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.nickname = form.nickname.data

        if form.foto_perfil.data:
            nome_imagem = link_foto(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        database.session.commit()
        flash(f'Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.nickname.data = current_user.nickname
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil-editar.html', foto_perfil=foto_perfil, form=form)


