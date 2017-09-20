from flask import Flask, request
from flask_restful import Resource, fields, marshal_with
from models.kairatools_models import User


class UsersRoute(Resource):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'picture': fields.String
    }

    @marshal_with(user_fields)
    def get(self):
        try:
            return User.get()
        except User.DoesNotExist:
            return {}

