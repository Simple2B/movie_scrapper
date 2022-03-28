import base64

link_bytes = "https://123movies.navy/american-siege/152076/".encode("ascii")
print(str(link_bytes))
print(str(base64.b64encode(link_bytes).decode("utf-8")))
