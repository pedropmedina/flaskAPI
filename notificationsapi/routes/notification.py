from flask import Blueprint, request, make_response, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError

from ..utils.http_status import HttpStatus
from ..models.base import db as orm
from ..models.notification import Notification, NotificationSchema
from ..models.category import NotificationCategory, NotificationCategorySchema

notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

bp = Blueprint('notification', __name__)
notification = Api(bp)


class NotificationResource(Resource):
    def get(self, id):
        notification = Notification.query.get_or_404(id)
        notification_result = notification_schema.dump(notification)
        return jsonify({'notification': notification_result})

    def patch(self, id):
        notification = Notification.query.get_or_404(id)
        json_data = request.get_json()

        if 'message' in json_data and json_data['message'] is not None:
            notification.message = json_data['message']

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
            return jsonify({'notification': data})
        except SQLAlchemyError as err:
            orm.session.rollback()
            response = {'messages': str(err)}
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
        notifications_result = notifications_schema.dump(notifications)
        return jsonify({'notifications': notifications_result})

    def post(sef):
        json_data = request.get_json()

        if not json_data:
            return (
                jsonify({'message': 'No input data provided'}),
                HttpStatus.bad_request_400.value,
            )

        try:
            data = notification_schema.load(json_data)
        except ValidationError as err:
            return {'messages': err.messages}, 422

        try:
            notification_category_name = json_data['notification_category']['name']
            notification_category = NotificationCategory.filter_by(
                name=notification_category_name
            ).first()

            if notification_category is None:
                # create new NotificationCategory
                notification_category = NotificationCategory(notification_category_name)
                orm.session.add(notification_category)

            # create Notification
            notification = Notification(
                message=data['message'],
                ttl=data['ttl'],
                notification_category=notification_category,
            )
            orm.session.add(notification)
            orm.session.commit()
            result = NotificationSchema.dump(Notification.query.get(id))
            return jsonify({'notification': result}), HttpStatus.created_201.value
        except SQLAlchemyError as err:
            orm.session.rollback()
            return {'messages': str(err)}, HttpStatus.bad_request_400.value


notification.add_resource(NotificationListResource, '/notifications')
notification.add_resource(NotificationResource, '/notifications/<int:id>')
