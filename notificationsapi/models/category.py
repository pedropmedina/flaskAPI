from marshmallow import fields, validate

from .base import db as orm, ma, ResourceAddUpdateDelete


# Notification Category Model
class NotificationCategory(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    name = orm.Column(orm.String(150), unique=True, nullable=False)

    @classmethod
    def is_name_unique(cls, id, name):
        existing_notification_category = cls.query.filter_by(name=name).first()
        if existing_notification_category is None:
            return True
        else:
            # sqlalchemy will assign 0 to items' id that have yet to be register in db
            # Knowing that this is a brand new item confirms its uniqueness
            if existing_notification_category.id == id:
                return True
            else:
                return False


# Notification Category Schema
class NotificationCategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('category.notificationcategoryresource', id='<id>', _external=True)
