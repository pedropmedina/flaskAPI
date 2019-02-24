from marshmallow import fields, pre_load, validate

from ..db import db as orm, ma, ResourceAddUpdateDelete


# Notfication Model
class Notification(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    message = orm.Column(orm.String(250), unique=True, nullable=False)
    ttl = orm.Column(orm.Integer, nullable=False)
    creation_date = orm.Column(
        orm.TIMESTAMP, server_default=orm.func.current_timestamp()
    )
    notification_category_id = orm.Column(
        orm.Integer,
        orm.ForeignKey('notification_category.id', ondelete='CASCADE'),
        nullable=False,
    )
    notification_category = orm.relationship(
        'NotificationCategory',
        backref=orm.backref(
            'notifications', lazy='dynamic', order_by='Notification.message'
        ),
    )
    displayed_times = orm.Column(orm.Integer, nullable=False, server_default='0')
    displayed_once = orm.Column(orm.Boolean, nullable=False, server_default='false')

    def __init__(self, message, ttl, notification_category):
        self.message = message
        self.ttl = ttl
        self.notification_category = notification_category


# Notification Schema
class NotificationSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    message = fields.String(required=True, validate=validate.Length(5))
    ttl = fields.Integer()
    creation_date = fields.DateTime()
    notification_category = fields.Nested(
        'NotificationCategorySchema', only=['id', 'url', 'name'], required=True
    )
    displayed_times = fields.Integer()
    displayed_once = fields.Boolean()
    url = ma.URLFor('service.notificationsresouce', id='<id>', _external=True)

    @pre_load
    def process_notification_category(self, data):
        notification_category = data.get('notification_category')
        if notification_category:
            if isinstance(notification_category, dict):
                notification_category_name = notification_category.get('name')
            else:
                notification_category_name = notification_category
            notification_category_dict = dict(name=notification_category_name)
        else:
            notification_category_dict = {}
        data['notification_category'] = notification_category_dict
        return data
