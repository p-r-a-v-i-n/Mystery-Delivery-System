### Mystery Delivery System (FastBox Simulator)

This project is a small simulator for FastBox company. It calculates how agents move to deliver packages and shows a report at the end.

#### Main Points:
- **Cleaning Data**: Some files use lists and some use dictionaries. I convert everything to dictionaries so it is easy to read.
- **Finding Agent**: For each package, the code finds which agent is closest to the warehouse.
- **Agent Moving**: After a delivery, the agent stays at that location. They wait there for the next job.
- **Reports**: It calculates total distance and how many packages each agent delivered.

#### Decisions & Assumptions
1. **Efficiency**: I use `Distance / number of packages`. A smaller number means the agent is better because they traveled less for each package.
2. **Routing order**: Agents stay at the delivery location. They don't go back to the start point every time as it is more efficient.
3. **Tie-break**: If two agents have the same distance, the one that comes first in the list is picked.
4. **New Agent**: Halfway through the work, a new agent named `A_New` joins the fleet to help.

#### Features (Bonus)
- **Traffic Delays**: I added 0-20% random extra distance to simulate traffic.
- **Map Drawing**: There is a small ASCII map to see locations. You can turn this off with `SHOW_MAP = False` in `main.py`.
- **Top Performer**: The best agent from each run is saved in `top_performers.csv`.

#### How to Run
Run this command in terminal:
```bash
python3 main.py
```
- Individual reports for each file are in the `reports/` folder.
- The final overall report is saved in the root `report.json`.
