# Gooner 💦

**Gooner** is your all-in-one badass porn video downloader. Just drop your links, and it figures out what to grab—no stress, no hassle. Whether it’s a single video or a batch, Gooner’s got you covered.

---

## Features

- Downloads 😏 videos from multiple websites seamlessly  
- Supports single video download with a URL  
- Batch download from a list of links in a text file  
- Automatically detects and grabs the correct video from the link  
- Easy to use, just provide links and output folder  

---

## How to Use

### RUN PIP TO INSTALL REQUIREMENTS
if possible use conda and create a venv with ```python=3.13```
```bash
pip install -r requirements.txt
```

### Single Video Download

```bash
python gooner.py -u "url" -o "output_folder"
```

### BATCH DOWNLOAD
```bash
python gooner.py -b url.txt -o "output_folder"
```

### URL.txt
```bash
link 1
link 2
link 3
```