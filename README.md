I find it easier to log contacts to spreadsheet by format:
callsign  locator  timestamp 
for example:
ES1AA  KO29IK  1710

In Baltic VHF/UHV/SHF august contest we also need serial, so it transforms to:

callsign serial locator mode timestamp my serial frequency
for example:
ES0AA  015 ko18oq  fm  1824    001 145.400

So txttoedi.py is ment for convert thise simple lines from spreadsheet to EDI contact lines, but information in front must be added manually, for example by coping from https://es1bbq.github.io/EDI/ web logger.

adiftoedi.py is used for WSJT-X adif lines to be converted to EDI contacts for sending as logs in every month VHF/UHF 2m/70cm/4/m/6m 
