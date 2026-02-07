import re
from urllib.parse import urlparse, urldefrag, urljoin, parse_qs
from bs4 import BeautifulSoup


#GLOBAL DATA VARIABLES
urls_scrapped = set()
urls_seen_including_bad = set()
num_of_each_subdomain = {}
longest_page = {"url":"", "length":0}
word_counter = {}
stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

def normalize_url(url):
    # fragmantise url and gets a parsed url
    url, fragment = urldefrag(url)
    parsed = urlparse(url)
    # get parts of url and makes it lowercase
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    if path.endswith("/index.html"):
        path = path[:-10]
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return scheme + "://" + netloc + path

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
    
    # Check status code - only process 200 OK responses
    if resp.status != 200:
        # if resp.status == 404:
        #     # print(f"[404 Not Found] Skipping: {url}")
        # elif resp.status == 403:
        #     # print(f"[403 Forbidden] Skipping: {url}")
        # elif resp.status >= 600:
        #     # print(f"[Cache Error {resp.status}] Skipping: {url} - {resp.error if resp.error else 'Unknown error'}")
        # else:
        #     # print(f"[Status {resp.status}] Skipping: {url}")
        return list()
    
    # Check for valid response and content
    if not resp.raw_response:
        # print(f"[No Response] Skipping: {url}")
        return list()
    
    if not resp.raw_response.content:
        # print(f"[Empty Content] Skipping: {url}")
        return list()
    
    # Avoid very large files
    content_length = len(resp.raw_response.content)
    MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_CONTENT_SIZE = 100  # 100 bytes
    
    if content_length > MAX_CONTENT_SIZE:
        # print(f"[Too Large] Skipping: {url} (Size: {content_length / (1024*1024):.2f}MB)")
        return list()
    
    # Avoid dead pages with minimal content
    if content_length < MIN_CONTENT_SIZE:
        # print(f"[Too Small] Skipping: {url} (Size: {content_length} bytes)")
        return list()
    
    try:
        html_info = BeautifulSoup(resp.raw_response.content, "html.parser")
        
        # Check for meaningful text content
        text_content = html_info.get_text(strip=True)
        if len(text_content) < 100:
            # print(f"[Low Text Content] Skipping: {url}")
            return list()
        
        # Collect analytics data
        helper_get_data(url, html_info)
        
        # Extract all links from the page
        links = html_info.find_all("a")
        list_of_links = []
        for link in links:
            linkers = link.get("href")
            if linkers:
                combined_link = urljoin(url, linkers)
                defragged_link = urldefrag(combined_link)[0]
                list_of_links.append(defragged_link)
        
        return list_of_links
        
    except Exception as e:
        print(f"[Parse Error] Failed to parse {url}: {e}")
        return list()

def helper_get_data(url, html_info):
    norm_url = normalize_url(url)
    urls_scrapped.add(norm_url)
    # urls_seen_including_bad.add(url)
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
        stripped_word = word.lower().strip(".,?!;:&|/{}[]#")
        if not stripped_word:
            continue
        if stripped_word not in stop_words:
            if stripped_word in word_counter:
                word_counter[stripped_word] += 1
            else:
                word_counter[stripped_word] = 1
    # printer_data()
    #COUNT WORDS

def printer_data():
    words_50 = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)
    print("Number of unique pages: ", len(urls_scrapped))
    print(f"Longest page: {longest_page['url']} that has {longest_page['length']} words")
    print("Number of subdomains: ", len(num_of_each_subdomain))
    print("The top 50 words are: ", words_50[:50])
    print("")

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        norm_url = normalize_url(url)
        if norm_url in urls_scrapped:
            return False
        bad_path_names = ["date", "calendar","year", '/svn/', 'git/', '/wiki/group', '/wiki/public', 'wiki/fr', '/data', '/login'] #maybe change or add more if needed
        domains_that_are_allowed = set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])
        parsed = urlparse(url)
        if norm_url in urls_seen_including_bad:
            return False
        else:
            urls_seen_including_bad.add(norm_url)
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
        if '?' in url:
            qry_param = parsed.query.lower()
            traps = ['tab_details', 'tab_files', 'do=media', 'do=edit', 'image=', 'ical=', 'outlook-ical=', 'eventDisplay=','tribe-bar-date','subpage=','share=', 'c=', 'n=', 'o='] #maybe fix the c n o and add page=
            for x in traps:
                if x in qry_param:
                    return False
        path_checker = parsed.path.lower()
        if 'mailman' in parsed.netloc or 'mailman' in path_checker:
            if any(x in path_checker for x in ['/admin/', '/private/', '/pipermail/']):
                return False
        if '/day/' in path_checker or '/today/' in path_checker:
            return False
        if re.search(r'/\d{4}[-/]\d{2}[/-]\d{2}',path_checker):
            return False
        if re.search(r'/\d{4}[/-]\d{2}',path_checker):
            return False
        if re.fullmatch(r'/\d+', path_checker):
            return False
        if '/events/category/' in path_checker:
            if any(x in path_checker for x in ['/month', '/list']):
                return False
        if 'gitlab.ics.uci.edu' in parsed.netloc:
            if '/-/' in parsed.path:
                return False
        if '/page/' in parsed.path:
            page_num = re.search(r'/page/(\d+)', parsed.path)
            if page_num:
                page_val = int(page_num.group(1))
                if page_val > 5:
                    return False
        if 'tribe-events' in parsed.query:
            if 'paged=' in parsed.query:
                return False
        if 'eventDisplay=' in parsed.query.lower():
            return False
        if 'doku.php' in parsed.path:
            if 'idx' in parse_qs(parsed.query):
                return False
            po = parsed.path + parsed.query
            if po.count(':') > 3:
                return False
        for bad in bad_path_names:
            if bad in path_checker:
                return False
        #add the checker for calendar and other things that may trap crawler
        directory_paths = parsed.path
        #shouldnt be paths w a/b/c/a/s/d.com too MANYYY
        if directory_paths.count("/") > 15:
            return False
        if len(directory_paths) > 150:
            return False
        if 'wp-login.php' in path_checker:
            return False
        if re.search(r'/publications/r\d+[a-zA-z]?\.html$', parsed.path):
            get_path = re.search(r'r(\d+)', parsed.path)
            if get_path:
                num = int(get_path.group(1))
                if num >10:
                    return False
        #maybe come back and add more checking if we fail tests??
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mpg|mpeg"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|scm|rkt|ss|py"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    


    except TypeError:
        print ("TypeError for ", parsed)
        raise
