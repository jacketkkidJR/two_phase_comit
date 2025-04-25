import asyncio
import argparse
import comm
import util
import time
import sys
import psycopg2
from datetime import datetime


async def send_execute_request(coordinator, node_id, query, timestamp, args=tuple()):
    kind = "EXECUTE"
    data = {"node_id": node_id,
            "query": query,
            "timestamp": timestamp,
            "args": args}
    return await coordinator.send(kind, data)


async def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--coordinator", type=util.hostname_port_type, required=True)
    argparser.add_argument("--demo", choices=demo_tables.keys())
    argparser.add_argument("--n-nodes", type=int)
    # argparser.add_argument("--data-db")
    args = argparser.parse_args()
    coordinator_hostname, coordinator_port = args.coordinator

    is_demo = False
    if args.demo:
        if not args.n_nodes:
            print("For demo mode, the total number of participant nodes must be given with --n-nodes.")
            return 1
        is_demo = True
    else:
        if args.n_nodes:
            print("The argument --n-nodes may only be given in demo mode.")

    coordinator = comm.RemoteCallClient(coordinator_hostname, coordinator_port)
    await coordinator.connect()
    print("Connected to coordinator at {}:{}.".format(coordinator_hostname, coordinator_port))

    if not is_demo:
        await interactive_ui(coordinator)
    else:
        await demo_ui(coordinator, args.n_nodes, args.demo)


async def interactive_ui(coordinator):
    keep_going = True
    while keep_going:
        print("QUERY --------------------")
        sys.stdout.write("Execute query:  ")
        query = input()
        sys.stdout.write("On this node #: ")
        node_id = input()
        timestamp = datetime.utcnow().timestamp()
        # print(f"Query sent time: {timestamp}")
        success = await send_execute_request(coordinator, node_id, query, timestamp)
        if not success:
            print("Error: EXECUTE was not successful. (Server may be blocked at previous transaction.)")
        sys.stdout.write("Send another query request? (y/n) ")
        keep_going = (input().lower() == "y")


