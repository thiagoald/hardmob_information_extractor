import requests
import json

NL_KEY = '*'
TL_KEY = '*'

def translate(text):
    tmp_payload = {"q": text, "target": "en"}
    s = requests.post('https://translation.googleapis.com/language/translate/v2?key=' + TL_KEY, json=tmp_payload)
    data = s.json()['data']['translations'][0]
    return data['translatedText']

def sentiment(text):
    payload = {"encodingType": "UTF8", "document": {"type": "PLAIN_TEXT", "content": text}}
    r = requests.post('https://language.googleapis.com/v1/documents:analyzeSentiment?key=' + NL_KEY,
        json=payload)
    return r.json()

def generate_sentiments():
    with open('resources/new_output.json') as json_data:
        objs = json.load(json_data)
        newobjs = []

        amt = len(objs)

        for obj in objs:
            comments = obj['comments']
            scores = []
            tot_score = 0
            print "for " + obj['hardmob_link'] + ":"
            try:
                for comment in comments:
                    traducao = translate(comment)
                    sent = sentiment(traducao)
                    score = sent['documentSentiment']['score']
                    scores.append(score)
                    tot_score += score
                obj['scores'] = scores
                obj['avg_score'] = tot_score/int(len(scores))
                newobjs.append(obj)
            except:
                print "error found"
            print "remaining: " + str(amt)
            amt -= 1
        
        return newobjs

def main():
    newjson = generate_sentiments()
    with open('resources/scored_info.json', 'w') as json_file:
        json.dump(newjson, json_file, indent=4, sort_keys=True, ensure_ascii=True)

if __name__ == '__main__':
    main()
