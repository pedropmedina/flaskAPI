from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ..utils.http_status import HttpStatus
from ..models.base import db as orm
from ..models.category import NotificationCategory, NotificationCategorySchema
from ..models.notification import NotificationSchema


category_schema = NotificationCategorySchema(only=('id', 'name', 'url'))
categories_schema = NotificationCategorySchema(many=True)
notifications_schema = NotificationSchema(many=True, exclude=['notification_category'])

bp = Blueprint('category', __name__)
category = Api(bp)

duplicate_category_message = 'A notification category of name "{}" already exists.'


class NotificationCategoryResource(Resource):
    def get(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        category_data = category_schema.dump(notification_category)
        notifications_data = notifications_schema.dump(
            notification_category.notifications
        )
        return {'category': category_data, 'notifications': notifications_data}

    def patch(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        json_data = request.get_json()

        if not json_data:
            return (
                {'message': 'Not input data provided'},
                HttpStatus.bad_request_400.value,
            )

        if 'name' in json_data and json_data['name'] is not None:
            notification_category_name = json_data['name']
            if NotificationCategory.is_name_unique(
                id=0, name=notification_category_name
            ):
                notification_category.name = notification_category_name
            else:
                response = {
                    'message': duplicate_category_message.format(
                        notification_category_name
                    )
                }
                return response, HttpStatus.bad_request_400.value

        try:
            category_data = category_schema.dump(notification_category)
            notifications_data = notifications_schema.dump(
                notification_category.notifications
            )
        except ValidationError as err:
            return {'messages': err.messages}, 422

        try:
            notification_category.update()
            return {'category': category_data, 'notifications': notifications_data}
        except SQLAlchemyError as err:
            orm.session.rollback()
            return {'messages': str(err)}, HttpStatus.bad_request_400.value

    def delete(self, id):
        notification_category = NotificationCategory.query.get_or_404(id)
        try:
            notification_category.delete(notification_category)
            response = make_response()
            return str(response), HttpStatus.no_content_204.value
        except SQLAlchemyError as err:
            orm.session.rollback()
            return {'messages': str(err)}, HttpStatus.unathorized_401.value


class NotificationCatergoryListResource(Resource):
    def get(self):
        notification_categories = NotificationCategory.query.all()
        categories_data = categories_schema.dump(notification_categories)
        return {'categories': categories_data}

    def post(self):
        json_data = request.get_json()

        if not json_data:
            return (
                {'message': 'No input data provided'},
                HttpStatus.bad_request_400.value,
            )

        try:
            category_data = category_schema.load(json_data)
        except ValidationError as err:
            return {'messages': err.messages}, 422

        # check for category uniqueness
        notification_category_name = category_data['name']
        if not NotificationCategory.is_name_unique(
            id=0, name=notification_category_name
        ):
            response = {
                'message': duplicate_category_message.format(notification_category_name)
            }
            return response, HttpStatus.bad_request_400.value

        try:
            notification_category = NotificationCategory(name=category_data['name'])
            notification_category.add(notification_category)
            query = NotificationCategory.query.get(notification_category.id)
            category_data = category_schema.dump(query)
            notifications_data = notifications_schema.dump(
                notification_category.notifications
            )
            return (
                {'category': category_data, 'notifications': notifications_data},
                HttpStatus.created_201.value,
            )
        except SQLAlchemyError as err:
            orm.session.rollback()
            return {'messages': str(err)}, HttpStatus.bad_request_400.value


category.add_resource(NotificationCatergoryListResource, '/notification_categories')
category.add_resource(NotificationCategoryResource, '/notification_categories/<int:id>')
