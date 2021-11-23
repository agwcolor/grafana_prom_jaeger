**Note:** For the screenshots, you can store all of your answer images in the `answer-img` directory.

## Verify the monitoring installation

*TODO: 1* run `kubectl` command to show the running pods and services for all components. Take a screenshot of the output and include it here to verify the installation (see : ![default ns](/answer-img/1a_pods_services_default_ns.png) | ![monitoring ns](/answer-img/1b_pods_services_monitoring_ns.png)

## Setup the Jaeger and Prometheus source
*TODO: Expose Grafana to the internet and then setup Prometheus as a data source. Provide a screenshot of the home page after logging into Grafana. ![grafana prom datasource](/answer-img/2a_grafana_prometheus_datasource.png) | ![grafana home page](/answer-img/2b_grafana_home_screen.png) 

## Create a Basic Dashboard
*TODO:* ![prometheus basic dashboard](/answer-img/3_basic_dashboard_showing_prometheus.png) : Create a dashboard in Grafana that shows Prometheus as a source. Take a screenshot and include it here.

## Describe SLO/SLI
*TODO:* Describe, in your own words, what the SLIs are, based on an SLO of *monthly uptime* and *request response time*.

Actual *monthly uptime* and *request response time* are SLIs (service level indicators, or metrics) that can be used to determine if an SLO has been met. For example, let's say that our SLO for *monthly uptime* is at least 99.99% per month, and our SLO for *request response time* is less than 3 seconds on average.

The following general SLIs can have a bearing on whether the SLOs will be met directly or indirectly. These can be further broken down and visualized via specific metrics. 
- % uptime that a service is active
- Failure rate for a service. This could potentially affect monthly uptime.
- Latency - How long does it take to respond to a request? This directly measures the request response time SLI.
- Saturation - how heavy a load the servers have (saturation). This could cause downtime and slow response times
- Traffic - how much traffic are the servers getting? Perhaps there are times when servers get a spike in traffic. This could directly impact response times and uptime as well.


## Creating SLI (KPI) metrics.
*TODO:* It is important to know why we want to measure certain metrics for our customer. Describe in detail 5 metrics to measure these SLIs.
- Response types: Flask HTTP requests status 200, 500, 400
- Failed responses per second
- Uptime: frontend, trial, backend
- Pods health: Pods not ready
- Pods health: Pod restarts by namespace
- Average Response time (Latency)

## Create a Dashboard to measure our SLIs
*TODO:* Create a dashboard to measure the uptime of the frontend and backend services We will also want to measure to measure 40x and 50x errors. Create a dashboard that show these values over a 24 hour period and take a screenshot. (![400 & 500 errors](/answer-img/4_Uptime_4xx_5xx_errors_24h.png))

## Tracing our Flask App
*TODO:*  We will create a Jaeger span to measure the processes on the backend. Once you fill in the span, provide a screenshot of it here.
(![jaeger code](/answer-img/5_JaegerTraceScreenshot_backend.png) | ![jaeger trace](/answer-img/5_JaegerTraceCode.png))

## Jaeger in Dashboards
*TODO:* Now that the trace is running, let's add the metric to our current Grafana dashboard. Once this is completed, provide a screenshot of it here. (![jaeger in grafana](/answer-img/6_JaegerInDashboard.png))


## Report Error
*TODO:* Using the template below, write a trouble ticket for the developers, to explain the errors that you are seeing (400, 500, latency) and to let them know the file that is causing the issue.

TROUBLE TICKET

Name: 400 Errors & 500 Errors

Date: 11/22/2021

Subject: Errors in Backend App & Trial App

Affected Area: Backend App.py "/star" endpoint & Trial App.py "/" root endpoint

Severity: Severe

Description:  Errors in Backend App (405 error, method not allowed /star endpoint) & Trial App (500 error, / , main route)


## Creating SLIs and SLOs
*TODO:* We want to create an SLO guaranteeing that our application has a 99.95% uptime per month. Name three SLIs that you would use to measure the success of this SLO.
1. Uptime for each service
2. Response types - 200,4xx,5xx
3. Pod health


## Building KPIs for our plan

*TODO*: Now that we have our SLIs and SLOs, create KPIs to accurately measure these metrics. We will make a dashboard for this, but first write them down here:

Response types app health:
**Response types : Flask HTTP requests status 200, 500, 400**
- sum(flask_http_request_total{container=~"backend|frontend|trial",status=~"500"}) by (status,container)
- sum(flask_http_request_total{container=~"backend|frontend|trial",status=~"400"}) by (status,container)
- sum(flask_http_request_total{container=~"backend|frontend|trial",status=~"200"}) by (status,container)

**Failed responses per second**
- sum(rate(flask_http_request_duration_seconds_count{status!="200"}[30s]))

**Uptime : frontend, trial, backend**
- sum(up{container=~"frontend"}) by (pod)
- sum(up{container=~"trial"}) by (pod)
- sum(up{container=~"backend"}) by (pod)

**Pods health : Pods not ready**
- sum by (namespace) (kube_pod_status_ready{condition="false"})
**Pods health : Pod restarts by namespace**
- sum by (namespace)(changes(kube_pod_status_ready{condition="true"}[5m]))

**Average Response time (Latency)**
- rate(flask_http_request_duration_seconds_sum{status="200"}[1d])/
rate(flask_http_request_duration_seconds_count{status="200"}[1d])

## Final Dashboard
*TODO*: Create a Dashboard containing graphs that capture all the metrics of your KPIs and adequately representing your SLIs and SLOs. Include a screenshot of the dashboard here, and write a text description of what graphs are represented in the dashboard.  

Dashboard : See (![Final Dashboard](/answer-img/7_FinalDashboard.png))
Panels listed are :
- Flask HTTP request total: Status "200
- Flask HTTP request exceptions
- 5xx Errors last 24 hours
- 4xx Errors last 24 hours
- Failed responses per second
- Uptime Frontend Service Last 24 hours
- Uptime Backend Service Last 24 hours
- Uptime Trial Service Last 24 hours
- Pods Per Namespace
- Pods that were not ready
- Pod restarts per namespace
- CPU Usage
- Latency: Average response time