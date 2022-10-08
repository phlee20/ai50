import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pd = {}

    for key in corpus:
        
        # Equal probability distribution for no outgoing links 
        if corpus[page] == "":
            pd[key] == 1 / len(corpus)
        
        # Split damping factor across links
        elif key in corpus[page]:
            pd[key] = damping_factor / len(corpus[page]) + (1 - damping_factor) / len(corpus)
        else:
            pd[key] = (1 - damping_factor) / len(corpus)

    return pd

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize pagerank dictionary
    pagerank = {key: 0 for key in corpus.keys()}

    # Randomly select start page
    page = random.choice(list(corpus))
    
    for i in range(n):
        pd = transition_model(corpus, page, damping_factor)

        # Choose next page based on probability distribution
        weight = list(pd.values())
        page = random.choices(list(corpus), weights=weight, k=1)[0]
        
        # Add to pagerank
        pagerank[page] += 1

    # Divide sample results by total
    pagerank = {key: value / n for key, value in pagerank.items()}

    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize pagerank dictionary
    n = len(corpus.keys())
    pagerank = {key: 1 / n for key in corpus.keys()}

    while True:

        # Initialize threshold counter
        threshold = 0

        for p in corpus:

            # Initialize second condition sum
            d_sum = 0
            
            for i in corpus:
                
                # Check for page with no links
                if len(corpus[i]) == 0:
                    d_sum += pagerank[i] / len(corpus)
                
                # Check if page p is in page i
                elif p in corpus[i]:
                    d_sum += pagerank[i] / len(corpus[i])
                
            # Calculate new pagerank
            new_pagerank = (1 - damping_factor) / n + damping_factor * d_sum
            
            # Check for value changes under 0.001
            if abs(new_pagerank - pagerank[p]) < 0.001:
                threshold += 1
            
            # Update pagerank
            pagerank[p] = new_pagerank

        # End loop when all pagerank values are under the threshold
        if threshold == len(corpus):
            print(sum(pagerank.values()))
            return pagerank


if __name__ == "__main__":
    main()
