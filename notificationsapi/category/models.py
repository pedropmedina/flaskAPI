from marshmallow import fields, validate

from ..db import db as orm, ma, ResourceAddUpdateDelete


# Notification Category Model
class NotificationCategory(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    name = orm.Column(orm.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


# Notification Category Schema
class NotificationCategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    # Minumum length of 3 characters
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('service.notificationcategoryresource', id='<id>', _external=True)
    notifications = fields.Nested(
        'NotificationSchema', many=True, exclude='notification_category'
    )
