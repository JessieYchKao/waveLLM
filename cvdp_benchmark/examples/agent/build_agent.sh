#!/bin/sh 

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# docker build -f Dockerfile-base -t cvdp-example-agent-base .

# Check if the base image exist before building it
if [[ "$(docker images -q cvdp-cadence-base 2> /dev/null)" == "" ]]; then
  echo "Image cvdp-cadence-base not found. Building..."
  docker build -f Dockerfile-cadence -t cvdp-cadence-base .
else
  echo "Image cvdp-cadence-base already exists. Skipping build."
fi

docker build -f Dockerfile-agent -t cvdp-example-agent --no-cache .
