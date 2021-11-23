from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
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
# Since we're using gunicorn, use this - https://github.com/rycus86/prometheus_flask_exporter/blob/master/examples/gunicorn-internal/requirements.txt
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_flask_exporter import PrometheusMetrics


'''
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)
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

tracer = init_tracer('frontend')

# Frontend app
app = Flask(__name__)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
CORS(app)

# add this missing from starter code
metrics = GunicornInternalPrometheusMetrics(app, group_by='endpoint')
# metrics.info("frontend_app_info", "Frontend App Prometheus Metrics", version="1.0.3")

# static information as metric
metrics.info('frontend', 'Frontend App Metrics', version='1.0.3')

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


@app.route('/')
@endpoint_counter
def homepage():
    with tracer.start_span('front-end-homepage') as span:
        span.set_tag('message', 'Welcome to the front end')
    return render_template("main.html")

@app.route('/test')
@endpoint_counter
def test():
    with tracer.start_span('front-end-errortest') as span:
        span.set_tag('message', 'This will create an error - 4XX')
    return render_template("error.html")


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/403")
def status_code_403():
    status_code = 403
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/404")
def status_code_404():
    status_code = 404
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/500")
def status_code_500():
    status_code = 500
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/503")
def status_code_503():
    status_code = 503
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
    
if __name__ == "__main__":
    app.run()