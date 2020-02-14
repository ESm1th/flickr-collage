# flickr_collage
Fetch images from flickr API and create collage.

### How to start
Create `Flickr` app and obtain `API key` [link](https://www.flickr.com/services/apps/create/apply/)

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

Add `.env` file to project's folder with following variables:
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
