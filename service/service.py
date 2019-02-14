from flask import Flask
from flask_restful import abort, Api, fields, marshal_with, reqparse, Resource
from datetime import datetime
from pytz import utc

from models import NotificationModel
from http_status import HttpStatus

app = Flask(__name__)
service = Api(app)


notification_fields = {
    'id': fields.Integer,
    'uri': fields.Url('notification_endpoint'),
    'message': fields.String,
    'ttl': fields.Integer,
    'creation_data': fields.DateTime,
    'notification_category': fields.String,
    'displayed_times': fields.Integer,
    'display_once': fields.Boolean,
}


class NotificationManager:
    last_id = 0

    def __init__(self):
        self.notifications = {}

    def insert_notification(self, notification):
        self.__class__.last_id += 1
        notification.id = self.__class__.last_id
        self.notifications[self.__class__.last_id] = notification

    def get_notification(self, id):
        return self.notifications[id]

    def delete_notification(self, id):
        del self.notifications[id]


notification_manager = NotificationManager()


class Notification(Resource):
    def abort_if_notification_not_found(self, id):
        if id not in notification_manager.notifications:
            abort(
                HttpStatus.not_found_404.value,
                message=f'Notification {id} doesn\'t exist.',
            )

    # marshal_with helps in serializing and filtering the response
    # object. Only the fields set in the notification_fields will
    # be returned filtering out the rest. While setting up the
    # notification_fields, we also serialize the each fields to
    # ensure we get the data type specified.
    # What's important to remember is that marshal_with works on
    # the response object, not the request
    @marshal_with(notification_fields)
    def get(self, id):
        self.abort_if_notification_not_found(id)
        return notification_manager.get_notification(id)

    def delete(self, id):
        self.abort_if_notification_not_found(id)
        notification_manager.delete_notification(id)
        return ('', HttpStatus.no_content_204.value)

    @marshal_with(notification_fields)
    def patch(self, id):
        self.abort_if_notification_not_found(id)
        notification = notification_manager.get_notification(id)

        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str)
        parser.add_argument('ttl', type=int)
        parser.add_argument('display_times', type=int)
        parser.add_argument('display_once', type=bool)
        args = parser.parse_args()

        print(args)
        if 'message' in args and args['message'] is not None:
            notification.message = args['message']
        if 'ttl' in args and args['ttl'] is not None:
            notification.ttl = args['ttl']
        if 'display_times' in args and args['display_times'] is not None:
            notification.display_times = args['display_times']
        if 'display_once' in args and args['display_once'] is not None:
            notification.display_once = args['display_once']
        return notification


class NotificationList(Resource):
    @marshal_with(notification_fields)
    def get(self):
        return [v for v in notification_manager.notifications.values()]

    @marshal_with(notification_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'message',
            type=str,
            required=True,
            help='Message cannot be left blank',
        )
        parser.add_argument(
            'ttl',
            type=int,
            required=True,
            help='Time to live cannot be left blank!',
        )
        parser.add_argument(
            'notification_category',
            type=str,
            required=True,
            help='Notification category cannot be blank!',
        )
        args = parser.parse_args()

        notification = NotificationModel(
            message=args['message'],
            ttl=args['ttl'],
            creation_date=datetime.now(utc),
            notification_category=args['notification_category'],
        )
        notification_manager.insert_notification(notification)
        return (notification, HttpStatus.created_201.value)


service.add_resource(NotificationList, '/service/notifications')
service.add_resource(
    Notification,
    '/service/notifications/<int:id>',
    endpoint='notification_endpoint',
)

if __name__ == '__main__':
    app.run(debug=True)
