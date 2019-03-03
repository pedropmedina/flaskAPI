from flask_httpauth import HTTPBasicAuth
from flask import g, Blueprint, request
from flask_restful import Resource, Api
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ..utils.http_status import HttpStatus
from ..models.user import User, UserSchema
from ..helpers import PaginationHelper
from ..models.base import ma as orm

auth = HTTPBasicAuth()

bp = Blueprint('user', __name__)
user = Api(bp)

user_schema = UserSchema(unknown='EXCLUDE')


@auth.verify_password
def verify_user_password(name, password):
    user = User.query.filter_by(name=name).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]


class UserResource(AuthenticationRequiredResource):
    def get(self, id):
        user = User.query.get_or_404(id)
        result = user_schema.dump(user)
        return result


class UserListResource(Resource):
    @auth.login_required
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=User.query,
            resource_for_url='user.userlistresource',
            key_name='results',
            schema=user_schema,
        )
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        json_data = request.get_json()
        if not json_data:
            response = {'user': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value

        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {'messages': err.messages}, HttpStatus.bad_request_400.value

        user_name = data['name']
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user is not None:
            response = {'user': f'An user with the name {user_name} already exists.'}
            return response, HttpStatus.bad_request_400.value

        try:
            print('json_data --> ', json_data)
            user = User(name=user_name)
            error_message, password_ok = user.check_password_strength_and_hash_if_ok(
                json_data['password']
            )
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                user_result = user_schema.dump(query)
                return user_result, HttpStatus.created_201.value
            else:
                return {'message': error_message}
        except SQLAlchemyError as err:
            orm.session.rollback()
            response = {'message': str(err)}
            return response, HttpStatus.bad_request_400.value


user.add_resource(UserResource, '/users/<int:id>')
user.add_resource(UserListResource, '/users')
