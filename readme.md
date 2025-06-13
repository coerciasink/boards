# masonryBoard

## what this does

It takes directories filled with pics and sub directories filled with pics, and converts it into html files linking to those images. It will mimic the original file structure.
The images are arranged in a masonry format (looks like pinterest).
You can also create a file filled with images chosen randomly from a directory.
Click on the image to copy the image path.
You can change the number of columns shown.
Ignore the 'toggle layout' button for now.


## how to 

`python3 __main__.py`

that's it. following will show how to use the config.yml and use flags.

input your masterDir in the config.yml, the dir in which you want to store the created html files. 

Then create a csv file in the fileLists Folder.
Fill the first column with the absolute path of the directory with the images, and fill the second one with the name you want to give the directory in the created folders. 

You can change the csv filenames as you wish, add more or remove existing.

use --csvs flag to provide a list of csv files. If this isn't used, it will fallback to the directories mentioned in the config.yml.
You can choose a single directory using the --dir command.

You can also also set the margins in px and the column count in config, or by providing arguments. 

If you want to have a specific directory be used and select random N number of random images from it, you can do so. 

All the flags are optional.

This is what you would get if you used the flag --help.

```
usage: __main__.py [-h] [--random RANDOM] [--ranDir RANDIR]
                [--dir DIR] [--csvs CSVS [CSVS ...]]
                [--col COL] [--margin MARGIN]

Generate HTML for media directories.

options:
-h, --help            show this help message and exit
--random RANDOM       Select N random images from a directory   
                        and generate HTML.
--ranDir RANDIR       Directory to search images in for
                        --random
--dir DIR             Directory to use for the images
--csvs CSVS [CSVS ...]
                        List of CSV files to use
--col COL             number of columns to default to
                        (default: 5)
--margin MARGIN       Margin in px
```

That should be it. 

use this if you want to compile the app to a single binary. I am too lazy to release as precompiled binary files.

`pyinstaller --onefile __main__.py -n boards`



## Future to-dos

- [ ] Horizonatal layout. 
- [ ] make it so that it can push to a github pages site.
- [x] Clean the code, organise it and put it on github
- [x] Fix nested folders not being links issue.
- [x] Get the list of target and destination folders from a csv file or a txt file.
- [ ] hide image option
- [ ] Long press to open image in new tab
- [ ] star image option
- [ ] Bookmark location so that we can come to that part later
- [ ] Randomise button. Randomisation should be temporary, only till the tab is open. 
- [ ] sort by option
- [ ] add an option to copy a list of images to clipboard
- [ ] example site
- [ ] add the masterDir flag
- [ ] release precompiled binaries for win and mac. Linux users don't need this help tbh.
- [x] Random 100 pins from a folder feature. 
	- [x] You can also make this a static site feature, 
	- [x] add the utility in the python project instead of thr final product. The arguement will specify which directory to use.