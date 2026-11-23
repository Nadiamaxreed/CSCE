from pathlib import Path
import json,re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];dist=root/'dist';checked=0;faqs=0
for p in dist.rglob('*.html'):
 if not p.is_file():continue
 s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 for tag in s.select('a[href],img[src],script[src],link[href]'):
  u=tag.get('href') or tag.get('src');part=urlsplit(u)
  if part.scheme or part.netloc or not part.path:continue
  target=dist/unquote(part.path.lstrip('/')) if part.path.startswith('/') else p.parent/unquote(part.path)
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(p,u)
 if s.find('meta',attrs={'http-equiv':re.compile('refresh',re.I)}):continue
 assert len(s.select('link[rel=canonical]'))==1,p
 assert s.title and s.title.get_text(strip=True),p
 assert s.find('meta',attrs={'name':'description'}),p
 assert s.find('meta',attrs={'property':'og:image'}),p
 for tag in s.select('script[type="application/ld+json"]'):
  data=json.loads(tag.string or tag.get_text())
  nodes=data.get('@graph',[data])
  for node in nodes:
   if node.get('@type')=='FAQPage':
    faqs+=len(node['mainEntity'])
    for question in node['mainEntity']:
     normalize=lambda x:re.sub(r'\s+','',x)
     visible=normalize(s.get_text())
     assert normalize(question['name']) in visible,(p,question['name'])
     assert normalize(question['acceptedAnswer']['text']) in visible,(p,question['name'])
 checked+=1
for p in dist.glob('sitemap*.xml'):
 tree=ET.fromstring(p.read_bytes())
 for loc in tree.findall('.//{*}loc'):
  u=urlsplit(loc.text);assert u.scheme=='https'
  if loc.text.endswith('.xml'):continue
  target=dist/unquote(u.path.lstrip('/'))
  if target.is_dir():target=target/'index.html'
  assert target.exists(),loc.text
  s=BeautifulSoup(target.read_text(encoding='utf8'),'html.parser')
  assert not s.find('meta',attrs={'http-equiv':re.compile('refresh',re.I)}),loc.text
  assert not any('noindex' in tag.get('content','') for tag in s.select('meta[name=robots]')),loc.text
assert faqs>=5
print(json.dumps({'checkedPages':checked,'verifiedFaqAnswers':faqs,'brokenResources':0}))