async def demo_ui(coordinator, n_nodes, table):
    columns = demo_tables[table]
    create_table_query = demo_create_tables[table]
    print("Initializing tables on all participant nodes.")
    for i in range(n_nodes):
        print(f"Sending CREATE TABLE {table} query to node {i}.")
        timestamp = datetime.utcnow().timestamp()
        success = await send_execute_request(coordinator, i, create_table_query, timestamp)
        if not success:
            print(f"Failed.")
            return

    try:
        for row in data_tables[table]:
            row = list(row.values())
            node_id = hash(row[0]) % n_nodes
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ("
            for i in range(len(columns)):
                if i == 1:
                    query += f"{row[i]}, "
                if i == len(columns) - 1:
                    query += f"'{row[i]}')"
                if i != 1 and i != len(columns) - 1:
                    query += f"'{row[i]}', "
            print(query)

            print(f"Sending INSERT {row[0]} request to nodes.")
            for i in range(n_nodes):
                print(f"Sending INSERT {row[0]} query to node {i}.")
                timestamp = datetime.utcnow().timestamp()
                success = await send_execute_request(coordinator, i, query, timestamp)
                if not success:
                    print(f"Failed.")
                    return
            # success = await send_execute_request(coordinator, node_id, query, tuple(row))

            print("Sleeping for one second.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Killed.")


data_tables = {
    "thermometerobservation": [
        {"id": "thermo_001", "temperature": "22", "timeStamp": "2025-04-20 10:15:00", "sensor_id": "sensor_a"},
        {"id": "thermo_002", "temperature": "19", "timeStamp": "2025-04-20 10:20:00", "sensor_id": "sensor_b"},
        {"id": "thermo_003", "temperature": "25", "timeStamp": "2025-04-20 10:25:00", "sensor_id": "sensor_c"},
        {"id": "thermo_004", "temperature": "21", "timeStamp": "2025-04-20 10:30:00", "sensor_id": "sensor_d"},
        {"id": "thermo_005", "temperature": "18", "timeStamp": "2025-04-20 10:35:00", "sensor_id": "sensor_e"},
        {"id": "thermo_006", "temperature": "23", "timeStamp": "2025-04-20 10:40:00", "sensor_id": "sensor_f"},
        {"id": "thermo_007", "temperature": "20", "timeStamp": "2025-04-20 10:45:00", "sensor_id": "sensor_g"},
        {"id": "thermo_008", "temperature": "24", "timeStamp": "2025-04-20 10:50:00", "sensor_id": "sensor_h"},
        {"id": "thermo_009", "temperature": "26", "timeStamp": "2025-04-20 10:55:00", "sensor_id": "sensor_i"},
        {"id": "thermo_010", "temperature": "17", "timeStamp": "2025-04-20 11:00:00", "sensor_id": "sensor_j"},
    ],
    "wemoobservation": [
        {"id": "wemo_001", "currentMilliWatts": 150, "onTodaySeconds": 3600, "timeStamp": "2025-04-20 10:15:00", "sensor_id": "sensor_1"},
        {"id": "wemo_002", "currentMilliWatts": 120, "onTodaySeconds": 2700, "timeStamp": "2025-04-20 10:20:00", "sensor_id": "sensor_2"},
        {"id": "wemo_003", "currentMilliWatts": 180, "onTodaySeconds": 4200, "timeStamp": "2025-04-20 10:25:00", "sensor_id": "sensor_3"},
        {"id": "wemo_004", "currentMilliWatts": 200, "onTodaySeconds": 4800, "timeStamp": "2025-04-20 10:30:00", "sensor_id": "sensor_4"},
        {"id": "wemo_005", "currentMilliWatts": 100, "onTodaySeconds": 1800, "timeStamp": "2025-04-20 10:35:00", "sensor_id": "sensor_5"},
        {"id": "wemo_006", "currentMilliWatts": 160, "onTodaySeconds": 3900, "timeStamp": "2025-04-20 10:40:00", "sensor_id": "sensor_6"},
        {"id": "wemo_007", "currentMilliWatts": 140, "onTodaySeconds": 3000, "timeStamp": "2025-04-20 10:45:00", "sensor_id": "sensor_7"},
        {"id": "wemo_008", "currentMilliWatts": 170, "onTodaySeconds": 4200, "timeStamp": "2025-04-20 10:50:00", "sensor_id": "sensor_8"},
        {"id": "wemo_009", "currentMilliWatts": 130, "onTodaySeconds": 2400, "timeStamp": "2025-04-20 10:55:00", "sensor_id": "sensor_9"},
        {"id": "wemo_010", "currentMilliWatts": 110, "onTodaySeconds": 1500, "timeStamp": "2025-04-20 11:00:00", "sensor_id": "sensor_10"},
    ],
    "wifiapobservation": [
        {"id": "wifi_001", "clientId": "client_01", "timeStamp": "2025-04-20 10:15:00", "sensor_id": "sensor_x"},
        {"id": "wifi_002", "clientId": "client_02", "timeStamp": "2025-04-20 10:20:00", "sensor_id": "sensor_y"},
        {"id": "wifi_003", "clientId": "client_03", "timeStamp": "2025-04-20 10:25:00", "sensor_id": "sensor_z"},
        {"id": "wifi_004", "clientId": "client_04", "timeStamp": "2025-04-20 10:30:00", "sensor_id": "sensor_a1"},
        {"id": "wifi_005", "clientId": "client_05", "timeStamp": "2025-04-20 10:35:00", "sensor_id": "sensor_b1"},
        {"id": "wifi_006", "clientId": "client_06", "timeStamp": "2025-04-20 10:40:00", "sensor_id": "sensor_c1"},
        {"id": "wifi_007", "clientId": "client_07", "timeStamp": "2025-04-20 10:45:00", "sensor_id": "sensor_d1"},
        {"id": "wifi_008", "clientId": "client_08", "timeStamp": "2025-04-20 10:50:00", "sensor_id": "sensor_e1"},
        {"id": "wifi_009", "clientId": "client_09", "timeStamp": "2025-04-20 10:55:00", "sensor_id": "sensor_f1"},
        {"id": "wifi_010", "clientId": "client_10", "timeStamp": "2025-04-20 11:00:00", "sensor_id": "sensor_g1"},
    ]
}

demo_tables = {
    "thermometerobservation": ("id", "temperature", "timestamp", "sensor_id"),
    "wemoobservation": ("id", "currentmilliwatts", "ontodayseconds", "timestamp", "sensor_id"),
    "wifiapobservation": ("id", "clientid", "timestamp", "sensor_id")
}


demo_create_tables = {
    "thermometerobservation":
        """CREATE TABLE IF NOT EXISTS ThermometerObservation (
          id varchar(255) NOT NULL,
          temperature integer DEFAULT NULL,
          timeStamp timestamp NOT NULL,
          sensor_id varchar(255) DEFAULT NULL,
          PRIMARY KEY (id)
        )""",
    "wemoobservation":
        """CREATE TABLE IF NOT EXISTS wemoobservation (
          id varchar(255) NOT NULL,
          currentMilliWatts integer DEFAULT NULL,
          onTodaySeconds integer DEFAULT NULL,
          timeStamp timestamp NOT NULL,
          sensor_id varchar(255) DEFAULT NULL,
          PRIMARY KEY (id)
        )""",
    "wifiapobservation":
        """CREATE TABLE IF NOT EXISTS WiFiAPObservation (
          id varchar(255) NOT NULL,
          clientId varchar(255) DEFAULT NULL,
          timeStamp timestamp NOT NULL,
          sensor_id varchar(255) DEFAULT NULL,
          PRIMARY KEY (id)
        )"""
}


if __name__ == "__main__":
    asyncio.run(main())
