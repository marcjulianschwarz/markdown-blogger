# markdown-blogger

A Python tool for converting markdown files into a blog webpage.

This was made to generate my website [marc-julian.com](https://www.marc-julian.com). It is not tested (only for my needs). Of course you can try to use it and let me know if there are any issues.

## Basic Usage

Make sure to update all of the hardcoded values (e.g. default values for post metadata) and the template html files.

Create a file `paths.py` and specify the variables `BLOG_IN` (path to markdown files) and `BLOG_OUT` (path to folder where website should be generated).

Then call `blog.py` like this:

```
python blog.py
```

You can specify the flags `-o` to open the page in your browser and `-w` to create the _web-version_ of the blog. The normal (local) version will use your local paths for all of the links, so you can try the website locally first.

So to make it ready for publishing run

```
python blog.py -w
```
