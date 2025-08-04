import requests as req
import cloudscraper
import argparse
import os
import bs4
import re
import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

def get_video_name(url):
    return str(url.split("/")[-1])

def get_highest_resolution_player(m3u8_content):
    urls = re.findall(r'^https://.*?\.m3u8$', m3u8_content, re.MULTILINE)
    if not urls:
        print("No valid m3u8 URLs found in the response.")
        return ""
    return urls[-1]

def get_segment_links(m3u8_content):
    segment_links = re.findall(r'^(https://.*?\.ts)$', m3u8_content, re.MULTILINE)
    if not segment_links:
        print("No segment links found in the m3u8 content.")
        return []
    return segment_links

def process_url(url, output_path):
    session = req.Session()
    session.headers.update(HEADERS)
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch URL {url}: {response.status_code}")
            return

        html_parser = bs4.BeautifulSoup(response.text, "html.parser")
        video_tag = html_parser.find(name="video")

        if not video_tag:
            print("No video tag found in the HTML.")
            return  

        source_tag = video_tag.find(name="source")
        player_url = source_tag.get("src") if source_tag else None
        if not player_url:
            print("No source URL found in the video tag.")
            return

        res_response = session.get(player_url)
        if res_response.status_code != 200:
            print(f"Failed to fetch video player URL: {res_response.status_code}")
            return

        highest_res = get_highest_resolution_player(res_response.text)
        if not highest_res:
            print("No m3u8 player URL found.")
            return

        seg_pack_req = session.get(highest_res)
        if seg_pack_req.status_code != 200:
            print(f"Failed to fetch video segments: {seg_pack_req.status_code}")
            return

        segment_links = get_segment_links(seg_pack_req.text)
        if not segment_links:
            print("No .ts segments found.")
            return

        file_name = get_video_name(url)
        print(f"Calculating total size for {file_name}.mp4...")

        sample_segment = segment_links[0]
        try:
            sample_packet = session.get(sample_segment, stream=True)
        except req.exceptions.SSLError:
            print("SSL error on segment fetch, retrying without verify...")
            sample_packet = session.get(sample_segment, stream=True, verify=False)

        if sample_packet.headers.get("Content-Length"):
            sample_packet_size = int(sample_packet.headers["Content-Length"])
            total_size = len(segment_links) * sample_packet_size
        else:
            print("No Content-Length found, estimating size by 1024 bytes per segment.")
            total_size = len(segment_links) * 1024

        output_file = os.path.join(output_path, f"{file_name}.mp4")
        with open(output_file, "wb") as f, tqdm.tqdm(
            desc=f"Downloading {file_name}.mp4",
            unit="B",
            total=total_size,
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for seg_url in segment_links:
                try:
                    ts_packet = session.get(seg_url, stream=True)
                except req.exceptions.SSLError:
                    ts_packet = session.get(seg_url, stream=True, verify=False)

                if ts_packet.status_code != 200:
                    print(f"Failed to download segment: {ts_packet.status_code}")
                    continue

                for chunk in ts_packet.iter_content(chunk_size=1024):
                    f.write(chunk)
                    bar.update(len(chunk))

    except Exception as e:
        print(f"Error processing URL: {e}")

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
