import base64
import requests

#?q_string=american&q_imdb=tt13496236

link_bytes = "https://123movies.navy/american-siege/152076/".encode('ascii')
print(str(base64.b64encode(link_bytes).decode("utf-8"))+"?q_string=american-siege&q_imdb=tt0815241")

print(str(base64.b64decode("aHR0cHM6Ly8xMjNtb3ZpZXMxMjMuY2MvbW92aWUvYW1lcmljYW4tc2llZ2UtMjAyMi54eWs=").decode("utf-8")))

r = requests.get("https://fmovies.to/movie/fireheart-0m98r/1-full")
print(r.json())

'''f = open("movies.html", "r")
read_movies = f.read()
f.close()

f = open("Knowncyberlockers.txt", "r")
read_lockers = f.read()
f.close()

#print(read_lockers.split())

for i in read_lockers.split():
    for j in read_movies.split():
        if i.split(".")[0] in j:
            print(i)'''


'''f = open("CyberlockerPerpRecordKeeper.csv", "r")
read_lockers = f.read()
f.close()
f = open("movies_links.txt", "a")
for i in read_lockers.split():
    if len(i.split()[0].split(',')) > 2:
        print(i.split()[0].split(','))
        f.write(i.split()[0].split(',')[3] + "\n")

f.close()'''


# # # cleaning for short links # # #
'''f = open("text_files/potential_cyberlockers.txt", "r")
read_lockers = f.read().splitlines()
f.close()
check_list = []
for i in read_lockers:
    if i not in check_list and "NOTHING" not in i and "Error" not in i:
        check_list.append(i)
print(len(check_list))

t = open("potential_cyberlockers2.txt", "a")
for i in check_list:
    t.write(str(i)+"\n")

t.close()'''


# # # cleaning 1 for full rls # # #
'''f = open("text_files/potential_cyberlockers_full_urls.txt", "r")
read_lockers = f.read().splitlines()
f.close()
check_list = []
for i in read_lockers:
    for j in i.split('"'):
        if j not in check_list and "NOTHING" not in i and "Error" not in i:
            check_list.append(j)
print(len(check_list))

t = open("full_urls.txt", "a")
for i in check_list:
    t.write(str(i)+"\n")

t.close()'''


# # # cleaning 2 for full rls # # #
'''trash_symbols = (
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
        "wts.one", "remotefilez", "liveschauen", "cover", "background", ".png", ".jpg", "paypal",
        )
f = open("text_files/full_urls.txt", "r")
read_lockers = f.read().splitlines()
f.close()
check_list = []
for i in read_lockers:
    checker = 0
    for j in trash_symbols:
        if j in i:
            checker += 1
            continue
    if checker == 0 and "http" in i:
        check_list.append(i)

print(len(check_list))
t = open("text_files/full_urls_clean3.txt", "a")
for i in check_list:
    t.write(str(i)+"\n")

t.close()'''

# # # count how many cyberlocker urls were fond # # #

'''f = open("text_files/Knowncyberlockers.txt", "r")
read_true_lockers = f.read().splitlines()
f.close()
f = open("text_files/full_urls_clean.txt", "r")
read_poten_lockers = f.read().splitlines()
f.close()
count_lc = 0

for i in read_true_lockers:
    for j in read_poten_lockers:
        if i.split()[0] in j:
            count_lc +=1

print(count_lc)'''
