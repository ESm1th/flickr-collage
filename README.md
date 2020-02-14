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
      |   README.md
      |   .env
      |   requirements.txt
      |---collage
            |   main.py
            |   collage.py
            |   fetcher.py
```

Change derictory to `collage` folder:
```
$ cd collage
```
