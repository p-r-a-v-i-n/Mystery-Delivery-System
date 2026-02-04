import json
import random
import csv
import os

# Toggle this if you want to see the ASCII map visualization
SHOW_MAP = False

def get_json_data(path):
    """Reads a JSON file and returns its contents."""
    try:
        f = open(path, "r")
        return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No such file - {path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse JSON from {path}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while reading {path}: {str(e)}")
        return None


def clean(json_data):
    """Converts lists of warehouses and agents to dictionaries."""
    if isinstance(json_data["warehouses"], list):
        json_data["warehouses"] = {w["id"]: w["location"] for w in json_data["warehouses"]}
    
    if isinstance(json_data["agents"], list):
        json_data["agents"] = {a["id"]: a["location"] for a in json_data["agents"]}
    return json_data

def calculate_distance(coordinate_1, coordinate_2):
    """Calculates Euclidean distance between two 2D points."""
    return ((coordinate_1[0] - coordinate_2[0])**2 + (coordinate_1[1] - coordinate_2[1])**2)**0.5


def get_nearby_agents(location, data):
    """Finds all nearest agents and sorts them by distance"""
    distances = []
    for agent_id, agent_loc in data["agents"].items():
        d = calculate_distance(location, agent_loc)
        distances.append((d, agent_id))
    return sorted(distances)

def get_agent_stat(data):
    """Initialize agent stats."""
    stats = {
        agent_id: {
            "packages_delivered": 0, 
            "total_distance": 0.0,
            "efficiency": 0.0
        } 
        for agent_id in data["agents"].keys()
    }
    return stats

def get_warehouse(data, warehouse_id):
    """Retrieves the location of a warehouse by its ID."""
    return data["warehouses"].get(warehouse_id)

def update_agent_distance(data, agent_id, new_location):
    """Update agent location."""
    if agent_id in data["agents"]:
        data["agents"][agent_id] = list(new_location)

def visualize_map(data, width=50, height=25):
    """Generates a visual representation of the map."""
    MAX_COORD = 110
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    scale_x = width / MAX_COORD
    scale_y = height / MAX_COORD

    def to_grid(x, y):
        gx = int(x * scale_x)
        gy = int(y * scale_y)
        return min(gx, width-1), min(gy, height-1)

    for pkg in data["packages"]:
        gx, gy = to_grid(pkg["destination"][0], pkg["destination"][1])
        grid[gy][gx] = 'p'

    for loc in data["warehouses"].values():
        gx, gy = to_grid(loc[0], loc[1])
        grid[gy][gx] = 'W'

    for loc in data["agents"].values():
        gx, gy = to_grid(loc[0], loc[1])
        if grid[gy][gx] == ' ':
            grid[gy][gx] = 'A'
        else:
            grid[gy][gx] = '*'

    print("\n[Map View: W=Warehouse, A=Agent, p=Package, *=Overlap]")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")

def save_top_agent_csv(agent_id, stats, report_name, filename="top_performers.csv"):
    """Save top agent stats to CSV."""
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Report", "Agent ID", "Packages Delivered", "Total Distance", "Efficiency"])
        writer.writerow([report_name, agent_id, stats["packages_delivered"], stats["total_distance"], stats["efficiency"]])

def generate_report(data, report_name="Unknown"):
    """Generate report for a test case."""
    agent_stat = get_agent_stat(data)
    packages = data["packages"]
    num_packages = len(packages)

    print(f"\n{'='*50}")
    print(f"Report for: {report_name}")
    print(f"{'='*50}")

    for i, package in enumerate(packages):
        # Bonus: Simulating mid-day agent join (at 50% progress)
        if i == num_packages // 2:
            new_id = "A_New"
            print(f">> EVENT: {new_id} joined the fleet at [50, 50]")
            data["agents"][new_id] = [50, 50]
            agent_stat[new_id] = {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0}

        w_id = package.get("warehouse_id") or package.get("warehouse")
        w_loc = get_warehouse(data, w_id)
        if w_loc is None:
             print(f"Error: Warehouse {w_id} not found. Skipping package {package['id']}")
             continue
        
        near_by_agents = get_nearby_agents(w_loc, data)

        dist_btw_agent_and_w_house, agent_id = near_by_agents[0]
        dist_btw_ware_house_to_des = calculate_distance(w_loc, package["destination"])


        delay_factor = random.uniform(1.0, 1.2) # Random Delivery Delay (0% to 20% extra distance/time)
        total_trip_distance = (dist_btw_agent_and_w_house + dist_btw_ware_house_to_des) * delay_factor

        agent_stat[agent_id]["total_distance"] += total_trip_distance
        agent_stat[agent_id]["packages_delivered"] += 1

        update_agent_distance(data, agent_id, package["destination"])

    best_agent = None
    min_eff = float('inf')
    for a_id, stat in agent_stat.items():
        if stat["packages_delivered"] > 0:
            raw_eff = stat["total_distance"] / stat["packages_delivered"]
            stat["efficiency"] = round(raw_eff, 2)
            stat["total_distance"] = round(stat["total_distance"], 2)
            if raw_eff < min_eff:
                min_eff = raw_eff
                best_agent = a_id
            
    agent_stat["best_agent"] = best_agent
    print(json.dumps(agent_stat, indent=4))
    
    os.makedirs("reports", exist_ok=True)
    filename_clean = os.path.basename(report_name).replace(".json", "")
    output_filename = f"reports/report_{filename_clean}.json" if report_name != "Unknown" else "reports/report.json"
    
    try:
        with open(output_filename, "w") as f:
            json.dump(agent_stat, f, indent=4)
        print(f"Report saved: {output_filename}")
    except Exception as e:
        print(f"Logging error: {e}")

    if best_agent:
        save_top_agent_csv(best_agent, agent_stat[best_agent], report_name)
    
    if SHOW_MAP:
        visualize_map(data)

    return agent_stat

def generate_multiple_reports():
    """Iterates through predefined test files and generates individual reports."""
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
        "test_cases/test_case_10.json"
    ]
    
    overall_stats = {}
    
    for path in file_paths:
        raw_data = get_json_data(path)
        if raw_data:
            clean_data = clean(raw_data)
            case_stats = generate_report(clean_data, report_name=path)
            
            for agent_id, stats in case_stats.items():
                if agent_id == "best_agent":
                    continue
                if agent_id not in overall_stats:
                    overall_stats[agent_id] = {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0}
                
                overall_stats[agent_id]["packages_delivered"] += stats["packages_delivered"]
                overall_stats[agent_id]["total_distance"] += stats["total_distance"]

    global_best_agent = None
    min_avg_dist = float('inf')
    
    for agent_id, stats in overall_stats.items():
        if stats["packages_delivered"] > 0:
            avg_dist = stats["total_distance"] / stats["packages_delivered"]
            stats["efficiency"] = round(avg_dist, 2)
            stats["total_distance"] = round(stats["total_distance"], 2)
            
            if avg_dist < min_avg_dist:
                min_avg_dist = avg_dist
                global_best_agent = agent_id

    overall_stats["best_agent"] = global_best_agent

    print(f"\n{'='*50}")
    print("GLOBAL OVERALL PERFORMANCE REPORT")
    print(f"{'='*50}")
    print(json.dumps(overall_stats, indent=4))
    
    try:
        with open("report.json", "w") as f:
            json.dump(overall_stats, f, indent=4)
        print("\nOverall global report saved to report.json")
    except Exception as e:
        print(f"Error saving global report: {e}")

if __name__ == "__main__":
    generate_multiple_reports()
