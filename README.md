## TRUBOX-Site-Cleanup-Scripts

Scripts to help automate and simplify the process of cleaning up TRUBOX sites

## Files

The repository contains the following files:

1. `automated_browser.py`: This is the main Python script.
2. `config.json.template`: A template for the configuration file. You need to rename it to `config.json` and replace placeholders with actual values.
3. `sitemasterlist.txt`: This file contains a list of websites which the script will use.

## Installation

To run this project, you need to install the following Python libraries:

1. `pynput`
2. `win10toast`
3. `selenium`

You can install these libraries using pip:

```bash
pip install pynput win10toast selenium
```

## Configuration

1. Rename config.json.template to config.json.
2. Replace ```<your-username>``` and ```<your-password>``` with your login credentials.
3. Update the site list in sitemasterlist.txt with the sites you want to iterate over.
4. Configure the hotkeys, browser options, and pages in the config.json file.

## Execution

Run the script with the following command:
```bash
python automated_browser.py
```

## Additional Features
- Reverse iteration is possible by setting ```reverse_list``` to ```true```
- An offset can be added to align the internal list, starting at index 0, with another list that may start at another index (like a spreadsheet with header lines).
- Additional Selenium browser options can be added to ```browser_options```. This has not been thouroughly tested, so use caution.
- A Toast Windows notification can be enabled, with ```loaded_toast``` to ```true```, that will alert when the pages have loaded successfuly.
- The browser can open in fullscreen automatically with ```maximize_browser```.
- The displayed page after all pages are loaded can be set manually by changing ```displayed_page``` to the index of the desired page.

## Disclaimer

Please make sure you have the necessary permissions to automate the interaction with the websites listed in the sitemasterlist.txt. Any misuse of this script is not the responsibility of the authors.

## License

This project is open source and available under the GNU General Public License v3.0.
