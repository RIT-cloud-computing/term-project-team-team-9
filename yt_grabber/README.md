# Youtube livestream image grabber

Grabs an image from a youtube livestream every 5 seconds and sends it to a lambda


## Installation
1. Install Python 3.9+
2. run `pip install youtube-dl`
3. run `pip install -r requirements.txt`
4. run `python grabber.py` to start the script

The script runs forever in a loop, so be sure to kill the process with `CTRL+C` or via the `kill` command
