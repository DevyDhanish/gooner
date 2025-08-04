VIDEO_URL = "" # given by user
CDN_URL = "https://javtiful.com/ajax/get_cdn"

GET_CDN_PAYLOAD = {
    "video_id": "",
    "pid_c": "",
    "token": ""
}

def submit_video_id(id):
    GET_CDN_PAYLOAD["video_id"] = str(id)

def submit_token(token):
    GET_CDN_PAYLOAD["token"] = str(token)

def get_cdn_header(video_url):
    return {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://javtiful.com",
        "priority": "u=1, i",
        "referer": f"{video_url}",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }