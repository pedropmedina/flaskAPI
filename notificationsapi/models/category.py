from marshmallow import fields, validate

from .base import db as orm, ma, ResourceAddUpdateDelete


# Notification Category Model
class NotificationCategory(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    name = orm.Column(orm.String(150), unique=True, nullable=False)


# Notification Category Schema
class NotificationCategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('category.notificationcategoryresource', id='<id>', _external=True)
