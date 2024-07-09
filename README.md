# Sam's Club Bonus Offers Automated

This is a quick and dirty script in order to add all of the offers on https://bonusoffers.samsclub.com/venues to your card.

The idea is to schedule this script to run on a cadence you see fit and forget about it. There is the ability to add email configuration for it to send a notification if it faces an issue.

## Warning
This code uses automation tools to access your account. Review the terms of service for your account and use this tool at your own risk.

## Installation
1. Install [Google Chrome](https://www.google.com/chrome/)
2. Install requirements: `pip install -r requirements.txt`

## Usage
`python .\SamsClubBonusOffers.py` will prompt you for email and password

OR

`python .\SamsClubBonusOffers.py -n {EMAIL} {PASSWORD}` for starting script directly

If you want to have email configuration for when the script encounters errors, setup a .env file with respective information.

## Dependencies
This code uses the following dependencies:

- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver), which is licensed under GPL-3.0.
- [selenium](https://github.com/SeleniumHQ/Selenium), which is licensed under Apache-2.0.


