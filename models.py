from app import db
from flask_login import UserMixin
from datetime import datetime
import pytz

def get_sp_time():
    # Obtém o fuso horário de São Paulo/Brasília
    sp_tz = pytz.timezone('America/Sao_Paulo')
    # Retorna a hora atual em SP
    return datetime.now(sp_tz)

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    registros = db.relationship('RegistroPonto', backref='usuario', lazy=True)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class RegistroPonto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=get_sp_time)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, inicio_almoco, fim_almoco, saida
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<RegistroPonto {self.usuario_id} - {self.tipo}>'
