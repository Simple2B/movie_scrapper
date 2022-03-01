import os
import time
from .ms_scrapper import scrapper  # get_pages
from .ms_parser import get_link  # , filter_potential_cyberlockers
from app.config import settings


text_files_path = str(os.path.join(settings.BASE_DIR, "scrapper/text_files/"))


def write_links(urls_list):
    start_time = time.time()
    print(">>>>>>>>>>>>>> Parser start time: ", time.localtime())
    sites_count = 0
    read_lockers = urls_list
    f = open(text_files_path+"potential_cyberlockers.txt", "w")
    pcfu = open(text_files_path+"potential_cyberlockers_full_urls.txt", "w")

    for website in read_lockers:
        if len(website.split("/")[2].split(".")) >= 3:
            website_name = website.split("/")[2].split(".")[1]
        else:
            website_name = website.split("/")[2].split(".")[0]

        print(f"{sites_count} website of this launch: {website_name}")
        print(website)
        scrapper_response = scrapper(website)  # get_pages(website)
        if scrapper_response is False:
            err = f"TIMEOT ocured when scrapping {website}\n"
            f.write(err)
            pcfu.write(err)
            continue
        else:
            potential_links = get_link(text_files_path+"movies.html", website_name)
            print(potential_links[0], "\n", len(potential_links[0]))
            print(potential_links[1], "\n", len(potential_links[1]))

            if len(potential_links[0]) == 0:
                f.write(f"NOTHING FOUND => {website}\n")
            elif len(potential_links[0]) == 1 and "cloudflare" in potential_links[0][0]:
                f.write(f"CLOUDFLARE BLOCK => {website}\n")
            else:
                for i in potential_links[0]:
                    f.write(str(i)+"\n")

            if len(potential_links[1]) == 0:
                pcfu.write(f"NOTHING FOUND => {website}\n")
            elif len(potential_links[1]) == 1 and "cloudflare" in potential_links[1][0]:
                pcfu.write(f"CLOUDFLARE BLOCK => {website}\n")
            else:
                for i in potential_links[1]:
                    pcfu.write(str(i)+"\n")

    f.close()
    pcfu.close()
    sites_count += 1
    print(">>>>>>> Scrapping and writing finished in: ", time.time() - start_time)
    return potential_links[1]


if __name__ == "__main__":
    write_links([
        "https://123movies.navy/american-siege/152076/",
        ])
