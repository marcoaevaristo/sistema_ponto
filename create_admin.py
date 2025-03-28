from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def criar_admin():
    with app.app_context():
        # Primeiro, vamos verificar se o banco de dados existe
        db.create_all()
        
        # Verificar se o admin já existe
        admin = Usuario.query.filter_by(email='admin@admin.com').first()
        if not admin:
            admin = Usuario(
                nome='Administrador',
                email='admin@admin.com',
                senha=generate_password_hash('admin123'),
                cargo='Administrador',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Usuário admin criado com sucesso!')
            print('Email: admin@admin.com')
            print('Senha: admin123')
        else:
            print('Usuário admin já existe!')

if __name__ == '__main__':
    criar_admin()
