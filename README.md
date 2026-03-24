# Stable Matching Simulator

A visual, interactive educational tool for exploring the **Gale-Shapley stable matching algorithm**. This simulator demonstrates how mutual preferences influence final outcomes while ensuring stability and fairness in matching scenarios.

## Overview

The Stable Matching Problem is a classic algorithmic challenge in economics, computer science and operations research. Given two groups (e.g. residents and hospitals) where each member has a ranked preference list, the goal is to find a stable matching where no pair would mutually prefer to abandon their current matches.

This simulator provides:
- **Interactive GUI** for defining preferences and running simulations
- **Two matching modes**: Manual (explicit preferences) and Auto (criteria-based)
- **Real-time algorithm visualization** with step-by-step event logging
- **Comprehensive metrics** including stability verification and preference satisfaction
- **Unmatched analysis** explaining why residents didn't match
- **Dataset import/export** for reproducible studies
- **Runtime performance analysis** tools

## Features

### Core Algorithm
- **Gale-Shapley Implementation**: Industry-standard stable matching algorithm
- **Resident-Proposing Variant**: Residents make proposals; hospitals accept/reject
- **Resident Stability**: No unmatched resident-hospital pair would both prefer each other

### Matching Modes

#### Manual Mode
- Explicitly define preferences for both groups
- Hospitals and residents rank each other directly
- Full control over all preference lists

#### Auto Mode
- Hospitals rank residents automatically based on criteria:
  - **GPA sorting**: Prefer residents with higher GPAs
  - **Degree filtering**: Accept only specific degree types (Undergraduate, Postgraduate, or All)
- Residents still specify their hospital preferences manually
- Simulates realistic matching scenarios (e.g. hospital hiring)

### User Interface
- **Hospitals View**: Define capacity, preferences (manual mode), or criteria (auto mode)
- **Residents View**: Enter GPA, degree, and hospital preferences
- **Output View**: Display matching results, statistics, algorithm events, and explanations
- **D3 Visualization**: Interactive timeline visualization of the algorithm's proposal flow

### Analytics & Insights
- **Matching Statistics**:
  - Unmatched rate and count
  - Average preference rank satisfaction (residents & hospitals)
  - First choice rate
  - Blocking pair detection
  - Total proposals made
  - Proposal distribution

- **Unmatched Resident Explanations**:
  - Why they didn't match (ineligible, blocked by capacity, ranking issues)
  - Closest competitive hospitals
  - GPA/ranking gap analysis

### Dataset Management
- **Generate**: Create random test datasets with custom sizes
- **Import**: Load JSON datasets into the simulator
- **Export**: Save current simulation setup as JSON
- **Test Datasets**: Pre-made datasets ranging from 25-150 residents

### Performance Analysis
- **Runtime Study**: Measure algorithm performance across different problem sizes
- **Proposal Counting**: Track algorithmic efficiency
- **CSV Results**: Export performance metrics
- **Visualization**: Generate runtime growth graphs

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup

1. **Clone/Download the repository**
   ```bash
   git clone <https://github.com/sulwync/Stable-Matching-Simulator>
   cd Stable-Matching-Simulator
   ```

2. **Install dependencies**
   ```bash
   pip install matplotlib pywebview
   ```

   **Dependencies explanation:**
   - `matplotlib`: Required for performance analysis graphs 
   - `pywebview`: Required for interactive D3.js visualization of algorithm steps

3. **Verify installation**
   ```bash
   python -m pip list | grep matplotlib
   ```

## Usage

### Running the Simulator

```bash
cd src
python -m gui.simulator
```

This launches the interactive GUI application.

### GUI Walkthrough

#### 1. Set Up Hospitals (Left Panel)
- **Number of Hospitals**: Define how many hospitals participate
- **Mode Selection**: Choose "Manual" or "Auto"
- **Capacity**: How many residents each hospital can accept
- **Manual Mode**: List resident preferences (comma or space-separated)
- **Auto Mode**: Select preferred degree type

