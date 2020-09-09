# -*- coding:utf-8 -*-
import prometheus_client
from prometheus_client import Gauge, Counter
from prometheus_client.core import CollectorRegistry, REGISTRY
from flask import Response, Flask

app = Flask(__name__)
# 实例化 REGISTRY
REGISTRY = CollectorRegistry(auto_describe=False)
# 这里又加了个 sertype 的 labels，定义的 labels 一定要被用到，否则会报错
port_up = Gauge("Server_port", "monitor server port status.", ["sertype", "host", "port"], registry=REGISTRY)


@app.route("/metrics")
def requests_count():
    # 模拟多个值传入
    a = [{"sertype": "zookeeper", "host": "192.168.1.22", "port": "2181", "status": 0},
         {"sertype": "zookeeper", "host": "192.168.1.33", "port": "2181", "status": 0},
         {"sertype": "zookeeper", "host": "192.168.1.44", "port": "2181", "status": 1},
         {"sertype": "mysql", "host": "192.168.1.88", "port": "3306", "status": 0},
         {"sertype": "mysql", "host": "192.168.1.99", "port": "3306", "status": 1}]
    for i in a:
        ip = "".join(i.get("host"))
        port = "".join(i.get("port"))
        status = i.get("status")
        sertype = "".join(i.get("sertype"))
        port_up.labels(sertype, ip, port).set(status)
    return Response(prometheus_client.generate_latest(port_up),
                    mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=31672, debug=True)
