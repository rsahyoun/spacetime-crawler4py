import re
from urllib.parse import urlparse

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
    return list()

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
