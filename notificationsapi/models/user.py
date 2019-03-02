import re
from passlib import custom_app_context as password_context
from marshmallow import fields, validate

from .base import ma, db as orm, ResourceAddUpdateDelete


class User(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    name = orm.Column(orm.String(50), unique=True, nullable=False)
    password_hash = orm.Column(orm.String(120), nullable=False)
    creation_date = orm.Column(
        orm.TIMESTAMP, server_default=orm.func.current_timestamp()
    )

    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def check_password_strength_and_hash_if_ok(self, password):
        if len(password) < 8:
            return (
                'The password is too short. Please, specify a password wit at least 8 \
                        characters',
                False,
            )
        if len(password) > 32:
            return (
                'The password is too long. Please, specify a password with \
                    no more that 32 characters.',
                False,
            )
            if re.search(r'[A-Z]', password) is None:
                return 'The password must include at least one uppercase letter', False
            if re.search(r'[a-z]', password) is None:
                return 'The password must include at lease one lowercase letter', False
            if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
                return 'The password must include at least one symbol', False
            self.password_hash = password_context.hash(password)
            return '', True


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('user.userresource', id='<id>', _external=True)
