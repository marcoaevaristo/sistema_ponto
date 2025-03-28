import os
from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def reset_database():
    with app.app_context():
        # Remove o banco de dados existente
        if os.path.exists('ponto.db'):
            os.remove('ponto.db')
        
        # Cria todas as tabelas
        db.create_all()
        
        # Cria usuário admin
        admin = Usuario(
            nome='Administrador',
            email='admin@admin.com',
            senha=generate_password_hash('admin123'),
            cargo='Administrador',
            is_admin=True
        )
        
        # Adiciona ao banco de dados
        db.session.add(admin)
        db.session.commit()
        
        print('Banco de dados recriado!')
        print('Usuário admin criado:')
        print('Email: admin@admin.com')
        print('Senha: admin123')

if __name__ == '__main__':
    reset_database()
