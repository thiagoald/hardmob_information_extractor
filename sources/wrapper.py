""" Extracts metadata from posts in the HTML pages. """
import os
import time
import codecs
import multiprocessing
import simplejson as json
import bs4
import regex
import requests

def extract_data_from_html(file_path):
    offers = []
    soup = None
    with codecs.open(file_path, 'r', encoding='ISO-8859-1') as file_:
        soup = bs4.BeautifulSoup(file_.read(), 'html.parser')

    page_items = soup.find_all('li', {'class':'sprite_statusicon_thread_30 threadbit '})
    for item in page_items:
        offer = {}
        offer['title'] = item.find('a', {'class':'title'}).get_text()
        offer['hardmob_link'] = item.find('a', {'class':'title'})['href']
        offer['external_links'] = []

        # Finding prices
        price_candidates = []
        for match in regex.finditer(r"(( (R\$|RS|Rs|r\$|rS|rs|$|U\$)\s*\d+(\.\d\d\d)*(,\d\d)?(^\p{L}$)?)" +
                                    r"|(\s+\d+(\.\d\d\d)*(,\d\d)?(^\p{L}$)?))",
                                    offer['title']):
            price_candidate = {'string':match.group(0),
                               'likelihood':0}
            # More likely to be a price if...

            # Has 'R$' at the beginning
            if match.group(3) is not None:
                price_candidate['likelihood'] = price_candidate['likelihood'] + 2

            # Has a comma followed by two numbers in the end (,XX)
            if (match.group(5) is not None) or (match.group(8) is not None):
                price_candidate['likelihood'] = price_candidate['likelihood'] + 1
            price_candidates.append(price_candidate)

        offer['prices'] = []
        if price_candidates != []:
            top_likelihood = sorted(price_candidates,
                                    key=lambda item: item['likelihood'],
                                    reverse=True)[0]['likelihood']
            offer['prices'] = [price['string']
                               for price in price_candidates
                               if price['likelihood'] == top_likelihood]
        offers.append(offer)
    folder_path = file_path.split('.html')[0]
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    for i, offer in enumerate(offers):
        print codecs.encode(offer['title'], 'utf-8')
        
        # Cache offer pages if needed
        if not os.path.exists(os.path.join(folder_path, 'offer{}.html'.format(i))):
            req = requests.get(offer['hardmob_link'])
            with codecs.open(os.path.join(folder_path, 'offer{}.html'.format(i)), 'w+', encoding=req.encoding) as file_:
                file_.write(req.text)
                source_text = req.text
        else:
            source_text = codecs.open(os.path.join(os.path.join(folder_path, 'offer{}.html'.format(i))), 'r', encoding='ISO-8859-1').read()
        try:
            soup = bs4.BeautifulSoup(source_text, 'html.parser')
            first_post = soup.find('div', {'class':'postrow'})
            for link in first_post.find_all('a'):
                offer['external_links'].append(link['href'])
        except Exception as e:
            print('Could not find an external link for this offer!')

    return offers

def main():
    NUMBER_OF_THREADS = 4
    HTML_FOLDER = reduce(os.path.join, ['..', 'resources', 'html'])
    OUTPUT_FILE = reduce(os.path.join, ['..', 'resources', 'output.json'])

    if os.path.exists(HTML_FOLDER):
        files_paths = []
        for root, dirs, files in os.walk(HTML_FOLDER):

            for file_name in files:
                _, extension = os.path.splitext(file_name)
                is_page = (file_name.find('page') != -1)
                if extension == '.html' and is_page:
                    files_paths.append(os.path.join(root, file_name))
        # Sequential
        # offer_list = reduce(lambda l1, l2: l1 + l2, map(extract_data_from_html, files_paths))

        # # Parallel
        pool = multiprocessing.Pool(NUMBER_OF_THREADS)
        results = pool.map_async(extract_data_from_html, files_paths)
        pool.close()
        while not results.ready():
            print "Number of HTML files left: {}".format(results._number_left)
            time.sleep(1)
        pool.join()
        offer_list = reduce(lambda l1, l2: l1 + l2, results.get())
        offer_list = offer_list[0:300]
        # for offer in offer_list:
        #     print codecs.encode(offer['title'], 'utf-8')

        with codecs.open(OUTPUT_FILE, 'w+', encoding='utf-8') as file_:
            json.dump(offer_list, file_, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        print HTML_FOLDER + ' does not exist!'


if __name__ == '__main__':
    main()
