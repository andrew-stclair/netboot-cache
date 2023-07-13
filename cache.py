"""Build the nginx config using the json file"""
import json
#import requests

config = json.loads(open("cache.json", encoding="utf-8").read())

# This makes netboot fail
# MENUVER = requests.get(
#     "https://api.github.com/repos/netbootxyz/netboot.xyz/releases/latest",
#     timeout=15).json()['tag_name']
# config['locations']['/sigs/'] = f"http://boot.netboot.xyz/{MENUVER}/sigs/"

NGINX_CONFIG = "user nginx;\n"
NGINX_CONFIG += "worker_processes auto;\n"
NGINX_CONFIG += "pcre_jit on;\n"
NGINX_CONFIG += "error_log  /var/log/nginx/error.log warn;\n"
NGINX_CONFIG += "pid        /var/run/nginx.pid;\n"
NGINX_CONFIG += "events {\n"
NGINX_CONFIG += "        worker_connections 1024;\n"
NGINX_CONFIG += "}\n"
NGINX_CONFIG += "http {\n"
NGINX_CONFIG += "    include       /etc/nginx/mime.types;\n"
NGINX_CONFIG += "    default_type  application/octet-stream;\n"
NGINX_CONFIG += "    log_format  main  '$remote_addr - $remote_user [$time_local] \"$request\" '\n"
NGINX_CONFIG += "                      '$status $body_bytes_sent \"$http_referer\" '\n"
NGINX_CONFIG += "                      '\"$http_user_agent\" \"$http_x_forwarded_for\"';\n"
NGINX_CONFIG += "    access_log  /var/log/nginx/access.log  main;\n"
NGINX_CONFIG += "    sendfile        on;\n"
NGINX_CONFIG += "    #tcp_nopush     on;\n"
NGINX_CONFIG += "    keepalive_timeout  65;\n"
NGINX_CONFIG += "    gzip on;\n"
NGINX_CONFIG += "    proxy_force_ranges on;\n"
NGINX_CONFIG += f"    proxy_cache_path /cache levels=1:2 keys_zone=cache:{config['cache_zone_size']} max_size={config['cache_max_size']} inactive=900m use_temp_path=off;\n"
NGINX_CONFIG += "    server {\n"

for location in config['locations']:
    NGINX_CONFIG += f"        sub_filter {config['locations'][location]} {location};\n"

NGINX_CONFIG += "        sub_filter_once off;\n"
NGINX_CONFIG += "        access_log on;\n"
NGINX_CONFIG += "        add_header Cache-Control \"public\";\n"

for location in config['locations']:
    NGINX_CONFIG += f"        location {location} {{\n"
    NGINX_CONFIG += "            resolver 1.1.1.1 valid=60s;\n"
    NGINX_CONFIG += f"            proxy_pass {config['locations'][location]};\n"
    NGINX_CONFIG += "            proxy_cache cache;\n"
    NGINX_CONFIG += "            proxy_read_timeout 120s;\n"
    NGINX_CONFIG += "            proxy_intercept_errors on;\n"
    NGINX_CONFIG += "            proxy_cache_revalidate on;\n"
    NGINX_CONFIG += "            proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;\n"
    NGINX_CONFIG += "            proxy_cache_background_update on;\n"
    NGINX_CONFIG += "            proxy_cache_lock on;\n"
    NGINX_CONFIG += "            error_page 301 302 307 = @handle_redirects;\n"
    NGINX_CONFIG += "        }\n"

NGINX_CONFIG += "        location @handle_redirects {\n"
NGINX_CONFIG += "            resolver 1.1.1.1;\n"
NGINX_CONFIG += "            set $saved_redirect_location '$upstream_http_location';\n"
NGINX_CONFIG += "            proxy_pass $saved_redirect_location;\n"
NGINX_CONFIG += "        }\n"

NGINX_CONFIG += "        proxy_hide_header Cache-Control;\n"
NGINX_CONFIG += "        proxy_hide_header Content-Security-Policy;\n"
NGINX_CONFIG += "        proxy_hide_header X-GitHub-Request-Id;\n"
NGINX_CONFIG += "    }\n"
NGINX_CONFIG += "}\n"
NGINX_CONFIG += "\n"

NGINX_CONFIG_FILE = open("config/nginx.conf", "w", encoding="utf-8")
NGINX_CONFIG_FILE.write(NGINX_CONFIG)
NGINX_CONFIG_FILE.close()
