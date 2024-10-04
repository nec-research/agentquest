# Clone the repository
git clone https://github.com/lucagioacchini/auto-pen-bench
cd auto-pen-bench

# Copy the data files
cp data/games.json ../../../agentquest/data/autopenbench

# Install the benchmark
make install

# Copy the content of .env in an existing file or create a new one
if [ ! -f ../../.env ]; then
    cp .env ../../../
else
    cat .env >> ../../../.env
fi