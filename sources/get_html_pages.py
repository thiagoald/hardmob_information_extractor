""" GETs NUMBER_OF_PAGES from http://www.hardmob.com.br/promocoes """

import codecs
import os
import time
import functools
import multiprocessing
import requests

def save_page(index_, folder_):
    """ GETs the 'index' page from hardmob and saves in a file in 'folder' """
    status = None
    if not os.path.exists(os.path.join(folder_, 'page{}.html'.format(index_))):
        # print 'GET', 'http://www.hardmob.com.br/promocoes/index{}.html'.format(index_)
        req = requests.get('http://www.hardmob.com.br/promocoes/index{}.html'.format(index_))
        # print 'Encoding:', req.encoding
        # print 'Writing to file "hardmob/page{}.html"...'.format(index_)
        with codecs.open(os.path.join(folder_, 'page{}.html'.format(index_)), 'w+', encoding=req.encoding) as file_:
            file_.write(req.text)
        status = (index_, 'fetched')
    else:
        status = (index_, 'in cache')
    return status


def main():
    """ Main """
    NUMBER_OF_PAGES = 10
    HTML_FOLDER = reduce(os.path.join, ['..', 'resources', 'html'], '')
    NUMBER_OF_THREADS = 4

    if not os.path.exists(HTML_FOLDER):
        os.mkdir(HTML_FOLDER)
    pool = multiprocessing.Pool(NUMBER_OF_THREADS)
    result = pool.map_async(functools.partial(save_page, folder_=HTML_FOLDER),
                            range(1, NUMBER_OF_PAGES+1))
    pool.close()
    while not result.ready():
        print "Number of HTML files left: {}".format(result._number_left)
        time.sleep(1)
    pool.join()
    for status in result.get():
        print status


if __name__ == '__main__':
    main()
