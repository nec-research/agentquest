# Clone the alfworld repo
git clone https://github.com/alfworld/alfworld.git alfworld

# Finish installation
rm alfworld/requirements.txt && cp requirements.txt alfworld/requirements.txt
pip3 install https://github.com/MarcCote/downward/archive/faster_replan.zip
pip3 install https://github.com/MarcCote/TextWorld/archive/handcoded_expert_integration.zip
cd alfworld && pip3 install .

# Apply patches
python_version=$(python3 -c 'import sys; print("python" + str(sys.version_info.major) + "." + str(sys.version_info.minor))')
packages=$(python3 -c "import os, sys; print(os.path.dirname(next(iter([p for p in sys.path if 'site-packages' in p and 'python' in p]))))")
tatsu_path="$packages/site-packages/tatsu/grammars.py"
fdownward_path="$packages/site-packages/fast_downward/interface.py"

diff -u $tatsu_path ../patches/grammars.py > ../patches/my_patch.patch
patch $tatsu_path < ../patches/my_patch.patch

diff -u $fdownward_path ../patches/interface.py > ../patches/my_patch.patch
patch $fdownward_path < ../patches/my_patch.patch

rm ../patches/my_patch.patch

# Move one level up and create alfworld_data directory
cd ..
mkdir -p /home/user/alfworld_data

# Get the absolute path of the directory
alfworld_data_path=$(readlink -f /home/user/alfworld_data)

# Set the ALFWORLD_DATA environment variable
export ALFWORLD_DATA="$alfworld_data_path"

cd alfworld && alfworld-download
# Remove folder
#cd .. && rm -rf alfworld
