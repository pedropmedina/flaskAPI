from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ..utils.http_status import HttpStatus
from ..models.base import db as orm
from ..models.notification import Notification, NotificationSchema
from ..models.category import NotificationCategory
from ..helpers import PaginationHelper

notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

bp = Blueprint('notification', __name__)
notification = Api(bp)

duplicate_notification_message = 'A notification with message "{}" already exists.'


class NotificationResource(Resource):
    def get(self, id):
        notification = Notification.query.get_or_404(id)
        notification_result = notification_schema.dump(notification)
        return {'notification': notification_result}

    def patch(self, id):
        notification = Notification.query.get_or_404(id)
        json_data = request.get_json()

        if 'message' in json_data and json_data['message'] is not None:
            notification_message = json_data['message']
            if not Notification.is_message_unique(id=0, message=notification_message):
                return (
                    {
                        'message': duplicate_notification_message.format(
                            notification_message
                        )
                    },
                    HttpStatus.bad_request_400.value,
                )
            else:
                notification.message = notification_message

        if 'ttl' in json_data and json_data['ttl'] is not None:
            notification.duration = json_data['ttl']

        if 'displayed_times' in json_data and json_data['displayed_times'] is not None:
            notification.displayed_times = json_data['displayed_times']

        if 'displayed_once' in json_data and json_data['displayed_once'] is not None:
            notification.displayed_once = json_data['displayed_once']

        try:
            data = notification_schema.dump(notification)
        except ValidationError as err:
            return {'messages': err.messages}, 422

        try:
            notification.update()
            return {'notification': data}
        except SQLAlchemyError as err:
            orm.session.rollback()
            response = {'messages': str(err)}
            return response, HttpStatus.bad_request_400.value

    def delete(self, id):
        notification = Notification.query.get_or_404(id)

        try:
            notification.delete(notification)
            response = make_response()
            return str(response), HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'messages': str(e)}
            return response, HttpStatus.unathorized_401.value


class NotificationListResource(Resource):
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=Notification.query,
            resource_for_url='notification.notificationlistresource',
            key_name='results',
            schema=notification_schema,
        )
        pagination_result = pagination_helper.paginate_query()
        return pagination_result

    def post(sef):
        json_data = request.get_json()

        if not json_data:
            return (
                {'message': 'No input data provided'},
                HttpStatus.bad_request_400.value,
            )

        try:
            data = notification_schema.load(json_data)
        except ValidationError as err:
            return {'messages': err.messages}, 422

        notification_message = data['message']
        if not Notification.is_message_unique(id=0, message=notification_message):
            return (
                {
                    'message': duplicate_notification_message.format(
                        notification_message
                    )
                },
                HttpStatus.bad_request_400.value,
            )

        try:
            notification_category_name = json_data['notification_category']['name']
            notification_category = NotificationCategory.query.filter_by(
                name=notification_category_name
            ).first()

            if notification_category is None:
                # create new NotificationCategory
                notification_category = NotificationCategory(
                    name=notification_category_name
                )
                orm.session.add(notification_category)

            # create Notification
            notification = Notification(
                message=data['message'],
                ttl=data['ttl'],
                notification_category=notification_category,
            )
            orm.session.add(notification)
            orm.session.commit()
            result = notification_schema.dump(Notification.query.get(notification.id))
            return {'notification': result}, HttpStatus.created_201.value
        except SQLAlchemyError as err:
            orm.session.rollback()
            return {'messages': str(err)}, HttpStatus.bad_request_400.value


notification.add_resource(NotificationListResource, '/notifications')
notification.add_resource(NotificationResource, '/notifications/<int:id>')
