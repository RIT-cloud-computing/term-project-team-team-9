#!/bin/bash
yum update -y

#pull from github
git clone https://github.com/RIT-cloud-computing/term-project-team-team-9.git

#run script
cd term-project-team-team-9/cdk

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt

# zaharkin
cdk bootstrap aws://075837463923/us-east-2
cdk deploy --parameters emailparam="jaystalkeraws@gmail.com" --outputs-file ./cdk-outputs.json

cd ../

python3 switcher.py

cd yt-grabber

pip3 install -r requirements.txt

#print
echo "Completed"