import cloudscraper
import requests as req
import re
import tqdm
import argparse
import os

# "https:\/\/nineyu.com\/fc8b1eed-bfeb-4d7f-95ca-64dfa84b8d1a\/seek\/_0.jpg""

# #EXTM3U
# #EXT-X-VERSION:3
# #EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
# 640x360/video.m3u8
# #EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=842x480
# 842x480/video.m3u8
# #EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
# 1280x720/video.m3u8

def get_video_packet_url(code, resolution, video_packet):
    return f"https://surrit.com/{code}/{resolution}/{video_packet}"

def get_video_code(html_response):
    urls = re.findall(r'https:\\/\\/nineyu\.com\\/([a-z0-9-]{36})\\/seek\\/', html_response)
    if not urls:
        print("No video code found in the HTML response.")
        return None
    return urls[0]

def get_available_resolutions(code):
    res = re.findall(r'#EXT-X-STREAM-INF:BANDWIDTH=\d+,RESOLUTION=(\d+x\d+)', code)
    if not res:
        print("No resolutions found in the playlist.")
        return
    return res

def get_highest_resolution(resolutions):
    if not resolutions:
        return None
    # Sort resolutions by width and height, descending
    resolutions.sort(key=lambda x: (int(x.split('x')[0]), int(x.split('x')[1])), reverse=True)
    return resolutions[0]

def get_playlist_m3u8(code) -> str:
    return f"https://surrit.com/{code}/playlist.m3u8"

def get_video_m3u8(code, resolution) -> str:
    return f"https://surrit.com/{code}/{resolution}/video.m3u8"

def get_video_packets_str(video_url) -> list:
    response = req.get(video_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch video: {response.status_code}")
        return []

    video_packets = re.findall(r'video\d+\.jpeg', response.text)

    if not video_packets:
        print("No video packets found in the response.")
        return []
    
    return video_packets

def process_url(url, output_path):
    print(f"Processing URL: {url}")
    scrapper = cloudscraper.create_scraper()
    response = scrapper.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch URL {url}: {response.status_code}")
        return
    
    html_response = response.text

    video_code = get_video_code(html_response)
    if not video_code:
        return
    playlist_url = get_playlist_m3u8(video_code)
    response = req.get(playlist_url)

    res = get_highest_resolution(get_available_resolutions(response.text))

    if not res:
        print("No available resolutions found.")
        return

    video_url = get_video_m3u8(video_code, res)
    response = req.get(video_url)

    if response.status_code != 200:
        print(f"Failed to fetch video M3U8: {response.status_code}")
        return
    
    video_packets : list = get_video_packets_str(video_url)

    sample_video_packet = get_video_packet_url(video_code, res, video_packets[0])
    sample_packet_size = req.get(sample_video_packet).headers.get("Content-Length")
    total_size = len(video_packets) * int(sample_packet_size) if sample_packet_size else 0

    with open(os.path.join(output_path, f"{video_code}.mp4"), "wb") as f, tqdm.tqdm(
        desc=f"Downloading {video_code}.mp4",
        unit="B",
        total=total_size,
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for video_packet in video_packets:
            video_packet_download_url = get_video_packet_url(video_code, res, video_packet)

            response = req.get(video_packet_download_url, stream=True)
            if response.status_code != 200:
                print(f"Failed to download video packet: {response.status_code}")
                continue

            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                bar.update(len(chunk))

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