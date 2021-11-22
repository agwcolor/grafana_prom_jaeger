from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging, requests

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

tracer = init_tracer('trial')



app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
CORS(app)

# add this missing from starter code
metrics = GunicornInternalPrometheusMetrics(app, group_by='endpoint')
# metrics.info("trial_app_info", "Trial App Prometheus Metrics", version="1.0.3")

# static information as metric
metrics.info('trial', 'Trial App Metrics', version='1.0.3')

# custom metric to be applied to multiple endpoints
endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

# register extra metrics
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths', labels={'path': lambda: request.path}
    )
)

#config = Config(
#        config={},
#        service_name='your-app-name',
#        validate=True,
#        metrics_factory=PrometheusMetricsFactory(service_name_label='your-app-name')
#)
#tracer = config.initialize_tracer()

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

tracer = init_tracer('trial')

@app.route('/')
def homepage():
    # return render_template("main.html")
    with tracer.start_span('get-python-jobs') as span:
        homepages = []
        res = requests.get('https://jobs.github.com/positions.json?description=python')
        span.set_tag('first-tag', len(res.json()))
        for result in res.json():
            try:
                homepages.append(requests.get(result['company_url']))
            except:
                return "Unable to get site for %s" % result['company']
    return jsonify(homepages)

if __name__ == "__main__":
    app.run(debug=True,)