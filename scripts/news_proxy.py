"""Read-only Content Hub proxy. Loopback only, no data cache or token logging."""
import os,json,re,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlencode,urlparse
from urllib.error import HTTPError
TOKEN=os.environ['HM_CONTENT_HUB_TOKEN'];COMPANY=int(os.environ['HM_CONTENT_HUB_COMPANY_ID'])
BASE=os.environ['API_URL'].rstrip('/');SEM=threading.BoundedSemaphore(2)
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): return None
OPENER=build_opener(NoRedirect)
def get(path,**params):
 req=Request(BASE+'/'+path+'?'+urlencode(dict(company_id=COMPANY,**params)),headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/json','Cache-Control':'no-cache'})
 with OPENER.open(req,timeout=20) as r: body=json.load(r)
 if body.get('code')!=0:raise ValueError('upstream business failure')
 return body['data']
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,code,body):
  data=json.dumps(body,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store, max-age=0');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  path=urlparse(self.path).path
  if not SEM.acquire(blocking=False):return self.reply(503,{'error':'新闻服务繁忙，请稍后重试'})
  try:
   if path=='/feed':
    categories=get('news-categories')['items'];items=[];page=1
    while True:
     data=get('news',page=page,per_page=100)
     if data['pagination']['page']!=page:raise ValueError('invalid pagination')
     for item in data['items']:
      if item['company_id']!=COMPANY:raise ValueError('company mismatch')
      items.append(item)
     if page>=data['pagination']['last_page']:break
     page+=1
     if page>1000:raise ValueError('pagination limit')
    self.reply(200,{'categories':categories,'items':items})
   elif re.fullmatch(r'/detail/[0-9a-fA-F-]{36}',path):
    data=get('news/'+path.rsplit('/',1)[1])
    if data['company_id']!=COMPANY:raise ValueError('company mismatch')
    self.reply(200,data)
   else:self.reply(404,{'error':'Not found'})
  except HTTPError as e:self.reply(503 if e.code==429 else 502,{'error':'新闻暂时无法加载，请稍后重试'})
  except Exception:self.reply(502,{'error':'新闻暂时无法加载，请稍后重试'})
  finally:SEM.release()
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',18726),Handler).serve_forever()
