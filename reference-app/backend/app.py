from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import pymongo
import logging
from flask_pymongo import PyMongo
# Tracing
from jaeger_client import Config
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# from prometheus_flask_exporter import PrometheusMetrics
# Since we're using gunicorn - https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-internal
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_flask_exporter import PrometheusMetrics

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

# Configure Jaeger tracer
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
        validate=True
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('backend')

# Backend app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
CORS(app)

# FlaskInstrumentor().instrument_app(app, excluded_urls="metrics")
# RequestsInstrumentor().instrument()

metrics = GunicornInternalPrometheusMetrics(app, group_by='endpoint')
# metrics = PrometheusMetrics(app, group_by='endpoint')

# static information as metric
metrics.info('backend', 'Backend App Metrics', version='1.0.3')

# register extra metrics
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths', labels={'path': lambda: request.path}
    )
)

# custom metric to be applied to multiple endpoints
endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

mongo = PyMongo(app)

@app.route('/')
@endpoint_counter
def homepage():
    with tracer.start_active_span('home-page'):
        answer = "I'm on the home page"
        return jsonify(response=answer)


@app.route('/api')
@endpoint_counter
def my_api():
    with tracer.start_span('my-api'):
        answer = "something"
        return jsonify(response=answer)

@app.route('/star', methods=['POST'])
@endpoint_counter
def add_star():
    with tracer.start_span('add star'):
        star = mongo.db.stars
        name = request.json['name']
        distance = request.json['distance']
        star_id = star.insert({'name': name, 'distance': distance})
        new_star = star.find_one({'_id': star_id })
        output = {'name' : new_star['name'], 'distance' : new_star['distance']}
        return jsonify({'result' : output})


if __name__ == "__main__":
    app.run()
