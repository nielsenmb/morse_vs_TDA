A simple UI for inspecting the pdfs provided by the TDA team. 

Currently only supports editing the _lc columns. Not the _sc columns. Not sure what to do about those yet.

Setup instructions
------------------
1. Put pdfs in a directory in /path/to/image/dir
2. Put the csv named WG1-2.csv in /path/to/csv

You'll need to have the PDF's locally and convert them to png first. The following worked on Ubuntu:
cd /path/to/image/dir
sudo mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off
ls *.pdf | xargs -I{} basename {} .pdf | xargs -I{} -t convert -density 100 -flatten {}.pdf {}.png
sudo mv /etc/ImageMagick-6/policy.xml.off /etc/ImageMagick-6/policy.xml

(The policy.xml lines disable and reenable the ImageMagick security policies)

The csv file is ; separated cause apparently crazy people made it. Don't worry about that. It'll be converted to , after you use inspectr first time.

Instructions
------------
-1. Read the instructions provided by the TDA people.
0. cd /directory/where/inspectr/is/located
1. python inspectr.py /path/to/csv/WG1-2.csv /path/to/image/dir/wg12/wg12
2. Gaze upon the visually stunning UI
3. Now look closer at the lightcurve/psd
4. Pick a primary classification from the top row of options (labels start with P).
5. Pick a secondary classification from the bottom row of otpons (labels start with S). Picking a secondary without first picking a primary or picking a secondary that is the same as the primary does nothing.
6. Optionally write in a note about weirdness.
7. Press the Next button.

If you make a mistake well...good luck. You'll need to edit the csv manually. 

Todo
----
Add in a note on the statusbar what the previous target in case you make a mistake.

