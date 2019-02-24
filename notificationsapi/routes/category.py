from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError

from ..utils.http_status import HttpStatus
from ..models.base import db as orm
from ..models.category import NotificationCategory, NotificationCategorySchema


notification_category_schema = NotificationCategorySchema()

bp = Blueprint('category', __name__)
category = Api(bp)


class NotificationCategoryResource(Resource):
    def get(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        dump_result = notification_category_schema.dump(notification_category).data
        return dump_result

    def patch(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        notification_category_dict = request.get_json()
        if not notification_category_dict:
            response = {'message': 'Not input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = notification_category_schema.validate(notification_category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        try:
            if (
                'name' in notification_category_dict
                and notification_category_dict['name'] is not None
            ):
                notification_category.update()
                return self.get(id)
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.bad_request_400.value

    def delete(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        try:
            notification_category.delete(notification_category)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.unathorized_401.value


class NotificationCatergoryListResource(Resource):
    def get(self):
        notification_categories = NotificationCategory.query.all()
        dump_results = notification_category_schema.dump(
            notification_categories, many=True
        )
        return dump_results

    def post(self):
        notification_category_dict = request.get_json()
        if not notification_category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = notification_category_schema.validate(notification_category_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        try:
            notification_category = NotificationCategory(
                notification_category_dict['name']
            )
            notification_category.add(notification_category)
            query = NotificationCategory.query.get(notification_category.id)
            dump_result = notification_category_schema.dump(query).data
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.bad_request_400.value


category.add_resource(NotificationCatergoryListResource, '/notification_categories')
category.add_resource(NotificationCategoryResource, '/notification_categories/<int:id>')
