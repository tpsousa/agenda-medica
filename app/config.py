import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///agenda.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Serviço (real ou mockado) de onde os agendamentos são buscados via HTTP.
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5001")
    API_TIMEOUT = float(os.environ.get("API_TIMEOUT", "5"))
