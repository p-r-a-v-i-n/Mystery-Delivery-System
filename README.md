# Mystery Delivery System (FastBox Simulator)

### How it works:
- **Normalization**: Some of the test data uses lists for warehouses/agents while others use dictionaries. The script "cleans" this data on the fly to keep the logic consistent.
- **Closest Agent Logic**: Before a package is picked up, the script finds the agent currently closest to that package's warehouse using Euclidean distance.
- **Dynamic Movement**: After a delivery, the agent stays at the destination coordinate and is ready for their next assignment from that new position.
- **Reporting**: For every run, it calculates total distance, packages delivered, and a "cost-per-delivery" efficiency metric.

## Key Decisions & Assumptions

Since some scenarios weren't explicitly covered in the prompt, I made the following engineering decisions:
1. **Efficiency Calculation**: I interpreted "efficiency" as `Total Distance / Packages Delivered`. This tells us the average distance (cost) incurred for each successful delivery. A lower number here is better.
2. **Post-Delivery Positioning**: Once an agent delivers a package, they wait at the destination point. I figured this was more logical than them driving all the way back to a home base for no reason.
3. **Tie-breaking**: If two agents are exactly the same distance from a warehouse, the script picks the one that appears first in the dataset.
4. **Mid-day Hires**: For the bonus task, I implemented a "mid-day join" event. Exactly halfway through the package list, a new agent (`A_NEW`) is added to the pool to help out.

## Bonus Features Included
- **Random Delays**: Real traffic is unpredictable. I added a `random` factor that simulates delays by increasing the calculated distance of a trip by up to 20%.
- **ASCII Map**: There's a rough visualizer that shows where everyone is on a 100x100 grid. You can toggle this off in the code using the `SHOW_MAP` variable.
- **CSV Export**: The top performer from every test case is logged into `top_performers.csv` for overtime tracking.

## Running the Code
Simply run:
```bash
python3 main.py
```
Reports for each individual test case are saved in the `reports/` folder. A final, aggregated report summarizing the performance of all agents across all test cases is saved as `report.json` in the project root.
