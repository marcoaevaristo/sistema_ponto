from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pytz
from datetime import datetime

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurações da aplicação
app.config['SECRET_KEY'] = 'sua_chave_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados
db = SQLAlchemy(app)

# Configura o gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Filtro de template para formatar datas
@app.template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M:%S'):
    if value is None:
        return ''
    if value.tzinfo is None:
        sp_tz = pytz.timezone('America/Sao_Paulo')
        value = pytz.utc.localize(value).astimezone(sp_tz)
    return value.strftime(format)

# Importa as rotas
from routes import *
