"""Publish static dist to the independent Jinan catering exhibition site; retain release and config backups."""
from pathlib import Path
import subprocess,hashlib,json,tarfile,datetime,os
R=Path(__file__).resolve().parents[1]
STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
KEY=str(Path.home()/'.ssh/hm_ts_deploy_ed25519')
HOST='root@118.89.192.96';DOMAIN='csce.hm-d.cn'
archive=R/'.astro'/f'csce-{STAMP}.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for p in (R/'dist').rglob('*'):
  if p.is_file():t.add(p,arcname=p.relative_to(R/'dist').as_posix(),recursive=False)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
ssh=['ssh','-i',KEY,'-o','BatchMode=yes','-o','ConnectTimeout=15',HOST]
def remote(script):
 subprocess.run(ssh+['bash','-s'],input=script.replace('\r\n','\n').encode('utf8'),check=True)
subprocess.run(['scp','-i',KEY,'-o','BatchMode=yes',str(archive),HOST+':/root/'+archive.name],check=True)
script=r'''set -eu
STAMP=__STAMP__
DOMAIN=csce.hm-d.cn
ROOT=/www/wwwroot/csce.hm-d.cn
RELEASE=/www/wwwroot/csce.hm-d.cn-releases/$STAMP
BACKUP=/root/csce-backups/$STAMP
CONF=/www/server/panel/vhost/nginx/csce.hm-d.cn.conf
mkdir -p "$BACKUP" "$RELEASE" /www/wwwroot/csce-acme
sha256sum /www/server/panel/vhost/nginx/jnxz.hm-d.cn.conf /www/server/panel/vhost/nginx/syxz.hm-d.cn.conf /www/server/panel/vhost/nginx/ts.hm-d.cn.conf /www/server/panel/vhost/nginx/t.hm-d.cn.conf > "$BACKUP/other-sites.sha256"
[ ! -e "$CONF" ] || cp -a "$CONF" "$BACKUP/nginx.conf"
if [ -L "$ROOT" ]; then cp -a "$ROOT" "$BACKUP/site-entry"; elif [ -e "$ROOT" ]; then echo 'Existing site root is not a symlink; preserve and inspect it first.'; exit 1; fi
printf '%s  %s\n' '__SHA__' '/root/__ARCHIVE__' | sha256sum -c -
tar -xzf /root/__ARCHIVE__ -C "$RELEASE"
test -s "$RELEASE/index.html"
chmod -R a+rX "$RELEASE"
ln -s "$RELEASE" /www/wwwroot/.csce-next-$STAMP
mv -Tf /www/wwwroot/.csce-next-$STAMP "$ROOT"
if [ ! -f /etc/letsencrypt/live/csce.hm-d.cn/fullchain.pem ]; then
cat > "$CONF" <<'NGINX'
server {
 listen 80;
 server_name csce.hm-d.cn;
 root /www/wwwroot/csce.hm-d.cn;
 index index.html;
 location ^~ /.well-known/acme-challenge/ { root /www/wwwroot/csce-acme; default_type text/plain; try_files $uri =404; }
 location / { try_files $uri $uri/ =404; }
}
NGINX
/www/server/nginx/sbin/nginx -t
/www/server/nginx/sbin/nginx -s reload
certbot certonly --webroot -w /www/wwwroot/csce-acme -d csce.hm-d.cn --non-interactive --agree-tos --register-unsafely-without-email --deploy-hook '/www/server/nginx/sbin/nginx -t && /www/server/nginx/sbin/nginx -s reload'
fi
cat > "$CONF" <<'NGINX'
server {
 listen 80;
 server_name csce.hm-d.cn;
 root /www/wwwroot/csce.hm-d.cn;
 location ^~ /.well-known/acme-challenge/ { root /www/wwwroot/csce-acme; default_type text/plain; try_files $uri =404; }
 location / { return 301 https://csce.hm-d.cn$request_uri; }
}
server {
 listen 443 ssl;
 server_name csce.hm-d.cn;
 root /www/wwwroot/csce.hm-d.cn;
 index index.html;
 ssl_certificate /etc/letsencrypt/live/csce.hm-d.cn/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/csce.hm-d.cn/privkey.pem;
 ssl_protocols TLSv1.2 TLSv1.3;
 ssl_session_cache shared:CSCESSL:10m;
 ssl_session_timeout 1d;
 add_header Cache-Control 'no-cache, max-age=0, must-revalidate' always;
 add_header X-Content-Type-Options nosniff always;
 access_log /www/wwwlogs/csce.hm-d.cn.log;
 error_log /www/wwwlogs/csce.hm-d.cn.error.log;
 error_page 404 /404.html;
 gzip on;
 gzip_types text/css application/javascript application/json image/svg+xml;
 location ^~ /.well-known/acme-challenge/ { root /www/wwwroot/csce-acme; default_type text/plain; try_files $uri =404; }
 location / { try_files $uri $uri/ =404; }
 location ^~ /_astro/ { expires 1y; add_header Cache-Control 'public, immutable'; try_files $uri =404; }
 location ^~ /media/optimized/ { expires 7d; add_header Cache-Control 'public'; try_files $uri =404; }
 location ~ /\. { deny all; }
}
NGINX
/www/server/nginx/sbin/nginx -t
/www/server/nginx/sbin/nginx -s reload
sha256sum -c "$BACKUP/other-sites.sha256"
readlink "$ROOT"
systemctl is-enabled certbot.timer
'''.replace('__STAMP__',STAMP).replace('__SHA__',sha).replace('__ARCHIVE__',archive.name)
remote(script)
record={'domain':DOMAIN,'server':'118.89.192.96','release':'/www/wwwroot/csce.hm-d.cn-releases/'+STAMP,'backup':'/root/csce-backups/'+STAMP,'archiveSha256':sha,'archive':archive.name}
(R/'.astro/deployment.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record))
