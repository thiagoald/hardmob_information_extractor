from bs4 import BeautifulSoup
import regex
import requests
import json

#run from /hardmob_information_extractor folder (not /source)

def get_comments():
    with open('resources/output.json') as json_data:
        objs = json.load(json_data)
        newobjs = []

        amt = len(objs)

        for obj in objs:
            url = obj['hardmob_link']
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            comments = []
            for content in soup.find_all('blockquote'):
                text = str(content.get_text().encode('utf-8')).strip('\n')
                newtext = ''
                for line in text.split('\n'):
                    if (any(c.isalpha() for c in line)):
                        if ('http' not in line and 'googletag' not in line):
                            newtext += (line + '\n')
                comments.append(newtext.decode('utf-8'))
            obj['comments'] = comments
            newobjs.append(obj)
            print "remaining " + str(amt)
            amt -= 1

        return newobjs

def main():
    newjson = get_comments()
    with open('resources/new_output.json', 'w') as json_file:
        json.dump(newjson, json_file, indent=4, sort_keys=True, ensure_ascii=True)

if __name__ == '__main__':
    main()
