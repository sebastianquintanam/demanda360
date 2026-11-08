from flask_login import UserMixin
from sqlalchemy import FetchedValue
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=FetchedValue())
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())

    def set_password(self, clave: str) -> None:
        # Werkzeug usa scrypt con sal aleatoria; en la base solo queda el hash
        self.password_hash = generate_password_hash(clave)

    def check_password(self, clave: str) -> bool:
        return check_password_hash(self.password_hash, clave)

    @property
    def is_active(self) -> bool:  # Flask-Login: un usuario inactivo no puede entrar
        return bool(self.activo)

    def __repr__(self) -> str:  # nunca incluye el hash
        return f"<Usuario {self.usuario} ({self.rol})>"
