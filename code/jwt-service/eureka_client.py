import py_eureka_client.eureka_client as eureka_client


def init_eureka(app_name, port):
    eureka_client.init(
        eureka_server="http://localhost:8761/eureka",
        app_name=app_name,
        instance_port=port,
        instance_host="localhost",
        renewal_interval_in_secs=10,
        duration_in_secs=30
    )
