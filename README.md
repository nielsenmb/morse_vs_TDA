A simple UI for inspecting the pdfs provided by the TDA team. 

Setup instructions
------------------
1. Put pdfs in a directory in /path/to/image/dir
2. Put the csv named WG1-2.csv (or similar for your WG) in /path/to/csv (Note: this will be edited when you start classifying, so make a backup)

You'll need to have the PDF's locally and convert them to png first. I don't know how to make PyQT show pdf files. Converting to png might be system dependent. The following worked on Ubuntu:
1. cd /path/to/image/dir
2. sudo mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off
3. ls *.pdf | xargs -I{} basename {} .pdf | xargs -I{} -t convert -density 100 -flatten {}.pdf {}.png
4. sudo mv /etc/ImageMagick-6/policy.xml.off /etc/ImageMagick-6/policy.xml

(The policy.xml lines disable and reenable the ImageMagick security policies)

For other systems I'm not sure how to convert.

The WG1-2.csv file is semi-colon separated. Don't worry about that. It'll be converted to comma after you use inspectr first time.

Instructions
------------
1. Read the instructions provided by the TDA people.
2. cd /directory/where/inspectr/is/located
3. python inspectr.py /path/to/csv/WG1-2.csv /path/to/image/dir/wg12/wg12
4. Gaze upon the visually stunning UI
5. Now look closer at the lightcurve/psd
6. Pick a primary classification from the top row of options (labels start with P).
7. Pick a secondary classification from the bottom row of otpons (labels start with S). Picking a secondary without first picking a primary or picking a secondary that is the same as the primary does nothing.
8. Optionally write in a note about weirdness.
9. Press the Next button.

If you make a mistake well...good luck. You'll need to edit the csv manually. 
