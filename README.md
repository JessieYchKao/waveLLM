
source env_setup.sh


https://github.com/YosysHQ/oss-cad-suite-build/releases
export PATH=../oss-cad-suite/bin:$PATH


ollama run nomic-embed-text

export DEEPSEEK_API_KEY


python parseVCD.py