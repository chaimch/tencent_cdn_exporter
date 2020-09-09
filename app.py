#!/usr/bin/env python
# -*- coding:utf-8 -*-
from random import randint
from flask import Flask, Response
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CollectorRegistry

app = Flask(__name__)

registry = CollectorRegistry()

counter = Counter('my_counter', 'an example showed how to use counter', ['machine_ip'], registry=registry)
gauge = Gauge('my_gauge', 'an example showed how to use gauge', ['machine_ip'], registry=registry)
buckets = (100, 200, 300, 500, 1000, 3000, 10000, float('inf'))
histogram = Histogram('my_histogram', 'an example showed how to use histogram', ['machine_ip'], registry=registry, buckets=buckets)
summary = Summary('my_summary', 'an example showed how to use summary', ['machine_ip'], registry=registry)


@app.route('/metrics')
def hello():
    counter.labels('127.0.0.1').inc(1)
    gauge.labels('127.0.0.1').set(2)
    histogram.labels('127.0.0.1').observe(1001)
    summary.labels('127.0.0.1').observe(randint(1, 10))
    return Response(generate_latest(registry), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