#### 2. Set Up Residents (Middle Panel)
- **Number of Residents**: Define how many residents participate
- **GPA** (Auto mode only): 0.0 - 4.0 scale
- **Degree** (Auto mode only): Undergraduate or Postgraduate
- **Hospital Preferences**: List hospitals in preference order

#### 3. Run Simulation
- Click **"Run Simulation"** to execute the Gale-Shapley algorithm
- Results appear in the Output View (Right Panel)

#### 4. View Results (Right Panel)
- **Matching Results**: Resident → Hospital assignments
- **Statistics**: Comprehensive metrics
- **Event Log**: Step-by-step algorithm trace
- **Explanations**: Why unmatched residents didn't match
- **Visualize**: Interactive D3 timeline of proposals

### Command-Line Tools

#### Generate Random Datasets
```bash
cd src
python generate_dataset.py --mode auto --hospitals 10 --residents 50 --output my_dataset.json
```

Options:
- `--mode`: `manual` or `auto` (default: manual)
- `--hospitals`: Number of hospitals (default: 5)
- `--residents`: Number of residents (default: 10)
- `--output`: Output file path
- `--seed`: Random seed for reproducibility

#### Run Performance Analysis
```bash
cd src
python runtime_study.py --mode auto --start 50 --stop 500 --step 50 --repeats 3
```

Options:
- `--mode`: `manual` or `auto`
- `--start`, `--stop`, `--step`: Range of problem sizes
- `--hospital-ratio`: Ratio of hospitals to residents (default: 0.5)
- `--repeats`: Number of trials per size (default: 3)
- `--seed`: Random seed
- Outputs: CSV results and performance graphs

## Project Structure

```
Stable-Matching-Simulator/
├── README.md                          # This file
├── src/
│   ├── core/                          # Core algorithm 
│   │   ├── explain_unmatched.py       # Analysis of unmatched 
│   │   ├── gale_shapley.py            # Gale-Shapley stable 
│   │   ├── metrics.py                 # Statistics and metrics 
│   │   └── types.py                   # Type definitions
│   │
│   ├── dataset/                       # Pre-made test datasets
│   │   ├── manual_25H_50R_trial*.json
│   │   ├── manual_50H_100R_trial*.json
│   │   ├── ... (more sizes)
│   │   ├── manual_150H_300R_trial*.json
│   │
│   ├── gui/                           # GUI components
│   │   ├── views/                     # UI component views
│   │   │   ├── hospitals_view.py      # Hospitals input panel
│   │   │   ├── residents_view.py      # Residents input panel
│   │   │   └── output_view.py         # Results display panel
│   │   ├── widgets/                   # Custom UI widgets
│   │   │   ├── placeholder_entry.py   # Entry with placeholder
│   │   │   └── scrollframe.py         # Scrollable frame widget
│   │   ├── controller.py              # Application logic 
│   │   ├── d3_viewer.py               # D3.js visualization 
│   │   └── simulator.py               # Main application window
│   │
│   ├── results/                       # Runtime study outputs
│   │   └── proposal_graph.png
│   │   └── runtime_graph.png
│   │   └── runtime_study.csv
│   │
│   ├── dataset_test.json              # Example test dataset
│   ├── generate_dataset.py            # Dataset generation 
│   └── runtime_study.py               # Performance analysis 
```

## Core Components

### Gale-Shapley Algorithm (`core/gale_shapley.py`)

**Main Functions:**
- `stableMatch(resPref, hosPref, capacity)`: Execute algorithm with explicit preferences
- `stableMatchWithConst(resPref, resInfo, hosCriteria, capacity)`: Execute with auto-generated preferences
- `generateHosPref(resInfo, hosCriteria)`: Generate hospital preferences from criteria
- `buildRank(hosPref)`: Create ranking lookup tables

