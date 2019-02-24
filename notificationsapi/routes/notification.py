from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError

from ..utils.http_status import HttpStatus
from ..models.base import db as orm
from ..models.notification import Notification, NotificationSchema
from ..models.category import NotificationCategory

notification_schema = NotificationSchema()

bp = Blueprint('notification', __name__)
notification = Api(bp)


class NotificationResource(Resource):
    def get(self, id):
        notification = Notification.query.get_or_404(id)
        dumped_notification = notification_schema.dump(notification).data
        return dumped_notification

    def patch(self, id):
        notification = Notification.query.get_or_404(id)
        notification_dict = request.get_json(force=True)

        if 'message' in notification_dict and notification_dict['message'] is not None:
            notification.message = notification_dict['message']

        if 'ttl' in notification_dict and notification_dict['ttl'] is not None:
            notification.duration = notification_dict['ttl']

        if (
            'displayed_times' in notification_dict
            and notification_dict['displayed_times'] is not None
        ):
            notification.displayed_times = notification_dict['displayed_times']

        if (
            'displayed_once' in notification_dict
            and notification_dict['displayed_once'] is not None
        ):
            notification.displayed_once = notification_dict['displayed_once']

        dumped_notification, dump_errors = notification_schema.dump(notification)

        if dump_errors:
            return dump_errors, HttpStatus.bad_request_400.value

        validate_errors = notification_schema.validate(dumped_notification)

        if validate_errors:
            return validate_errors, HttpStatus.bad_request_400.value

        try:
            notification.update()
            return self.get(id)
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.bad_request_400.value

    def delete(self, id):
        notification = Notification.query.get_or_404(id)
        try:
            notification.delete(notification)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.unathorized_401.value


class NotificationListResource(Resource):
    def get(self):
        notifications = Notification.query.all()
        dump_result = notification_schema.dump(notifications, many=True).data
        return dump_result

    def post(sef):
        notification_category_dict = request.get_json()

        if not notification_category_dict:
            response = {'message': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value

        errors = notification_schema.validate(notification_category_dict)

        if errors:
            return errors, HttpStatus.bad_request_400.value

        try:
            notification_category_name = notification_category_dict[
                'notification_category'
            ]
            notification_category = NotificationCategory.query.filter_by(
                name=notification_category_name
            ).first()

            if notification_category is None:
                # Create a new NotificationCategory
                notification_category = NotificationCategory(
                    name=notification_category_name
                )
                orm.session.add(notification_category)
            # Now that we are sure we have a notification category
            # we can create a new Notification
            notification = Notification(
                message=notification_category_dict['message'],
                ttl=notification_category_dict['ttl'],
                notification_category=notification_category,
            )
            notification.add(notification)
            query = Notification.query.get(notification.id)
            dump_result = notification_schema.dump(query).data
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {'error': str(e)}
            return response, HttpStatus.bad_request_400.value


notification.add_resource(NotificationListResource, '/notifications')
notification.add_resource(NotificationResource, '/notifications/<int:id>')
