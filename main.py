import json

def get_json_data(path):
    try:
        f = open(path, "r")
    except FileNotFoundError as e:
        print("ERROR: File not found " + path)
    else:
        raw_data = f.read()
        json_data = json.loads(raw_data)
        return json_data


def get_nearby_agents(location):
    x1, y1 = location
    distances = []
    for agent in data["agents"]:
        x2, y2 = agent["location"]
        d = (((x2 - x1)**2) + ((y2 - y1)**2))**0.5
        distances.append((d, agent["id"]))
    return sorted(distances)


file_path = "base_case.json"
data = get_json_data(file_path)

sheet = {}
for warehouse in data["warehouses"]:
    if warehouse["id"] not in sheet:
        sheet[warehouse["id"]] = {"agents": get_nearby_agents(warehouse["location"]), "location": warehouse["location"]}
    else:
        sheet[warehouse["id"]]["agents"] = get_nearby_agents(warehouse["location"])
        sheet[warehouse["id"]]["location"] = warehouse["location"]

report = {}
from collections import defaultdict
r = defaultdict(list)
for package in data["packages"]:
    agent1 = sheet[package["warehouse_id"]]["agents"][0]
    
    x1, y1 = sheet[warehouse["id"]]["location"]
    
    x2, y2 = package["destination"]
    d = (((x2 - x1)**2) + ((y2 - y1)**2))**0.5
    print(f"FOR {package["warehouse_id"]} - distance {d}  (x1, y1): {x1, y1}, (x2,y2): {x2,y2}")
    if agent1[1] not in r:
        agent_report = {
            "total_distance": d,
            "packages_delivered": 1
        }
        r[agent1[1]] = agent_report
    else:
        r[agent1[1]]["total_distance"] += d
        r[agent1[1]]["packages_delivered"] += 1

print(r) # i'm in the middle of generating report

