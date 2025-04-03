#!/bin/bash
set -e

git clone https://github.com/princeton-nlp/WebShop.git

# Check if default-jdk is installed
if dpkg -l | grep -q 'default-jdk'; then
    echo "default-jdk is installed."
else
    echo "default-jdk is not installed. Run the following commands"
    echo "(sudo) apt update"
    echo "(sudo) apt install default-jdk"
    exit 1
fi

# Patch webshop repo's setup.sh
file="WebShop/setup.sh"
# Define the patterns to match for commenting out
patterns="
conda install -c pytorch faiss-cpu;
conda install -c conda-forge openjdk=11;
"
# Comment out the lines matching the patterns
for pattern in $patterns; do
    sed -i "s|^$pattern|# $pattern|g" "$file"
done
sed -i "/python -m spacy download en_core_web_lg/a python -m spacy download en_core_web_sm" "$file"

# Patch webshop repo's requirements.txt (too old spacy includes a requirement of a too old pydantic wrt the one required by openai)
cp WebShop/requirements.txt WebShop/requirements_orig.txt
sed -i "s|^spacy==3.3.0|spacy==3.7.4|g" WebShop/requirements.txt
sed -i "s|^torch==1.11.0|torch==2.2.0|g" WebShop/requirements.txt
sed -i "s|^transformers==4.19.2|transformers==4.37.2|g" WebShop/requirements.txt
echo "WerkZeug==2.2.2" >> WebShop/requirements.txt
echo "faiss-cpu==1.7.3" >> WebShop/requirements.txt

#Make a new environment for WebShop and install the packages there
python -m venv .webshop-venv
source .webshop-venv/bin/activate

# Install WebShop
curr_dir=$(pwd)
cd WebShop
./setup.sh -d small
cd "${curr_dir}"

deactivate

echo "DONE!"