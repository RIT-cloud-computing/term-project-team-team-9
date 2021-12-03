#!/bin/bash
yum update -y
yum install git -y

#pull from github
git clone https://github.com/RIT-cloud-computing/term-project-team-team-9.git

#run script
cd term-project-team-team-9/cdk

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt

cdk deploy
#print
echo "Completed"