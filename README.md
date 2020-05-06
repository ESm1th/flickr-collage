# flickr-collage
Fetch images from flickr API and create collage.

To run this app you should use `python >= 3.7`, because some features of `asyncio` that used in this project appeared in `python 3.7`, therefore app might not work on other `python` versions.

### How to start
Create `Flickr` app and obtain `API key`  [link](https://www.flickr.com/services/apps/create/apply/)

Clone repository:
```
$ git clone https://github.com/ESm1th/flickr_collage.git
```

Change working directory to project:
```
$ cd flickr_collage
```

Create virtual environment and activate it:
```
$ mkvirtualenv flickr --python=python3.7
```

Install dependencies:
```
$ pip install -r requirements.txt
```

Add `.env` file to project's folder with following variable:
```
API_KEY=some_api_key  # key obtained in first step
```

Structure of project:
```
+---flickr_collage
      |   .gitignore
      |   .env
      |   requirements.txt
      |   README.md
      |---collage
            |   main.py
            |   collage.py
            |   fetcher.py
```

Change derictory to `collage` folder:
```
$ cd collage
```

App has some `flags` to customize collage:

**Flag**|**Name**|**Required**|**Default**|**Description**
--------|--------|------------|-----------|---------------
`-t`|`--text`|Yes|-|text for searching images
`-q`|`--quantity`|No|20|quantity of images in collage
`-r`|`--rows`|No|5|rows of images in collage
`-c`|`--columns`|No|5|columns of images in collage
`-s`|`--size`|No|240,180|size of image as "width,height" form

The created collage is saved in the working directory with pattern:
```
{--text}_{timestamp}.png
```

### Examples:

Search and fetch 20 images by tag `ninja` and draw collage with 3 rows and 4 columns (only 12 images from fetched 20)
```
collage$ python main.py -t ninja -q 20 -r 3 -c 4
```
Result:
```
Done! Spent time: 6.0147929191589355
```
Search and fetch 50 images by tag `sea` and draw collage with 5 rows and 5 columns (only 25 images from fetched 50)
```
collage$ python main.py -t sea -q 50
```
Result:
```
Done! Spent time: 19.630441904067993      
```
