from flask import Flask
from flask_restful import abor, Api, fields, marshal_with, reqparse, Resource
from datetime import datetime
from pytz import utc

from models import NotificationModel
from http_status import HttpStatus


class NotificationManager:
    last_id = 0

    def __init__(self):
        self.notification = {}

    def insert_notification(self, notification):
        self.__class__.last_id += 1
        notification.id = self.__class__.last_id
        self.notification[self.__class__.last_id] = notification

    def get_notification(self, id):
        return self.notification[id]

    def delete_notification(self, id):
        del self.notification[id]
