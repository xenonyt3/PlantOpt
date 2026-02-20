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

1. **Initialization**: The application takes an initial grid layout and a flow/cost matrix between departments.
2. **Evaluation**: It calculates the centroids of each department and computes the total material handling cost based on rectilinear (Manhattan) distances.
3. **Iterative Swapping**: The CRAFT algorithm evaluates all valid pairwise swaps (departments that are adjacent or share the same area).
4. **Optimization**: If a swap reduces the total cost, it becomes the new layout. This process repeats until no further cost reductions can be found or the maximum iteration limit is reached.
5. **Results**: The cost reductions, iteration history, and the final optimized layout are displayed in the UI.
