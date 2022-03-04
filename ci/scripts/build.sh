set -e

rm -rf build
mkdir build

cd build

cp ../requirements.txt .
pip install -r requirements.txt --target ./package

cp -R ../cloudwatch-log-group-enforcer .
