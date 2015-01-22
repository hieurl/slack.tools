import websocket
import thread
import time
import requests
import json
import re
import urllib

global token, start_url, blocked_list
blocked_list=["sex","xxx","porn","thiendia", "jav", "18+"]

# SLACK TOKEN REQUIRED
token=""

start_url="https://slack.com/api/rtm.start?token="

def go_google(query):
    query=query.strip("<>{}[]")
    query=re.sub(r'http[s]*://[^\|]*\|','',query)
    query=re.sub(r'\s+','+',query)
    g_url="http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="
    res=requests.get(g_url+query)
    res=res.json()
    return res['responseData']['results']

def on_message(ws, message):
    try:
        msg=json.loads(message)

        res_msg={}
        if msg['type']=="message" and re.search(r'^gg\s', msg['text']):
            print message
            query=re.sub('^gg\s','',msg['text'])
            res_msg['type']="message"
            res_msg['channel']=msg['channel']
            res_msg['ts']=time.time()
            res_msg['text']="<@"+msg['user']+">: \n```"
            gg=go_google(query)
            if len(gg) == 0:
                res_msg['text']+="Google is dumb. Cannot search your\
                        query\n (or maybe YOU are dumb)```\n"
            else:
                gg=gg[0]
                if any(x in gg['content'].lower() for x in\
                        blocked_list):
                    res_msg['text']+="Content is NSFW\n```\n"
                else:
                    res_msg['text']+=gg['unescapedUrl']+"\n"
                    res_msg['text']+=gg['content']+"\n"
                    res_msg['text']+="```\n"
            res_msg['text']+="`This is an automatic message. This user does not take any responsible for this content`\n"
            print res_msg['text']

            #res_msg['text']="```\n GET BACK TO WORK! \n```"
            ws.send(json.dumps(res_msg))
    except Exception as e:
        print e
        pass


def on_close(ws):
    print "closed"

def on_error(ws, error):
    print error

def on_open(ws):
    def run(*args):
        while(True):
            time.sleep(3)
            ws.send('{"id":1, "type":"ping"}')

    thread.start_new_thread(run, ())

if __name__=="__main__":
    res=requests.get(start_url+token)
    url=res.json()['url']

    websocket.enableTrace(True)
    ws=websocket.WebSocketApp(url, on_message=on_message,
            on_error=on_error, on_close=on_close)
    ws.on_open=on_open
    ws.run_forever()
