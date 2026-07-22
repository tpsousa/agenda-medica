"""Cria as tabelas do banco de dados e o usuário de teste.

Uso: python seed.py
"""
import logging

from app import create_app
from app.extensions import db
from app.models import User

logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TEST_USERNAME = "admin"
TEST_EMAIL = "admin@timesaver.com.br"
TEST_PASSWORD = "admin123"


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(username=TEST_USERNAME).first() is None:
            user = User(username=TEST_USERNAME, email=TEST_EMAIL)
            user.set_password(TEST_PASSWORD)
            db.session.add(user)
            db.session.commit()
            logger.info("Usuário de teste criado (%s / %s).", TEST_USERNAME, TEST_PASSWORD)
        else:
            logger.info("Usuário de teste já existe, nenhuma ação necessária.")


if __name__ == "__main__":
    seed()
