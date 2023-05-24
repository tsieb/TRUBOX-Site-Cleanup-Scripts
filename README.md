## TRUBOX-Site-Cleanup-Scripts

Scripts to help automate and simpllify the process of cleaning up TRUBOX sites

## Files

The repository contains the following files:

1. `automated_browser.py`: This is the main Python script.
2. `config.json.template`: A template for the configuration file. You need to rename it to `config.json` and replace placeholders with actual values.
3. `sitemasterlist.txt`: This file contains a list of websites which the script will use.

## Installation

To run this project, you need to install the following Python libraries:

1. `json`
2. `pynput`
3. `win10toast`
4. `selenium`
5. `threading`

You can install these libraries using pip:

```bash
pip install json pynput win10toast selenium
```

## Configuration

1. Rename config.json.template to config.json.
2. Replace <your-username> and <your-password> with your login credentials.
3. Update the site list in sitemasterlist.txt with the sites you want to automate.
4. Configure the hotkeys, browser options, and page priorities in the config.json file.

## Execution

Run the script with the following command:
```bash
python automated_browser.py
```

## Disclaimer

Please make sure you have the necessary permissions to automate the interaction with the websites listed in the sitemasterlist.txt. Any misuse of this script is not the responsibility of the authors.

## License

This project is open source and available under the GNU General Public License v3.0.