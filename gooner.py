import argparse
import os

import livegore
import playvids
import playvids
import missav
import javtifull
import crazyshit

def get_downloader(url):
    site_name : list = url.split("/")[2].split(".")
    if "www" in site_name:
        site_name.remove("www")
    site_name = site_name[0]

    downloaders = {
        "javtiful": javtifull.process_url,
        "livegore": livegore.process_url,
        "missav": missav.process_url,
        "playvids": playvids.process_url,
        "crazyshit": crazyshit.process_url
    }

    for key, downloader in downloaders.items():
        if key == site_name:
            print(f"Matched downloader for {site_name}")
            return downloader
        
    return None

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
        downloader = get_downloader(args.url)
        if downloader:
            downloader(args.url, output_folder)
        else:
            print(f"No downloader found for URL: {args.url}")

    elif args.batch:
        try:
            with open(os.path.abspath(args.batch), "r") as f:
                urls = [line.strip() for line in f if line.strip()]
                for url in urls:
                    downloader = get_downloader(url)
                    if downloader:
                        downloader(url, output_folder)
                    else:
                        print(f"No downloader found for URL: {url}")
                    
        except Exception as e:
            print(f"Failed to read batch file: {e}")

    else:
        print("bruh give me -u or -b")

if __name__ == "__main__":
    main()