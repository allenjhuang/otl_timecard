# OTL Timecard
Creates a new timecard for overtime-eligible Oracle employees using a csv file as reference.

Tested to be working with Python 3.8.5.


## How to use
### Windows with Firefox
1. Download and install the Mozilla Firefox browser.
2. Download the latest Windows release in https://github.com/allenjhuang/otl_timecard/releases.
3. Download the Firefox webdriver.
4. Move geckodriver.exe to the same folder as create_timecard.exe.
5. Copy timecard.csv, config.toml, and optionally secrets.toml from the templates folder to the same folder as create_timecard.exe.
6. Edit the timecard.csv file, entering your own timecard details. (See note #1)
7. Run the create_timecard executable. (See note #2)
8. Save if you want and submit your timecard. This program does not submit for you!

Go through steps 6 and 8 again for each timecard entry.


#### Notes:
1. If you're using a spreadsheet editor like Excel or LibreCalc, be careful of the autocorrect. For example, LibreCalc automatically replaces the regular dashes with long dashes in some situations. We want to make sure that the values for the first five fields exactly match the Oracle timecard website values.
2. A new Firefox window will open up. If the secrets.toml file is provided, it'll automatically log into the Oracle SSO. Otherwise, you'll have to enter your Oracle SSO username and password at the login screen. The program should move to the timecard section and fill it out according to the timecard.csv file from here. After filling out the timecard details, the program ends there. You'll have to save (if you want) and submit the timecard yourself.
3. Make sure you're on the Oracle network.


## TODO
1. Add exceptions for more situations.


## Thanks
Thank you, Tommy (Kai) Zhao, for guiding and motivating me through the creation of the first version!
