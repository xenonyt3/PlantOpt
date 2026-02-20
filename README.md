# PlantOpt - CRAFT Facility Layout Optimizer

Welcome to the **PlantOpt** prototype! This is a Python-based Facility Layout Optimization tool that replicates and modernizes classic QS-style industrial layout software. It utilizes the CRAFT (Computerized Relative Allocation of Facilities Technique) heuristic to minimize material handling costs by iteratively swapping departments within a facility grid.

## 🌟 Features

- **CRAFT Heuristic Optimization**: Iteratively evaluates pairwise department swaps to find the lowest material handling cost layout.
- **Interactive Web Interface**: Built with Streamlit for an easy-to-use, responsive frontend.
- **Built-in Toy Problem**: Quickly test and understand the optimization process using a default dataset.
- **Custom CSV Uploads**: Upload your own Initial Layout and Flow/Cost matrices.
- **Real-time Visualization**: Visualizes the facility grid (heatmap) before and after optimization.
- **Cost History Tracking**: Plots the objective function value over optimization iterations.

## 🛠️ Technology Stack

- **Python 3.x**
- **Streamlit** - Web Interface
- **NumPy & Pandas** - Matrix computations and data manipulation
- **Matplotlib & Seaborn** - Grid visualizations and plotting

## 📂 Project Structure

```
PlantOpt/
│
├── main.py                     # Entry point to run the Streamlit app
├── ui/
│   └── app.py                  # Streamlit application and UI logic
├── core/
│   ├── craft.py                # CRAFT algorithm implementation
│   ├── layout_engine.py        # Grid operations (centroids, distances, swaps)
│   └── cost.py                 # Cost calculation logic
├── models/
│   └── department.py           # Data models (Department dataclass)
└── README.md                   # Project documentation
```

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed. Install the required dependencies using `pip`:

```bash
pip install streamlit numpy pandas matplotlib seaborn
```

### Running the Application

To launch the layout optimizer, simply run the `main.py` entry point from the root directory:

```bash
python main.py
```
This will automatically start the Streamlit server and open the application in your default web browser.

## 📈 How It Works

The workflow directly mimics QS-style facility layout software, allowing sequential design steps:

1. **Input Departments & Area**: Specify the total number of departments and assign an area footprint to each.
2. **Input From-To Matrix (Flow)**: Enter the frequency/flow of materials between defined departments within an NxN data matrix.
3. **Generate Initial Layout**: Create a grid (rows x cols) large enough to accommodate the total area. The layout can be auto-generated or manually filled by plotting departments onto the grid.
4. **Calculate Cost**: Given the initial layout and flows, calculate an initial material handling cost (Rectilinear Manhattan Distance × Flow).
5. **Run CRAFT Optimization**: The CRAFT algorithm iteratively evaluates all valid pairwise swaps (departments of equal area, or bordering neighbors), continuing until no valid swaps improve the overall cost.
6. **Results & Metrics**: Final grids are visualized via heatmaps, alongside cost improvement percentages and step-by-step iteration charts.
