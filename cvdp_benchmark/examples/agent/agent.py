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

BASE_URL_DEEPSEEK = "https://api.deepseek.com"
MODEL_NAME_DEEPSEEK = "deepseek-reasoner"
BASE_URL_GPT_4O_MINI = ""
MODEL_NAME_GPT_4O_MINI = "gpt-4o-mini"
MODEL_NAME_GPT_5 = "gpt-5"
API_KEY = os.getenv("OPENAI_USER_KEY")
MAX_ITR = int(os.getenv("MAX_ITR"))

# Setup logging for agent
log_path_debug = f"{base_path}/rundir/agent_debug.log"
log_path_info = f"{base_path}/rundir/agent_info.log"
log_path_error = f"{base_path}/rundir/agent_error.log"

logger = logging.getLogger("agent_logger")
logger.setLevel(logging.DEBUG)  # Capture ALL logs

# Create formatters
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Handler for DEBUG (everything)
debug_handler = logging.FileHandler(log_path_debug)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

# Handler for INFO only (but not WARNING/ERROR/CRITICAL)
info_handler = logging.FileHandler(log_path_info)
info_handler.setLevel(logging.INFO)
info_handler.addFilter(lambda record: record.levelno == logging.INFO)
info_handler.setFormatter(formatter)

# Handler for ERROR and above
error_handler = logging.FileHandler(log_path_error)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(debug_handler)
logger.addHandler(info_handler)
logger.addHandler(error_handler)

greet = f""" You are an AI software agent for chip design automation.
If the test case fails, return a 1 from the function or task. Record the number of failed testcases and end simulation with $error, otherwise if there are no failiure end simulation with $finish."
When asking a question, you can only answer in the provided JSON format (must be a valid JSON string). 
Here are some options that you have, but you can only pick one action at a time
{{
    "action": "writeFile",
    "filePath": "The path of the file you want to overwrite or create if not exist"
    "content": "//The code or content that needs to be write to the file",
    "note": "Any other things you want to say or explain"
}},
{{
    "action": "readFiles",
    "filePath": "The path of a list of files you want to read. Format: ["file1.txt", "file2.sv"]"
    "content": "",
    "note": "Any other things you want to say or explain"
}},
{{
    "action": "listFiles",
    "filePath": "Path to the target folder to list all files"
    "content": "",
    "note": "Any other things you want to say or explain"
}}

Depending on the task specified by the prompt intelligently select an action to provide more information, which will help you to complete the task.
"""

def run_pytest():
    print("Running pytest")
    logger.info("=============== RUNNING PYTEST ============")
    cmd = "pytest /src/process.py -v -s"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Pytest return with errorCode {result.returncode}")
    logger.debug(f"pytest result: {result}")
    logger.info(f"Pytest complete with errorCode {result.returncode}")
    return result.returncode, result.stdout, result.stderr

 # Extract lines containing 'ERROR' or '*E' or 'assertion'
def extract_error_messages(output):
    error_lines = []
    for line in output.splitlines():
        if "ERROR" in line or "*E" in line or "assert" in line.lower():
            error_lines.append(line)
    return "\n".join(error_lines)

