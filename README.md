

# WAVELLM

Digital Simulation Waveform Verification Agent

## 1. Prerequisites & Initial Setup

Before you begin, ensure you have the necessary tools like Docker and Python3.12 installed.

### Environment Configuration

First, configure your shell environment and API keys.

1.  **Source the setup script** to load required environment variables:
    ```bash
    source env_setup.sh
    ```
2.  **Export your DeepSeek API key:**
    ```bash
    export DEEPSEEK_API_KEY="YOUR_API_KEY_HERE"
    export OPEN_AI_KEY='YOUR_API_KEY_HERE'
    ```

### Install OSS CAD Suite (with Yosys)

1.  **Download** the latest pre-compiled suite from the [official releases page](https://github.com/YosysHQ/oss-cad-suite-build/releases).
2.  **Extract** the downloaded archive.
3.  **Add the suite's `bin` directory to your system's PATH**. Make sure to adjust the relative path (`../oss-cad-suite`) to match the location where you extracted the files.
    ```bash
    # Example:
    export PATH=/path/to/your/oss-cad-suite/bin:$PATH
    ```

---

## ? 2. Analysis & Synthesis Workflow

This section covers the core steps for parsing design files and running synthesis.

### Start Local Services

1.  **Run the local embedding model** using Ollama. This is required for the RAG agent.
    ```bash
    ollama run nomic-embed-text
    ```

### Parse VCD and Run RAG Agent

Based on your saved information, this step likely involves parsing a Value Change Dump (VCD) file to be used with a Retrieval-Augmented Generation (RAG) agent.

1.  Execute the parsing script:
    ```bash
    python parseVCD.py
    ```

### Run Synthesis with Yosys

1.  **Synthesize the logic cone** using the provided Yosys script. This will generate a `.dot` file representing the design hierarchy.
    ```bash
    yosys -i synthesis/logic_cone.ys
    ```
2.  **Convert the DOT file to JSON** for easier processing in subsequent steps.
    ```bash
    python synthesis/dot_to_json.py hiearchy_view.dot
    ```

### Neo4j Database Setup

*(This section is a placeholder. Please add the specific commands for setting up and populating the Neo4j graph database.)*

```bash
```
# Run Docker

```bash
sudo docker system prune -af
docker images
docker run -it xxxxxxx
```

## Run cadence docker

```bash
cd cvdp_benchmark/examples/cadence_docker
tar -czf XCELIUM2309.tgz -C /home/tools/cadence/installs/XCELIUM2309 .
tar -czf VMANAGER2309.tgz -C /home/tools/cadence/installs/VMANAGER2309 . 
docker build -t cvdp-cadence-verif:latest .
```

## Run benchmark

```bash
python tools/dataset_subset_creator.py cvdp-benchmark-dataset/cvdp_v1.0_nonagentic_code_generation.jsonl cvdp_cid16_dataset.jsonl --only-cid 16 --add-reports --add-outputs
python3.12 run_benchmark.py -f cvdp_cid16_dataset.jsonl -l -m gpt-4o-mini
```

