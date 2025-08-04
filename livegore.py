import requests as re
from tqdm import tqdm
import argparse
import os
from html_parser import HtmlParser

URL = ""
VIDEO_URL = "https://xxx.livegore.com//rb-include/videos/"
VIDEO_ID_TAG = "example_video_1"

def get_video_name(url):
    return url.split("/videos/")[1]

# def get_video_id(url):
#     return url.split("/video/")[1].split("/")[0]

# def unique_filename(name, folder):
#     base, ext = os.path.splitext(name)
#     i = 1
#     while os.path.exists(os.path.join(folder, name)):
#         name = f"{base}_{i}{ext}"
#         i += 1
#     return name

def download_video(url, output_folder):
    video_data = re.get(url, stream=True)
    
    if video_data.status_code != 200:
        print(f"Failed to fetch video : {video_data.status_code}")
        return

    total_size = int(video_data.headers.get("Content-Length", 0))
    block_size = 8192

    filename = get_video_name(url)
    full_path = os.path.abspath(os.path.join(output_folder, filename))

    with open(full_path, "wb") as f, tqdm(
        desc=f"Downloading {filename}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in video_data.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    print(f"Saved to {full_path}")

def process_url(url, output_folder):
    print(f"Processing {url}")

    html_response = re.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if html_response.status_code != 200:
        print(f"Failed to load HTML: {html_response.status_code}")
        return

    parser = HtmlParser(html_response.content)

    video_tag = parser.get_by_id(VIDEO_ID_TAG)
    video_src = video_tag.find("source").get("src")

    download_video(video_src, output_folder)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Single video URL")
    parser.add_argument("-b", "--batch", help="File with list of video URLs")
    parser.add_argument("-o", "--output", help="Output folder", required=True)
    args = parser.parse_args()

    output_folder = args.output

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if args.url:
        process_url(args.url, output_folder)

    elif args.batch:
        try:
            with open(os.path.abspath(args.batch), "r") as f:
                urls = [line.strip() for line in f if line.strip()]
                for url in urls:
                    process_url(url, output_folder)
        except Exception as e:
            print(f"Failed to read batch file: {e}")

    else:
        print("bruh give me -u or -b")

if __name__ == "__main__":
    main()