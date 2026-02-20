use serde::{Deserialize, Serialize};
use serde_json::Result;
use std::collections::HashMap;
use std::fs;

#[derive(Serialize, Deserialize, Debug)]
pub struct Warehouse {
    id: String,
    location: [i64; 2],
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Agent {
    id: String,
    location: [i64; 2],
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Package {
    id: String,
    warehouse_id: String,
    destination: [i64; 2],
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Data {
    warehouses: Vec<Warehouse>,
    agents: Vec<Agent>,
    packages: Vec<Package>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Stat {
    packages_delivered: i64,
    total_distance: f64,
    efficiency: f64,
}

fn get_agent_stat(data: &Data) -> HashMap<String, Stat> {
    let mut stats = HashMap::new();

    for agent in &data.agents {
        stats.insert(
            agent.id.clone(),
            Stat {
                packages_delivered: 0,
                total_distance: 0.0,
                efficiency: 0.0,
            },
        );
    }
    stats
}

fn get_warehouse<'a>(data: &'a Data, ware_id: &'a str) -> Option<&'a Warehouse> {
    data.warehouses
        .iter()
        .find(|&warehouse| warehouse.id == ware_id)
        .map(|v| v as _)
}

fn calculate_distance(co_1: &[i64], co_2: &[i64]) -> f64 {
    let dx = (co_1[0] - co_2[0]) as f64;
    let dy = (co_1[1] - co_2[1]) as f64;

    (dx * dx + dy * dy).sqrt()
}

fn get_nearby_agents(location: &[i64; 2], data: &Data) -> Vec<(f64, String)> {
    let mut distances: Vec<(f64, String)> = data
        .agents
        .iter()
        .map(|agent| {
            let d = calculate_distance(location, &agent.location);
            (d, agent.id.clone())
        })
        .collect();

    distances.sort_by(|a, b| a.0.total_cmp(&b.0));

    distances
}

fn main() -> Result<()> {
    let content = fs::read_to_string("./base_case.json").expect("should have able to read file");

    let mut data: Data = serde_json::from_str(&content)?;

    let mut agent_stat = get_agent_stat(&data);

    let num_packages = data.packages.len();

    for (i, package) in data.packages.iter().enumerate() {
        if i == num_packages / 2 {
            let new_id = "A_New";
            println!(">> Event: {} joined the fleet at [50, 50]", new_id);
        }

        let warehouse = match get_warehouse(&data, &package.warehouse_id) {
            Some(w_l) => w_l,
            None => {
                println!(
                    "ERROR: Warehouse {} not found. Skipping package {}",
                    package.warehouse_id, package.id
                );
                continue;
            }
        };
        let near_by_agents = get_nearby_agents(&warehouse.location, &data);
        let (dist_btw_agent_and_w_house, agent_id) = &near_by_agents[0];
        let dist_btw_ware_house_to_des =
            calculate_distance(&warehouse.location, &package.destination);

        let total_trip_distance = dist_btw_agent_and_w_house + dist_btw_ware_house_to_des;

        agent_stat.entry(agent_id.to_string()).and_modify(|stat| {
            stat.total_distance += total_trip_distance;
            stat.packages_delivered += 1;
        });

        for agent in data.agents.iter_mut() {
            if agent.id == *agent_id {
                agent.location = package.destination;
            }
        }
    }

    let report = serde_json::to_string_pretty(&agent_stat)?;
    println!("================================================================");
    println!("================== REPORT ======================================");
    println!("{}", report);
    println!("================================================================");

    Ok(())
}
