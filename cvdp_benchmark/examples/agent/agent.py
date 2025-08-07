#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Simple CVDP agent implementation for the agentic workflow.
This agent reads prompt.json and makes changes to files in the mounted directories.
"""

import os
import json
import sys
import glob
import time
from openai import OpenAI
import re
import subprocess
import logging

base_path = '/code'
MODEL_NAME = "deepseek-reasoner"
API_KEY = "sk-api-key"
MAX_ITR = 3 

# Setup logging for agent
log_path = f"{base_path}/rundir/agent.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)

greet = f""" You are an AI software agent for chip design automation.
When asking a question, you can only answer in the provided JSON format (must be a valid JSON string): 
{{
    "action": "writeFile",
    "filePath": "The path of the file you want to overwrite"
    "content": "//The code or content that needs to be write to the file",
    "note": "Any other things you want to say or explain"
}}
"""

def run_pytest():
    print("Running pytest")
    logging.info("=============== RUNNING PYTEST ============")
    cmd = "pytest /src/process.py -v -s"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Pytest return with errorCode {result.returncode}")
    logging.info(f"pytest result: {result}")
    return result.returncode, result.stdout, result.stderr

 # Extract lines containing 'ERROR' or '*E' or 'assertion'
def extract_error_messages(output):
    error_lines = []
    for line in output.splitlines():
        if "ERROR" in line or "*E" in line or "assert" in line.lower():
            error_lines.append(line)
    return "\n".join(error_lines)

def update_prompt_with_error(base_prompt, error_msg):
    logging.info("=========== [UPDATE PROMPT] ============")
    print("Updating prompt")
    enhanced_prompt = base_prompt + "\n\nThe simulation test failed with the following errors:\n"
    enhanced_prompt += error_msg
    enhanced_prompt += "\nPlease fix the testbench accordingly and provide the updated SystemVerilog code."
    return enhanced_prompt

def extractJson(text):
    pattern = r"```(?:\w+\n)?(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def deepseek(prompt):
    print('Waiting for answer from Deepseek...\n')
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": greet},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    logging.info("============= RESPONSE ====================")
    logging.info(response.choices[0].message.content)
    text = extractJson(response.choices[0].message.content)
    logging.info('==============Extracted JSON ===================')
    logging.info(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        logging.error(f'Invalid JSON: {e}')
        return

def read_prompt():
    """Read the prompt from prompt.json"""
    try:
        with open(f"{base_path}/prompt.json", "r") as f:
            prompt_data = json.load(f)
            return prompt_data.get("prompt", "")
    except Exception as e:
        print(f"Error reading prompt.json: {e}")
        logging.error(f"Error reading prompt.json: {e}")
        return ""

def list_directory_files(dir_path):
    """List all files in a directory recursively"""
    files = []
    if os.path.exists(dir_path):
        for root, _, filenames in os.walk(dir_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, dir_path)
                files.append(rel_path)
    return files

def read_file(file_path):
    """Read the contents of a file"""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        logging.error(f"Error reading file {file_path}: {e}")
        return ""

def write_file(file_path, content):
    """Write content to a file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
        logging.info(f"Successfully wrote to {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        logging.error(f"Error writing to file {file_path}: {e}")

def analyze_prompt_and_modify_files(prompt, itr = 0):
    """Analyze the prompt and modify files accordingly"""
    print(f"Analyzing prompt (itr={itr})...")
    logging.info(f"============= ANALYZING PROMPT [ITR {itr}] ====================")
    logging.info(prompt)
    
    # List files in each directory
    rtl_files = list_directory_files(f"{base_path}/rtl")
    verif_files = list_directory_files(f"{base_path}/verif")
    docs_files = list_directory_files(f"{base_path}/docs")
    
    print(f"Found {len(rtl_files)} RTL files")
    logging.info(f"Found {len(rtl_files)} RTL files")

    # Process RTL files to replace "input" with "loompa"
    '''
    for rtl_file in rtl_files:
        rtl_path = os.path.join("/code/rtl", rtl_file)
        try:
            # Read the file content
            with open(rtl_path, 'r') as file:
                content = file.read()
            
            # Replace all occurrences of "input" with "loompa"
            modified_content = content.replace("input", "loompa")
            
            # Write the modified content back to the file
            with open(rtl_path, 'w') as file:
                file.write(modified_content)
                
            print(f"Replaced 'input' with 'loompa' in {rtl_file}")
        except Exception as e:
            print(f"Error processing {rtl_file}: {e}")
    '''
    
    # Example: Add a timestamp file to the rundir
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    write_file(f"{base_path}/rundir/agent_executed.txt", f"Agent executed at {timestamp}\nPrompt: {prompt}")
    
    response = deepseek(prompt)
    if not response:
        return

    if response["action"] == "writeFile":
        file_path = os.path.join(base_path, response["filePath"])
        write_file(file_path, response["content"])
        print(f'Modified file: {file_path}')
        logging.info(f'=============  MODIFY FILE: {file_path} =============')
        logging.info(response["content"])
    '''
    # Example: Check if we need to modify an RTL file based on prompt
    if "fix" in prompt.lower() and rtl_files:
        # Example: Take the first RTL file and add a comment
        rtl_file = rtl_files[0]
        rtl_path = os.path.join("/code/rtl", rtl_file)
       
        # content = read_file(rtl_path)
        write_file(rtl_path, response["content"])
        print(f"Modified RTL file: {rtl_file}")
    
    # Example: Add a documentation file
    '''
    '''
    if docs_files or "document" in prompt.lower():
        write_file(f"{base_path}/docs/agent_report.md", f"""# Agent Report
    

## Execution Summary
- Executed at: {timestamp}
- Prompt: {prompt}
- RTL files found: {len(rtl_files)}
- Verification files found: {len(verif_files)}
        
## Analysis
This is a sample agent report created during the agentic workflow execution.
        """)
        print("Created documentation file: agent_report.md")
        '''

def main():
    print("Starting CVDP agent...")
    logging.info("\n\n\n\n============== Starting CVDP agent ==============")
    
    # Read the prompt
    prompt = read_prompt()
    if not prompt:
        print("No prompt found in prompt.json. Exiting.")
        logging.error("No prompt found in prompt.json. Exiting.")
        sys.exit(1)

    for itr in range(1, MAX_ITR):
        analyze_prompt_and_modify_files(prompt, itr)

        retcode, stdout, stderr = run_pytest()
        if retcode != 0:
            # error_msg = extract_error_messages(stdout + "\n" + stderr)
            error_msg = stdout + "\n" + stderr
            print("Sanity test failed with error")
            logging.error("================ TEST FAILED ================")
            logging.error(error_msg)
            
            prompt = update_prompt_with_error(prompt, error_msg)
            
            # Optionally, rerun the sanity test or exit to retry externally
            print(f"Iteration {itr} completed.")
            logging.info(f"=============== ITERATION {itr} COMPLETED ===============")
        else:
            print("Test passed! Agent execution completed successfully.")
            logging.info("=============== MISSION COMPLETED ==================")
            sys.exit(0)
    
    print(f"Agent failed to pass the test within {itr} iterations.")
    logging.error(f"=============== MISSION FAILED ==================")
    logging.error(f"Agent failed to pass the test within {itr} iterations.")

if __name__ == "__main__":
    main() 