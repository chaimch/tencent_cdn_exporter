#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, Response
from prometheus_client import generate_latest, CollectorRegistry

from tencent import TencentCdnCollector

app = Flask(__name__)
app.config.from_json("./cdn.json")
registry = CollectorRegistry()


@app.route('/metrics')
def metrics():
    TencentCdnCollector(registry).collect()
    return Response(generate_latest(registry), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