**Algorithm Steps:**
1. Initialize free queue with all residents
2. While a resident is free:
   - Propose to next hospital in preference list
   - Hospital accepts if capacity available
   - If over capacity, hospital rejects worst-ranked resident
   - Rejected resident returns to queue to propose to next choice

**Time Complexity:** O(n²) where n = total agents

### Metrics (`core/metrics.py`)

Calculates:
- **Unmatched Rate**: Proportion of unmatched residents
- **Preference Satisfaction**: Average rank of assigned partner in preference list
- **First Choice Rate**: % of residents matched to first-choice hospital
- **Blocking Pairs**: Pairs that could both prefer each other (stability check)
- **Proposal Count**: Total proposals made by algorithm

### Unmatched Analysis (`core/explain_unmatched.py`)

For each unmatched resident, provides:
- **Ineligible Hospitals**: Blocked by criteria (auto mode) or not ranked (manual)
- **Eligible/Ranked Hospitals**: Hospitals that ranked them
- **Closest Miss**: Hospital they almost matched with and GPA/rank gap
- **Blocked Hospitals**: Hospitals where they were outranked

## Dataset Format

Datasets are JSON files with the following structure:

### Manual Mode
```json
{
  "mode": "manual",
  "hospitals": [
    {
      "capacity": 2,
      "manual_pref_str": "R1 R3 R5"
    }
  ],
  "residents": [
    {
      "pref_str": "H1 H2 H3"
    }
  ]
}
```

### Auto Mode
```json
{
  "mode": "auto",
  "hospitals": [
    {
      "capacity": 2,
      "pref_deg_str": "Postgraduate"
    }
  ],
  "residents": [
    {
      "gpa_str": "3.8",
      "deg_str": "Postgraduate",
      "pref_str": "H1 H2 H3"
    }
  ]
}
```

## Example Workflow

### Manual Mode Example

1. Define hospital capacities, resident preferences and hospital preferences
2. Click "Run Simulation"
3. View matching results and statistics
4. Click "Visualize" for interactive proposal timeline

### Auto Mode Example

1. Select "Auto" mode
2. Define hospital capacities and degree preferences
3. Enter resident GPA (0.0-4.0), degree type and hospital preferences for each resident
4. Click **"Run Simulation"**
5. Hospital preferences are automatically generated based on GPA/degree criteria
6. View matching results and statistics
7. Click "Visualize" for interactive proposal timeline

**Optional: Generate Large Test Datasets**
For testing larger scenarios (rather than manual entry), use the dataset generator:
```bash
python generate_dataset.py --mode auto --hospitals 10 --residents 50 --output test_dataset.json
```
Then import the generated dataset via "Import Dataset" button.

## Algorithm Guarantees

The Gale-Shapley algorithm guarantees:

**Stability**: No unmatched pair would mutually prefer each other  
**Termination**: Algorithm always completes in finite time  
**Resident Optimality**: Each resident gets the best match possible in any stable matching  
**Hospital Pessimality**: Each hospital gets the worst match possible in any stable matching

## Performance

Runtime analysis results (see `results/runtime_study.csv`):

- **Algorithm Complexity**: O(n²) proposals in worst case
- **Typical Performance**: Linear to quadratic growth depending on preference distributions

## References

- D. Gale and L. S. Shapley, “College Admissions and the Stability of Marriage,” The American Mathematical Monthly, vol. 69, no. 1, pp. 9–15, 1962.
- Gusfield, D., & Irving, R. W. The stable marriage problem: structure and algorithms. Cambridge, Massachusetts: The MIT Press, 1989.  
- Educational resource: https://www.jstor.org/stable/2312726  

## Changelog

- **v1.0** (Initial Release)
  - Core Gale-Shapley algorithm implementation
  - Manual and Auto matching modes
  - GUI simulator with three-panel layout
  - Comprehensive metrics and analysis
  - D3 visualization support
  - Runtime performance analysis tools 
