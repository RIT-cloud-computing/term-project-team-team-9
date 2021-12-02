#!/bin/bash
yum update -y
yum install git

#pull from github
git clone https://github.com/RIT-cloud-computing/term-project-team-team-9.git

#run script
cd term-project-team-team-9

#print
echo "Completed"