import os
from .ms_scrapper import get_pages, scrapper
from .ms_parser import get_link, filter_potential_cyberlockers
from app.config import settings


def write_links(urls_list):
    #f = open("text_files/movies_links.txt", "r")
    #read_lockers = f.read().splitlines()
    read_lockers = urls_list
    #f.close()#
    text_files_path = str(os.path.join(settings.BASE_DIR, "scrapper/text_files/"))
    print(text_files_path)
    f = open(text_files_path+"potential_cyberlockers_full_urls.txt", "w")
    print(f'4 === {os.path.join(settings.BASE_DIR, "scrapper/text_files/potential_cyberlockers_full_urls.txt")}')
    pcfu = open(text_files_path+"potential_cyberlockers_full_urls.txt", "w")

    for website in read_lockers:
        if len(website.split("/")[2].split(".")) >= 3:
            website_name = website.split("/")[2].split(".")[1]
        else:
            website_name = website.split("/")[2].split(".")[0]

        print(website_name)
        print(website)
        #get_pages(website)
        scrapper_response = scrapper(website)
        if scrapper_response == False:
            err = f"Error ocured when scrapping {website}\n"
            f.write(err)
            pcfu.write(err)
            continue
        else:
            potential_links = get_link(text_files_path+"movies.html", website_name)
            filtered_links = filter_potential_cyberlockers(potential_links, website_name)
            print(filtered_links[0], "\n", len(filtered_links[0]))
            
            if len(filtered_links[0]) == 0:
                f.write(f"NOTHING FOUND => {website}\n")
            elif len(filtered_links[0]) == 1 and "cloudflare" in filtered_links[0][0]:
                f.write(f"CLOUDFLARE BLOCK => {website}\n")
            else:
                for i in filtered_links[0]:
                    f.write(str(i)+"\n")
            
            if len(filtered_links[1]) == 0:
                pcfu.write(f"NOTHING FOUND => {website}\n")
            elif len(filtered_links[1]) == 1 and "cloudflare" in filtered_links[1][0]:
                pcfu.write(f"CLOUDFLARE BLOCK => {website}\n")
            else:
                for i in filtered_links[1]:
                    pcfu.write(str(i)+"\n")

    f.close()
    pcfu.close()

if __name__ == "__main__":
    write_links(["https://prmovies.com/american-siege-2021-Watch-online-on-prmovies/"])
