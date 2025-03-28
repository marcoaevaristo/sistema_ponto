from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app, db, login_manager
from models import Usuario, RegistroPonto
import pandas as pd
from datetime import datetime, timedelta
import pytz

def get_sp_time():
    sp_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(sp_tz)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Você precisa ser um administrador.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'warning')
            return redirect(url_for('login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html', year=datetime.now().year)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cargo = request.form.get('cargo')
        
        if not nome or not email or not senha or not cargo:
            flash('Por favor, preencha todos os campos.')
            return redirect(url_for('registrar'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.')
            return redirect(url_for('registrar'))
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            cargo=cargo,
            is_admin=False
        )
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login para continuar.')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.')
    
    return render_template('registrar.html')

@app.route('/registrar_ponto', methods=['POST'])
@login_required
def registrar_ponto():
    tipo = request.form.get('tipo')
    novo_registro = RegistroPonto(
        tipo=tipo,
        usuario_id=current_user.id,
        data=get_sp_time()
    )
    db.session.add(novo_registro)
    db.session.commit()
    flash('Ponto registrado com sucesso!')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    registros = RegistroPonto.query.filter_by(usuario_id=current_user.id)\
        .order_by(RegistroPonto.data.desc()).all()
    
    registros_por_dia = {}
    for registro in registros:
        data = registro.data.date()
        if data not in registros_por_dia:
            registros_por_dia[data] = {
                'entrada': None,
                'inicio_almoco': None,
                'fim_almoco': None,
                'saida': None,
                'horas_trabalhadas': timedelta(0)
            }
        registros_por_dia[data][registro.tipo] = registro.data
    
    return render_template('dashboard.html', 
                         registros_por_dia=registros_por_dia,
                         current_time=get_sp_time())

@app.route('/relatorios')
@login_required
def relatorios():
    registros = RegistroPonto.query.filter_by(usuario_id=current_user.id)\
        .order_by(RegistroPonto.data.desc()).all()
    
    registros_por_dia = {}
    total_horas = timedelta(0)
    
    for registro in registros:
        data = registro.data.date()
        if data not in registros_por_dia:
            registros_por_dia[data] = {
                'entrada': None,
                'inicio_almoco': None,
                'fim_almoco': None,
                'saida': None,
                'horas_trabalhadas': timedelta(0)
            }
        registros_por_dia[data][registro.tipo] = registro.data
    
    for data, reg in registros_por_dia.items():
        tempo_manha = reg['inicio_almoco'] - reg['entrada'] if reg['entrada'] and reg['inicio_almoco'] else timedelta(0)
        tempo_tarde = reg['saida'] - reg['fim_almoco'] if reg['fim_almoco'] and reg['saida'] else timedelta(0)
        reg['horas_trabalhadas'] = tempo_manha + tempo_tarde
        total_horas += reg['horas_trabalhadas']
    
    momento_geracao = get_sp_time().strftime('%d/%m/%Y às %H:%M:%S')
    return render_template('relatorios.html',
                         registros_por_dia=registros_por_dia,
                         total_horas=total_horas,
                         funcionario=current_user,
                         momento_geracao=momento_geracao)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    usuarios = Usuario.query.all()
    registros = RegistroPonto.query.order_by(RegistroPonto.data.desc()).all()
    return render_template('admin_dashboard.html', usuarios=usuarios, registros=registros)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('login'))

@app.route('/cadastrar_funcionario', methods=['GET', 'POST'])
@login_required
@admin_required  # Apenas admin pode cadastrar funcionários
def cadastrar_funcionario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cargo = request.form.get('cargo')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return redirect(url_for('cadastrar_funcionario'))
        
        novo_funcionario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            cargo=cargo,
            is_admin=False
        )
        
        try:
            db.session.add(novo_funcionario)
            db.session.commit()
            flash('Funcionário cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_funcionarios'))
        except:
            db.session.rollback()
            flash('Erro ao cadastrar funcionário.', 'error')
            
    return render_template('cadastrar_funcionario.html')

@app.route('/listar_funcionarios')
@login_required
@admin_required
def listar_funcionarios():
    funcionarios = Usuario.query.all()
    return render_template('listar_funcionarios.html', funcionarios=funcionarios)

@app.route('/editar_funcionario/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_funcionario(id):
    funcionario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        funcionario.nome = request.form.get('nome')
        funcionario.email = request.form.get('email')
        funcionario.cargo = request.form.get('cargo')
        
        if request.form.get('senha'):
            funcionario.senha = generate_password_hash(request.form.get('senha'))
        
        try:
            db.session.commit()
            flash('Funcionário atualizado com sucesso!', 'success')
            return redirect(url_for('listar_funcionarios'))
        except:
            db.session.rollback()
            flash('Erro ao atualizar funcionário.', 'error')
    
    return render_template('editar_funcionario.html', funcionario=funcionario)

@app.route('/deletar_funcionario/<int:id>')
@login_required
@admin_required
def deletar_funcionario(id):
    if current_user.id == id:
        flash('Você não pode deletar seu próprio usuário.', 'error')
        return redirect(url_for('listar_funcionarios'))
        
    funcionario = Usuario.query.get_or_404(id)
    try:
        db.session.delete(funcionario)
        db.session.commit()
        flash('Funcionário removido com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao remover funcionário.', 'error')
    
    return redirect(url_for('listar_funcionarios'))
