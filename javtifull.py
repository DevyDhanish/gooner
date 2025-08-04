import config
import requests as re
import html_parser
import argparse
import json
from tqdm import tqdm
import zstandard as zstd
import os
import time

MAX_RETRIES = 10
RETRY_INTERVAL = 2  # in seconds

def get_video_code(url):
    return url.split("/video/")[1].split("/")[1]

def get_video_id(url):
    return url.split("/video/")[1].split("/")[0]

def unique_filename(name, folder):
    base, ext = os.path.splitext(name)
    i = 1
    while os.path.exists(os.path.join(folder, name)):
        name = f"{base}_{i}{ext}"
        i += 1
    return name

def fetch_cdn_data(headers, payload):
    for attempt in range(MAX_RETRIES):
        try:
            res = re.post(config.CDN_URL, headers=headers, data=payload)
            if res.status_code != 200:
                print(f"[{res.status_code}] Bad response. Retrying in {RETRY_INTERVAL}s...")
                time.sleep(RETRY_INTERVAL)
                continue

            try:
                playlist_data = res.json()
                return playlist_data
            except json.JSONDecodeError:
                print("Not valid JSON. Retrying...\n")

        except Exception as e:
            print(f"Request error: {e}\nRetrying in {RETRY_INTERVAL}s...\n")

        time.sleep(RETRY_INTERVAL)

    print("Failed to get valid JSON after max retries.")
    return None

def download_video(url, output_file, output_folder):
    video_res = re.get(url, stream=True)

    if video_res.status_code != 200:
        print(f"Failed to fetch video: status {video_res.status_code}")
        return

    total_size = int(video_res.headers.get("Content-Length", 0))
    block_size = 8192

    filename = unique_filename(output_file, output_folder)
    full_path = os.path.abspath(os.path.join(output_folder, filename))

    with open(full_path, "wb") as f, tqdm(
        desc=f"Downloading {filename}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in video_res.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    print(f"Saved to {full_path}")

def process_url(url, output_folder):
    print(f"Processing: {url}")

    html_response = re.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if html_response.status_code != 200:
        print(f"Failed to load HTML: {html_response.status_code}")
        return

    config.submit_video_id(get_video_id(url))
    parser = html_parser.HtmlParser(html_response.content)
    config.submit_token(parser.get_data_csrf_token())

    cdn_headers = config.get_cdn_header(url)
    cdn_payload = config.GET_CDN_PAYLOAD

    playlist_data = fetch_cdn_data(cdn_headers, cdn_payload)
    if not playlist_data:
        return

    playlist_url = playlist_data["playlists"]

    download_video(playlist_url, get_video_code(url) + ".mp4", output_folder)

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
