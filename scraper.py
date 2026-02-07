import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup


#GLOBAL DATA VARIABLES
urls_scrapped = set()
num_of_each_subdomain = {}
longest_page = {"url":"", "length":0}
word_counter = {}
stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200:
        return list()
    #gets html info bs4 using lxml
    html_info = BeautifulSoup(resp.raw_response.content, "lxml")
    helper_get_data(url, html_info)
    links = html_info.find_all("a")
    list_of_links = []
    for link in links:
        linkers = link.get("href")
        #checks if the href value even stores something
        if linkers:
            #DATA COLLECTIONS
            # helper_get_data(linkers, html_info)
            combined_link = urljoin(url, linkers) #combine the last url with the next url
            defragged_link = urldefrag(combined_link)[0] #returns tuple of the url and the fragment
            list_of_links.append(defragged_link)
    return list_of_links

def helper_get_data(url, html_info):
    urls_scrapped.add(url)
    parsed = urlparse(url)
    sub_d = parsed.netloc
    if sub_d in num_of_each_subdomain:
        num_of_each_subdomain[sub_d] += 1
    else:
        num_of_each_subdomain[sub_d] = 1
    #get_words
    words = html_info.get_text().split()
    #count words
    len_of_words = len(words)
    if len_of_words > longest_page["length"]:
        longest_page["length"] = len_of_words
        longest_page["url"] = url
    #get longest url
    for word in words:
        stripped_word = word.lower().strip(".,?!;:")
        if stripped_word not in stop_words:
            if stripped_word in word_counter:
                word_counter[stripped_word] += 1
            else:
                word_counter[stripped_word] = 1
    printer_data()
    #COUNT WORDS

def printer_data():
    words_50 = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)
    print("Number of unique pages: ", len(urls_scrapped))
    print(f"Longest page: {longest_page['url']} that has {longest_page['length']} words")
    print("Number of subdomains: ", len(num_of_each_subdomain))
    print("The top 50 words are: ", words_50[:50])

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        bad_path_names = ["date", "calendar","year"] #maybe change or add more if needed
        domains_that_are_allowed = set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #this part checks if the domain is ok netloc gets the main part of the url
        checker = False
        # this checks if its act good like its not a fake page
        for x in domains_that_are_allowed:
            if parsed.netloc  == x or parsed.netloc.endswith( "."+x ):
                checker = True
                break
        if not checker:
            return False
        #add the checker for calendar and other things that may trap crawler
        directory_paths = parsed.path
        #shouldnt be paths w a/b/c/a/s/d.com too MANYYY
        if directory_paths.count("/") > 15:
            return False
        if len(directory_paths) > 250:
            return False
        #maybe come back and add more checking if we fail tests??
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
