from flask import Flask, make_response
from flask_graphql import GraphQLView
from flask_sockets import Sockets
from graphql_ws.gevent import GeventSubscriptionServer
import rx
import graphene
from graphql_subscriptions import (
    SubscriptionManager,
    RedisPubsub,
    SubscriptionServer
)
from template import render_graphiql

app = Flask(__name__)

# using Flask Sockets here, but could use gevent-websocket directly
# to create a websocket app and attach it to flask app object
sockets = Sockets(app)

# instantiate pubsub -- this will be used to "publish" mutations
# and also to pass it into your subscription manager
pubsub = RedisPubsub()
pubsub.pubsub.subscribe('editor_update')

class Cursor(graphene.InputObjectType):

    row = graphene.Int()
    column = graphene.Int()

class CursorOutput(graphene.ObjectType):

    row = graphene.Int()
    column = graphene.Int()

class CommandInput(graphene.InputObjectType):
    action = graphene.String(required=True)
    value = graphene.String()
    cursor_start = graphene.Field(Cursor)
    cursor_end = graphene.Field(Cursor)

class CommandOutput(graphene.ObjectType):
    action = graphene.String(required=True)
    value = graphene.String()
    cursor_start = graphene.Field(CursorOutput)
    cursor_end = graphene.Field(CursorOutput)


class Query(graphene.ObjectType):
    reverse = graphene.String(word=graphene.String())

    def resolve_reverse(self, info, word):
        return word[::-1]


class SendMessage(graphene.Mutation):

    Argument = CommandInput

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, args, info):
        # publish result of mutation to pubsub; check to see if there are any
        # active subscriptions first; this implementation uses cPickle to serialize,
        # so you could send regular python object; here I'm converting to a dict before
        # publishing
        pubsub.redis.publish('editor_update', 'lalalalal')
        print('sent message to editor_update')
        return SendMessage(ok=True)

class Mutation(graphene.ObjectType):

    send_message = SendMessage.Field()

def run(x, y):
    print(x)
    print(y)
    message = pubsub.pubsub.get_message()
    if message:
        return message['data']
    return None

class Subscription(graphene.ObjectType):

    editor_update = graphene.String()

    @staticmethod
    def resolve_editor_update(data, info):
        return rx.Observable.interval(1000).map(run)


# create schema using graphene or another python graphql library
# not showing models or schema design here for brevity
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# instantiate subscription manager object -- passing in schema and pubsub
subscription_mgr = SubscriptionManager(schema, pubsub)

@app.route('/graphiql')
def graphql_view():
    return make_response(render_graphiql())

app.add_url_rule(
    '/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=False))

# using Flask Sockets here -- on each new connection instantiate a
# subscription app / server -- passing in subscription manager and websocket
# @sockets.route('/subscriptions')
# def socket_channel(websocket):
#     subscription_server = SubscriptionServer(subscription_mgr, websocket)
#     subscription_server.handle()
#     return []


subscription_server = GeventSubscriptionServer(schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'

@sockets.route('/subscriptions')
def socket_channel(ws):
    subscription_server.handle(ws)

if __name__ == "__main__":

    # using a gevent webserver so multiple connections can be
    # maintained concurrently -- gevent websocket spawns a new
    # greenlet for each request and forwards the request to flask
    # app or socket app, depending on request type
    from geventwebsocket import WebSocketServer

    server = WebSocketServer(('', 5000), app)
    print '  Serving at host 0.0.0.0:5000...\n'
    server.serve_forever()

