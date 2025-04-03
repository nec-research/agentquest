# Install Python requirements
pip3 install -r requirements.txt

# Install remoteweb
git clone git@repos.ant-net:lgioacchini/remoteweb.git
cd remoteweb
pip3 install .
cd ..
rm -rf remoteweb
