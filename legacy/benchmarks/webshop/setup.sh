# Clone the webshop repo (tested up to 29.07.2023 commit a557a208d03b93c83f4075e66e8746922606e60f)
git clone https://github.com/princeton-nlp/WebShop.git webshop

# Check if default-jdk is installed
if dpkg -l | grep -q 'default-jdk'; then
    echo "default-jdk is installed."
else
    echo "default-jdk is not installed. Run the following commands, then re-run `make install-webshop`:"
    echo "(sudo) apt update"
    echo "(sudo) apt install default-jdk"
    exit 1
fi

# Install extra packages not included in webshop repo's requirements.txt
pip install -r requirements.txt

# Patch webshop repo's setup.sh
file="webshop/setup.sh"
# Define the patterns to match for commenting out
patterns="
conda install -c pytorch faiss-cpu;
conda install -c conda-forge openjdk=11;
"
# Comment out the lines matching the patterns
for pattern in $patterns; do
    sed -i "s|^$pattern|# $pattern|g" "$file"
done

# Patch webshop repo's requirements.txt (too old spacy includes a requirement of a too old pydantic wrt the one required by openai)
sed -i "s|^spacy==3.3.0|spacy==3.7.4|g" webshop/requirements.txt
sed -i "s|^torch==1.11.0|torch==2.2.0|g" webshop/requirements.txt
sed -i "s|^transformers==4.19.2|transformers==4.37.2|g" webshop/requirements.txt

# Install WebShop
curr_dir=$(pwd)
cd webshop
./setup.sh -d small
cd "${curr_dir}"

echo "DONE!"
