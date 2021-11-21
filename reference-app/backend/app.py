from flask import Flask, render_template, request, jsonify

import pymongo
import logging
from flask_pymongo import PyMongo

# https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-internal/config.py
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics


# Tracing
from jaeger_client import Config

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# from prometheus_flask_exporter import PrometheusMetrics
# Since we're using gunicorn - https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-internal
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics


# Jaeger Tracing Config
'''
trace.set_tracer_provider(TracerProvider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "backend"})
    )
))

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(JaegerExporter())
    )

tracer = trace.get_tracer(__name__)
'''

# Backend app
app = Flask(__name__)

FlaskInstrumentor().instrument_app(app, excluded_urls="metrics")
RequestsInstrumentor().instrument()

# metrics = PrometheusMetrics(app, group_by='endpoint')
metrics = GunicornInternalPrometheusMetrics(app)
# static information as metric
# metrics.info('backend_app_info', 'Backend App Prometheus Metrics', version='1.0.3')

app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

mongo = PyMongo(app)


# Another way to configure a tracer
def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('backend')

@app.route('/')
def homepage():
    with tracer.start_active_span('home-page'):
        answer = "I'm on the home page"
    return jsonify(response=answer)


@app.route('/api')
def my_api():
    with tracer.start_span('my-api'):
        answer = "something"
    return jsonify(response=answer)

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == "__main__":
    app.run()
