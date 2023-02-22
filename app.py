#!/usr/bin/env python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

# initializing app
app = Flask(__name__)
app.debug = True

# Configs
# Might need to modify below as needed for your pg setup: app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@hostname/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/apartment'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Modules
db = SQLAlchemy(app)

# Models
class Apartment(db.Model):
  __tablename__ = 'apartments'
  id = db.Column(db.Integer, primary_key=True)
  url = db.Column(db.String(255))
  price = db.Column(db.Integer)
  address = db.Column(db.String(255))
  bedroom = db.Column(db.Float)
  bathroom = db.Column(db.Float)


# Schema Objects
class ApartmentObject(SQLAlchemyObjectType):
  class Meta:
    model = Apartment
    interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
  node = graphene.relay.Node.Field()
  all_apartments = SQLAlchemyConnectionField(ApartmentObject)

# query based off neighborhood

# query based off rent

# query based off bedroom count and bathroom count

schema = graphene.Schema(query=Query)

# Routes
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.route('/')
def index():
  return 'Welcome to the Ahsun Apartment API'

if __name__ == '__main__':
  db.create_all()
  app.run()
