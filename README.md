# Inspectr

A simple UI for inspecting the pdfs provided by the TDA team. 

Running inspectr.py will launch a UI that displays the images that were distributed by the TDA team, one by one. You then click what you think the primary variability source is, and then any number of secondary sources. 

You can optionally add a note in case of lightcurve weirdness. 

You'll need to have the PDF's locally and convert them to png first, since I don't know how to make PyQT show pdf files. See below for what worked with Ubuntu.

**If you have any questions or ideas to improving the UI, create an issue to let me know.**

In the setup and usage instructions you'll need to replace boldface text with the bits that are appropriate for your system.

Setup instructions
------------------
1. Clone/download this repo and put it in a sensible place.
2. Download and put pdfs in a directory in **/path/to/image/dir**
3. Download and put the csv named **WGx-x.csv** in **/path/to/csv** (Note: this will be edited when you start classifying, so make a backup)
4. cd **/path/to/image/dir**
5. sudo mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.off
6. ls *.pdf | xargs -I{} basename {} .pdf | xargs -I{} -t convert -density 100 -flatten {}.pdf {}.png
7. sudo mv /etc/ImageMagick-6/policy.xml.off /etc/ImageMagick-6/policy.xml

Step 5 and 7 were found to be Ubuntu specific. They disable and reenable the ImageMagick security policies, so if you need to do step 5 it's important that you also do step 7.

The **WGx-x.csv** file is semi-colon separated. Don't worry about that, it'll be converted to comma after you use inspectr first time.

Usage instructions
------------------
1. Read the instructions provided by the TDA people.
2. cd **/directory/where/inspectr/is/located**
3. python inspectr.py **/path/to/csv/WGx-x.csv** **/path/to/image/dir/wgxx/wgxx** --initials **abc**
4. Gaze upon the visually stunning UI
5. Now look closer at the lightcurve/psd
6. Pick a primary classification from the top row of options (labels start with P).
7. Pick a secondary classification from the bottom row of otpons (labels start with S). Picking a secondary without first picking a primary or picking a secondary that is the same as the primary does nothing.
8. Optionally write in a note about weirdness in the blank text field.
9. Press the Next (save) button.

Notes
-----
The multi variability flag is automatically set if a secondary variability source is entered, so don't worry about that

Having the csv file open in, for example, a text editor at the same time as using inspectr may mess things up.

Progress is stored every time you press the Next button, so you can close the window and reopen it again. 

If you make a mistake well...good luck. You'll need to edit the csv manually. 

You can use the --shuffle option when starting inspectr to shuffle the rows in the csv file. More randomness is fun. 

At the moment the default is to look at the long cadence lightcurves. You can run inspectr with the --cadence sc argument to just view the short cadence lightcurve files, but you can't swap between the modes on-the-fly. 
