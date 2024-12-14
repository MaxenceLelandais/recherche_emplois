


seen_urls = set()
path_history = "url_glassdoor.txt"
with open(path_history, "r") as file:
    urls = file.read().splitlines()
    print(len(urls))
    seen_urls.update(urls)
    print(len(seen_urls))


path_history = "url_glassdoor2.txt"
with open(path_history, "a") as file:
    for i in seen_urls:
        file.write(i+"\n")
