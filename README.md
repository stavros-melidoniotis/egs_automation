# egs_automation
Python script that automatically acquires each week's free games on Epic Games Store.

# How it works
Before trying to run the script you must first open secrets.py file with a text editor and input:

1. Your Epic Games username or email
2. Your account's password

When running the script a Chrome window will open with the message "Chrome is being controlled by automated test software". Epic Games' login page will appear and you'll be loged into your account. After that you'll be redirected to the store page. The script now is going to locate this week's free games and open each one of them in a different tab. It will add them to user's game library if they aren't already owned and close each tab on finish.

# Requirements
You must have Python3 and pip installed on your system. Create a virtual environment by typing `python3 -m venv ./yourname`. Activate the environment by typing `source ./yourname/bin/activate`. The final step is to install Selenium package by typing `pip3 install selenium`.

If you get an error about Chrome and chromedriver incompatible version, then open Chrome and navigate to chrome://version. Locate the version of your browser and download the appropriate chromedriver from [here](https://chromedriver.chromium.org/downloads). Replace the project's chromedriver with the chromedriver you just downloaded and you're done.