def extractJson(text):
    pattern = r"```(?:\w+\n)?(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def llm(prompt):
    print('Waiting for answer from LLM...\n')
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL_DEEPSEEK)

    response = client.chat.completions.create(
        model=MODEL_NAME_DEEPSEEK,
        messages=[
            {"role": "system", "content": greet},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    print("============= RESPONSE ====================")
    logger.info("============= RESPONSE ====================")
    logger.debug(response.choices[0].message.content)
    text = extractJson(response.choices[0].message.content)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        logger.error(f'Invalid JSON: {e}')
        return

def read_prompt():
    """Read the prompt from prompt.json"""
    try:
        with open(f"{base_path}/prompt.json", "r") as f:
            prompt_data = json.load(f).get("prompt", "")
            docs = list_directory_files(f"{base_path}/docs")
            print(docs)
            if len(docs) > 0:
                print(f"Reading {len(docs)} files under /docs")
                logger.info(f"Reading {len(docs)} files under /docs")
                prompt_data += f"Please follow the provided specifications:\n" + read_files(docs)
            return prompt_data
    except Exception as e:
        print(f"Error reading prompt.json: {e}")
        logger.error(f"Error reading prompt.json: {e}")
        return ""

def list_directory_files(dir_path):
    """List all files in a directory recursively"""
    files = []
    if os.path.exists(dir_path):
        for root, _, filenames in os.walk(dir_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, dir_path)
                files.append(f"{dir_path}/{rel_path}")
    return files

def read_files(file_list):
    """Read the contents of a file"""
    file_contents = ""
    for file in file_list:
        file_path = os.path.join(base_path, file)
        try:
            with open(file_path, "r") as f:
                file_contents += file + ":\n" + f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            logger.error(f"Error reading file {file_path}: {e}")
            file_contents += file_path + ": File not exist"
    return file_contents

def write_file(file_path, content):
    """Write content to a file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
        logger.info(f"Successfully wrote to {file_path}")
        logger.debug(f"content: {content}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        logger.error(f"Error writing to file {file_path}: {e}")

def run_agent(prompt, itr = 0):
    """Analyze the prompt and take actions accordingly"""
    print(f"============= ITERATION {itr} ====================")
    logger.info(f"============= ANALYZING PROMPT [ITR {itr}] ====================")
    logger.debug(prompt)
    
    # List files in each directory
    rtl_files = list_directory_files(f"{base_path}/rtl")
    verif_files = list_directory_files(f"{base_path}/verif")
    docs_files = list_directory_files(f"{base_path}/docs")
    
    logger.debug(f"Found {len(rtl_files)} RTL files")

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
    
    response = llm(prompt)
    if not response:
        return False, "Response format incorrect, please follow the instruction and wrap the json response inside code block (``` json here ```)"

    print((f"Action: {response["action"]}, filePath: {response["filePath"]}"))
    logger.info(f"Action: {response["action"]}, filePath: {response["filePath"]}")
    if response["action"] == "writeFile":
        file_path = os.path.join(base_path, response["filePath"])
        write_file(file_path, response["content"])
        print(f'Modify file: {file_path}')
        logger.info(f'=============  MODIFY FILE: {file_path} =============')
        logger.debug(f"File content {response["content"]}")
        return  True, "Modified " + response["filePath"] + ":\n" + response["content"] 
    elif response["action"] == "readFiles":
        return False, read_files(response["filePath"])
    elif response["action"] == "listFiles":
        return False, "File list under " + response["filePath"] + ":\n" + list_directory_files(file_path)
    return False, ""
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
    logger.info("============== Starting CVDP agent ==============")
    
    # Read the prompt
    base_prompt = read_prompt()
    if not base_prompt:
        print("No prompt found in prompt.json. Exiting.")
        logger.error("No prompt found in prompt.json. Exiting.")
        sys.exit(1)

    prompt = base_prompt
    error_msg = ""
    for itr in range(1, MAX_ITR+1):
        run_test, last_response = run_agent(prompt, itr)

        if run_test:
            retcode, stdout, stderr = run_pytest()
            if retcode != 0:
                print("Pytest has error")
                logger.info("Pytest has error")
                error_msg = stdout + "\n" + stderr
                
                prompt = base_prompt + "\n\nThe previous code you've generated:\n"
                prompt += last_response
                prompt += "\n\nThe simulation test failed with the following errors:\n"
                prompt += error_msg
                prompt += "\nPlease fix it accordingly."
            else:
                print("Test passed! Agent execution completed successfully.")
                logger.info(f"=============== MISSION COMPLETED (Within {itr+1} iterations) ==================")
                sys.exit(0)
        else:
                prompt = base_prompt + "\n\n" + last_response
                if error_msg != "":
                    prompt += "\n\nThe previous simulation test failed with the following errors:\n"
                    prompt += error_msg
                    prompt += "\nPlease fix it accordingly."

        print(f"Iteration {itr} completed.")
        logger.info(f"=============== ITERATION {itr} COMPLETED ===============")
    
    print(f"Agent failed to pass the test within {MAX_ITR} iterations.")
    logger.info(f"=============== MISSION FAILED ==================")
    logger.error(f"Agent failed to pass the test within {MAX_ITR} iterations.")

if __name__ == "__main__":
    main()