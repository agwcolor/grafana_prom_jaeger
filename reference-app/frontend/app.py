from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics

# Frontend app
app = Flask(__name__)

metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')

@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()