from datasets import load_dataset, DatasetDict

# Save path
save_path = "datasets"

# Load and save the agentic split
agentic_ds = load_dataset("nvidia/cvdp-benchmark-dataset", "cvdp_agentic_code_generation")
agentic_ds.save_to_disk(f"{save_path}/cvdp_agentic_code_generation")

# Load and save the non-agentic split
nonagentic_ds = load_dataset("nvidia/cvdp-benchmark-dataset", "cvdp_nonagentic_code_generation")
nonagentic_ds.save_to_disk(f"{save_path}/cvdp_nonagentic_code_generation")

print("Datasets saved successfully!")
