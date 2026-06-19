# 🚀 Multi-Store Web Scraper Framework

An asynchronous, modular, and high-performance Command Line Interface (CLI) application built to track and parse products from e-commerce platforms using EANs (Barcodes). Powered by **Scrapling**'s high-stealth scraping capabilities and custom structured pipelines.

## 📂 Project Architecture

The system utilizes a **Vertical Slice Architecture**, isolating target-specific configurations, parsing logic, and execution wrappers into independent domain capsules.

- config/settings.py: Global paths, asset directory controls, and constants
- data/inputs/: Source lists for EAN inventory files
- data/output/: Normalized JSON extraction results
- targets/amazon/models.py: Object data schemas (Dataclasses)
- targets/amazon/parser.py: DOM CSS/XPath extraction fallbacks
- targets/amazon/worker.py: Core asynchronous worker pipeline
- utils/file_handler.py: Core data pipelines (CSV reader/JSON parser)
- utils/logger.py: Custom double-output ANSI colored logging
- main.py: App Entrypoint / Unified CLI Router

---

## 🛠️ Features

* **Dual Execution Modes:** Seamlessly toggle between parsing a complete batch file (.csv) or targeting a single, specific EAN directly via terminal flags.
* **Vertical Capsule Design:** Zero platform-logic contamination. Changing selectors for a store happens strictly within its dedicated folder.
* **Adaptive DOM Auto-Healing:** Leverages advanced parsing hooks to resist platform layout and class changes.
* **Advanced Semaphore Rate Limiting:** Built-in safeguards to orchestrate asynchronous batch tasks smoothly without triggering server-side IP blocks.
* **Structured Color Logs:** Dual-output tracking engine that logs clean text to file systems while outputting vibrant ANSI-colored status updates to developer terminals.

---

## 🚀 Getting Started

### 1. Prerequisites & Installation

Clone the repository to your environment, spin up a clean virtual environment, and install dependencies:

# Initialize and activate virtual environment
python -m venv venv
# On Windows use: .\venv\Scripts\activate
source venv/bin/activate  

# Install dependencies
pip install scrapling

### 2. Configure Your Source File
Ensure your default tracking source exists inside the path declared by your configuration workspace (e.g., data/eans.csv). The file must include an ean header layout:

---

## 🕹️ Usage Instructions

The platform runs as a unified CLI router. You choose your targeted marketplace engine as a positional argument followed by configuration modifiers.

### 📋 Mode A: Standard File Batch Mode
Executes the scraping loops concurrently through every line found inside your target .csv database file:

python main.py amazon

#### Adjusting Concurrency Controls
Scale or throttle the network processing capability directly based on your local machine and proxy limits:
python main.py amazon --concurrency 10

#### Passing an Alternative File Path
Override the default configured CSV input source file to stream custom target listings:
python main.py amazon --input data/holiday_deals.csv

### 🎯 Mode B: Single EAN Inspection Mode
Bypasses file system readers entirely to parse and debug a single product line instantly on the fly:

python main.py amazon --ean 7891172523915

---

## 🎨 Log Tracking and Output Pipelines

* **Terminal Log Outputs:** Colored automatically using safety standards. General system operations appear in Green, file validation and persistence notifications trigger Magenta, and handled exceptions highlight in Red.
* **Saved Artifacts:** Extraction pipelines structure clean data schemas inside data/output/amazon_results.json upon completion.
