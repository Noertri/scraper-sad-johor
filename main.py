from httpx import Client
from bs4 import BeautifulSoup
from urllib import parse
import time
from dataclasses import dataclass, asdict
import re
from datetime import datetime
import os
import csv
import itertools


client = Client(follow_redirects=True, timeout=10.)
main_url = "https://dewannegeri.johor.gov.my"


@dataclass
class Result:
    name: str = ""
    position:  str = "Member of the State Legislative Assembly (Ahli Dewan Undangan Negeri) | State Legislative Assembly (Dewan Undangan Negeri), Johor"
    address: str = ""
    phone_number: str = ""
    fax_number: str = ""
    email: str = ""
    photo_url: str = ""


def request_main_page(url):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6,ja;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://dewannegeri.johor.gov.my/sad/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    
    response = client.get(parse.urljoin(main_url, url), headers=headers)

    return response


def request_page(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6,ja;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = client.get(url, headers=headers)

    return response


def scraper(num_pages):
    results = []
    fax_phone_pattern = re.compile(r"No\..*:\s?(.*)")
    k = itertools.count(start=1, step=1)

    for page in range(1, num_pages+1):
        page_url = f"sad/?wpv_view_count=1136-TCPID24&wpv-wpcf-nama=&wpv-wpcf-kawasan-dun=&wpv-wpcf-parti=&wpv_paged={page}"
        r = request_main_page(page_url)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("#wpv-view-layout-1136-TCPID24 #et-boc .et-last-child p>a")
        if links:
            for link in links:
                name = link.get_text(strip=True, separator=" ")
                result = Result(name=name)
                href = link.get("href")
                if href:
                    r2 = request_page(href)
                    time.sleep(3)
                    soup2 = BeautifulSoup(r2.text, "html.parser")
                    addr = soup2.select_one("div#et-boc .et_pb_text_1 p:nth-child(2)")
                    phone = phone.get_text(strip=True, separator=" ") if (phone := soup2.select_one("div#et-boc .et_pb_text_2 p")) is not None else ""
                    fax = fax.get_text(strip=True, separator=" ") if (fax := soup2.select_one("div#et-boc .et_pb_text_3 p")) is not None else ""
                    email = email.get_text(strip=True, separator=" ") if (email := soup2.select_one("div#et-boc .et_pb_text_4 p a")) is not None else ""
                    photo = photo.get("src", "") if (photo := soup2.select_one("div#et-boc div.et_pb_image_0 img")) is not None else ""

                    result.address = addr.get_text(strip=True, separator=" ") if addr is not None else ""
                    result.phone_number = match_phone.group(1) if (match_phone := fax_phone_pattern.match(phone)) else ""
                    result.fax_number = match_fax.group(1) if (match_fax := fax_phone_pattern.match(fax)) else ""
                    result.email = email
                    result.photo_url = photo

                results.append(asdict(result))

                print(f"[{next(k)}] Success!!! : {result.name}")

    return results


if __name__ == "__main__":
    print("Start to scrape web...")
    results = scraper(6)
    filename = "ADUN_Johor_{0}.csv".format(datetime.now().strftime("%d%m%Y%H%M%S"))
    print(f"Save to hasil/{filename}")
    try:
        with open(os.path.join("hasil", filename,), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("name", "position", "address", "phone_number", "fax_number", "email", "photo_url"), delimiter=";")
            writer.writeheader()
            writer.writerows(results)
            f.close()
            print("Done...")
    except Exception as err:
        print(f"{err}")
