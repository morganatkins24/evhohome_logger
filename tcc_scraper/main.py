import os
import time
from datetime import datetime
from evohomeclient2 import EvohomeClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision


# Influx
influx_server = os.environ.get('server')
influx_database = os.environ.get('database')
influx_org = os.environ.get('org')
influx_bucket = os.environ.get('bucket')
influx_token = os.environ.get('DOCKER_INFLUXDB_INIT_ADMIN_TOKEN')

influx_client = InfluxDBClient(url=f"http://{influx_server}:8086", token=influx_token, org=influx_org)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Evohome
username = os.environ.get('EVOHOME_USERNAME')
password = os.environ.get('EVOHOME_PASSWORD')

client = EvohomeClient(username, password, debug=False)

while True:
    for loc in client.locations:
        print(f"Processing data for {loc.name}")
        for device in loc._gateways[0]._control_systems[0].temperatures():
            data = device
            data["location"] = loc.name
            print(f"Processing room: {data['name']}")
            dict_structure = {
                "measurement": "temperature",
                "tags": {"location": data['location'], "room": data['name']},
                "fields": {"temperature": data['temp'], "setpoint": data['setpoint']},
                "time": datetime.now().replace(microsecond=0).isoformat()
            }
            point = Point.from_dict(dict_structure, WritePrecision.NS)
            write_api.write(bucket=influx_bucket, record=point)

    print("Sleeping for 60s")
    time.sleep(60)

