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

def clean(json_data):
    if isinstance(json_data["warehouses"], list):
        json_data["warehouses"] = {w["id"]: w["location"] for w in json_data["warehouses"]}
    
    if isinstance(json_data["agents"], list):
        json_data["agents"] = {a["id"]: a["location"] for a in json_data["agents"]}
    return json_data

def calculate_distance(coordinate_1, coordinate_2):
    return ((coordinate_1[0] - coordinate_2[0])**2 + (coordinate_1[1] - coordinate_2[1])**2)**0.5


def get_nearby_agents(location, data):
    distances = []
    for id, loc in data["agents"].items():
        d = calculate_distance(location, loc)
        distances.append((d, id))
    return sorted(distances)

def get_agent_stat(data):
    stats = {
        id: {
            "packages_delivered": 0, 
            "total_distance": 0.0,
            "efficiency": 0.0
        } 
        for id in data["agents"].keys()
    }
    return stats


def get_warehouse(data, id):
    for _id in data["warehouses"].keys():
        if _id == id:
            return data["warehouses"][_id]
    return None

def update_agent_distance(data, id, new_location):
    for _id, agent in data["agents"].items():
        if _id == id:
            data["agents"][_id] = list(new_location)
        


file_paths = [
    "base_case.json",
    "test_cases/test_case_1.json",
    "test_cases/test_case_2.json",
    "test_cases/test_case_3.json",
    "test_cases/test_case_4.json",
    "test_cases/test_case_5.json",
    "test_cases/test_case_6.json",
    "test_cases/test_case_7.json",
    "test_cases/test_case_8.json",
    "test_cases/test_case_9.json",
    "test_cases/test_case_10.json",

]


def generate_report(data):
    agent_stat = get_agent_stat(data)
    for package in data["packages"]:
        w_id = package.get("warehouse_id") or package.get("warehouse")
        w_house = get_warehouse(data, w_id)
        if w_house is None:
             print(f"Error: Warehouse {w_id} not found.")
             continue
        near_by_agents = get_nearby_agents(w_house, data)
        nearest_agent = near_by_agents[0]

        agent_id = nearest_agent[1]

        dist_btw_agent_and_w_house = nearest_agent[0]
        dist_btw_ware_house_to_des = calculate_distance(w_house, package["destination"])

        total_trip_distance = dist_btw_agent_and_w_house + dist_btw_ware_house_to_des

        agent_stat[agent_id]["total_distance"] += total_trip_distance
        agent_stat[agent_id]["packages_delivered"] += 1

        update_agent_distance(data, agent_id, package["destination"])

    best_agent = None
    min_eff = float('inf')
    for agent_id in agent_stat:
        stat = agent_stat[agent_id] 
        
        if stat["packages_delivered"] > 0:
            raw_eff = stat["total_distance"] / stat["packages_delivered"]
            
            stat["efficiency"] = float(f"{raw_eff:.2f}")
            stat["total_distance"] = float(f"{stat['total_distance']:.2f}")
            if raw_eff < min_eff:
                min_eff = raw_eff
                best_agent = agent_id
            
    
    print(f"Best Agent: {best_agent}")
    print(json.dumps(agent_stat, indent=4))




def generate_multiple_reports():
    for file_path in file_paths:
        print(f"\n{'='*50}")
        print(f"Report for: {file_path}")
        print(f"{'='*50}")
        data = get_json_data(file_path)
        if data is None:
            continue
        clean_data = clean(data)
        generate_report(clean_data)

generate_multiple_reports()
