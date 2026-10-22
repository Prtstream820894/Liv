import urllib.parse
import re
import requests

# सोर्स M3U प्लेलिस्ट का URL
SOURCE_URL = "https://vk-playlist.pages.dev/sony.m3u"
OUTPUT_FILE = "new_sony.m3u"

# Custom headers अगर वर्कर या सर्वर को ब्लॉक होने से बचाना हो
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_final_url(url):
    """URL को बैकग्राउंड में ओपन करके उसका फाइनल रीडायरेक्ट लिंक निकालता है।"""
    try:
        # allow_redirects=True से यह आखिरी रीडायरेक्टेड URL तक जाता है
        response = requests.head(
            url, headers=HEADERS, allow_redirects=True, timeout=10
        )
        final_url = response.url

        # अगर HEAD रिक्वेस्ट से 405/403 मिले तो GET से ट्राय करते हैं (stream=True ताकि पूरा डेटा डाउनलोड न हो)
        if response.status_code >= 400:
            response = requests.get(
                url, headers=HEADERS, allow_redirects=True, stream=True, timeout=10
            )
            final_url = response.url
            response.close()

        print(f"[SUCCESS] Original: {url}\n          Final: {final_url}")
        return final_url
    except Exception as e:
        print(f"[ERROR] Could not resolve {url}: {e}")
        return url  # अगर फेल हुआ तो पुराना लिंक ही रख देगा


def process_playlist():
    print(f"Fetching playlist from {SOURCE_URL}...")
    response = requests.get(SOURCE_URL, headers=HEADERS)

    if response.status_code != 200:
        print("Failed to download source M3U playlist!")
        return

    lines = response.text.splitlines()
    new_lines = []

    for line in lines:
        line_str = line.strip()

        # अगर लाइन URL है (http या https से शुरू हो रही है)
        if line_str.startswith("http://") or line_str.startswith("https://"):
            final_stream_url = get_final_url(line_str)
            new_lines.append(final_stream_url)
        else:
            # #EXTM3U या #EXTINF वाली लाइनों को वैसे ही रहने दो
            new_lines.append(line)

    # नई M3U फाइल राइट करें
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    print(f"\nSuccessfully generated {OUTPUT_FILE}!")


if __name__ == "__main__":
    process_playlist()
