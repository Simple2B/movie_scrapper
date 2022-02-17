import time
import base64


trash_words = (
    "www.google-analytics.com", "www.googletagmanager.com", "schema.org", "www.gstatic.com", "www.w3.org",
    "cdnjs.cloudflare.com", "www.youtube.com", "www.facebook.com", "twitter.com", "api.whatsapp.com", "api.w.org",
    "s.w.org", "s.w.org", "z.moatads.com", "123images.co", "s4.histats.com", "putlocker2021.com", "toglooman.com",
    "cdn.itskiddoan.club", "ipp.littlecdn.com", "whos.amung.us", "image.tmdb.org", "watchomovies.pro", "ogp.me",
    "imagetot.com", "t.me", "cinema4up.tv", "bit.ly", "boldgrid.com", "youradexchange.com", "enterpapp.xyz",
    "schema.org", "s.w.org", "tag", "addthis", "addthisedge", "twitter", "ajax", "google",
    "amazon", "watchomovies.pro", "\\", "\\\\", "solarmovie", "static", "facebook", "youtube", "cloudflare",
    "clarity", "cinema4up", "api", "porno", "img", "pinterest", "reddit", "telegram", "fontawesome", "yandex",
    "123movie", "data-vocabulary", "disqus", "statcounter", "ytimg", "iclickcdn", "rtmark", "jeclittrecheckrep",
    "swellknife", "discovernative", "imdb", "stackpathcdn", "bootstrap", "tynt", "boustahe", "onesignal",
    "jsdelivr", "media.movieassets", "photobucket", "see.kmisln", "cdn.plyr.io", "lucidlydiscretion",
    "actsrelent", "push.monsy", "gmpg.org", "intelligenceadx", "dateddeed", "dozubatan", "pseepsie", "pixel.wp.com",
    "wordpress", "github", "localhost", "jquery", "www.w3.org", "secure", "stats", "image", "patreon", "adskeeper",
    "fayanka", "alexametrics", "c0.wp.com", "gif", "ssl.p.jwpcdn", "histats", "mangareader", "html5rocks",
    "gravitec", "wipeunauthorized", "sendmepush", "dpstream", "ver.acceder", "ja1908", "wts.one", "web-stat",
    "popup", "cloudfront", "html5boilerplate", "yorke-peninsula", "scorecardresearch", "cdn4ads", "ardalio",
    "wts.one", "remotefilez", "liveschauen", "background", ".png", ".jpg", "/svg"  # "cover",
    )

# website_name = "primewire"
# website_name = "cima4up"
# website_name = "putlocker"
# website_name = "moviebb"
# website_name = "prmovies"
# website_name = "solarmovie"
# website_name = "123movies-t"
# website_name = "fmovies"
# website_name = "gowatchseries"
# website_name = "fusionmovies"
base_dir = "/home/linp/simple2b/movie_scrap/scrapper_dev/text_files/"


def get_link(raw_html_file, website_name="fusionmovies"):
    '''
    Parser function. Reads the file and gets a cyberlocker link.
    '''
    potential_cyberlockers = []
    pc_full_urls = []

    start_time = time.time()
    # print(">>>>>>>>>>>>>> Parser start time: ", time.localtime())

    f = open(raw_html_file, "r")
    read_file = f.read()
    f.close()

    t = open(f"{base_dir}potential_cyberlockers_html_parts.txt", "a")  # ## ### write html part ### ## #

    for html_line in read_file.split():
        try:
            if "http:" in html_line or "https:" in html_line:
                # # # find basic links
                http_split_line = html_line.split("/")[2]
                checker = 0
                for trash in trash_words:
                    if trash in html_line or website_name in http_split_line.split("."):
                        checker += 1
                        break
                if checker == 0 and html_line not in pc_full_urls:
                    t.write(str(html_line)+"\n")  # ## ### write html part ### ## #
                    pc_full_urls.append(html_line)
                    potential_cyberlockers.append(http_split_line)
            elif "ase64" in html_line:
                # # # find encoded links
                encoded_html = html_line.split("ase64")[-1].split(")")[0].split("decode")[-1].strip('.,"(')
                try:
                    decoded_html = base64.b64decode(encoded_html)  # .decode("utf-8")
                    if "http" in str(decoded_html):
                        for i in str(decoded_html).split():
                            if "src" in i or "href" in i:
                                decoded_link = i.split('"')[1]
                                print("Encoded link found >>>>>>>>>>>> ", decoded_link)
                                potential_cyberlockers.append(decoded_link)
                    # print(decoded_html, "\n")
                except:
                    print("Fail to decode", "\n")
        except:
            print("Fail to read html", "\n")

    t.close()  # ################## write html part #########################
    print(">>>>>>>>>>>>>> Parser finished in: ", time.time() - start_time)
    return (potential_cyberlockers, pc_full_urls)


def filter_potential_cyberlockers(potential_cyberlockers, website_name):
    to_transform = list(trash_words)
    to_transform.append(website_name)
    trash_symbols = tuple(to_transform)
    print(potential_cyberlockers)
    short_urls = []
    long_urls = []

    for pc in potential_cyberlockers[0]:
        checker = 0
        for trash in trash_symbols:
            if trash in pc:
                checker += 1
                continue
        if checker == 0 and pc not in short_urls:
            short_urls.append(pc)

    for pc in potential_cyberlockers[1]:
        checker = 0
        for trash in trash_symbols:
            if trash in pc:
                checker += 1
                continue
        if checker == 0 and pc not in long_urls:
            long_urls.append(pc)

    '''
    working_list = pc_list
    symbols_counter = 0
    while symbols_counter != len(working_list):
        for symbol in trash_symbols:
            if symbol in working_list[symbols_counter] or symbol in str(working_list[symbols_counter]).split("."):
                #print(working_list[symbols_counter])
                working_list.remove(working_list[symbols_counter])
                if symbols_counter > 0:
                    symbols_counter -= 1

        symbols_counter += 1
        #print(symbols_counter)'''

    print("filter results: ", (short_urls, long_urls))
    return (short_urls, long_urls)


if __name__ == "__main__":
    pass
