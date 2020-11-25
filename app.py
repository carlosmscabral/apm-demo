# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A sample app demonstrating Stackdriver Trace
"""
import argparse
import random
import time
import os
import logging
import googlecloudprofiler


# [START trace_demo_imports]
from flask import Flask
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace import execution_context
from opencensus.trace.propagation import google_cloud_format
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.common.monitored_resource import monitored_resource 
# [END trace_demo_imports]
import requests


app = Flask(__name__)


# [START trace_demo_middleware]
propagator = google_cloud_format.GoogleCloudFormatPropagator()


def createMiddleWare(exporter):
    # Configure a flask middleware that listens for each request and applies automatic tracing.
    # This needs to be set up before the application starts.
    middleware = FlaskMiddleware(
        app,
        exporter=exporter,
        propagator=propagator,
        sampler=AlwaysOnSampler())
    return middleware
# [END trace_demo_middleware]


@app.route('/')
def template_test():
    # Sleep for a random time to imitate a random processing time
    time.sleep(random.uniform(0, 0.5))
    service_name = os.getenv('SVC_NAME')
    if service_name == "SERVICE-ONE":
        url = "http://app-apm-svc-two:8080"
    elif service_name == "SERVICE-TWO":
        url = "http://app-apm-svc-three:8080"
    else:
        return service_name + "_" + str(time.time()) + " "
    # [START trace_context_header]
    trace_context_header = propagator.to_header(execution_context.get_opencensus_tracer().span_context)
    response = requests.get(
        url,
        headers={
          'X-Cloud-Trace-Context' : trace_context_header
        }
    )
    # [END trace_context_header]
    return response.text + service_name + "_" + str(time.time()) + " "


if __name__ == "__main__":

    try:
        import googleclouddebugger
        googleclouddebugger.enable(
            breakpoint_enable_canary=False
        )
    except ImportError:
        pass

    service_name = os.getenv('SVC_NAME')



    try:
        googlecloudprofiler.start(
            service=service_name,
            service_version='1.0.1',
            # verbose is the logging level. 0-error, 1-warning, 2-info,
            # 3-debug. It defaults to 0 (error) if not set.
            verbose=3,
            # project_id must be set if not running on GCP.
            # project_id='my-project-id',
        )
    except (ValueError, NotImplementedError) as exc:
        print(exc)  # Handle errors here
        
    # [START trace_demo_create_exporter]
    createMiddleWare(StackdriverExporter())
    # [END trace_demo_create_exporter]
    app.run(host='0.0.0.0', port=8080)
