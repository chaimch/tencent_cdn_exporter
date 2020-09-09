# -*- coding:utf-8 -*-
import prometheus_client
from prometheus_client import Gauge, Counter
from flask import Response, Flask

app = Flask(__name__)
# 这次在 Gauge 类型里定义两个 labels，分别是"host"和"port",可以定义多个
port_up = Gauge("Server_port", "monitor server port status.", ["host", "port"])


@app.route("/metrics")
def requests_count():
    # 传入不同的 lables 即可一次获得多项
    port_up.labels("192.168.1.22", "2181").set(0)
    port_up.labels("192.168.1.33", "2181").set(0)
    port_up.labels("192.168.1.44", "2181").set(1)
    return Response(prometheus_client.generate_latest(port_up),
                    mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=31672, debug=True)
