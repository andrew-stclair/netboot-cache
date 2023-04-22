import json
import requests

config = json.loads(open("cache.json", encoding="utf-8").read())

MENUVER = requests.get(
    "https://api.github.com/repos/netbootxyz/netboot.xyz/releases/latest",
    timeout=15).json()['tag_name']

config['locations']['/sigs/'] = f"http://boot.netboot.xyz/{MENUVER}/sigs/"

NGINX_CONFIG = "# /etc/nginx/nginx.conf\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "user nginx;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "# Set number of worker processes automatically based on number of CPU cores.\n"
NGINX_CONFIG += "worker_processes auto;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "# Enables the use of JIT for regular expressions to speed-up their processing.\n"
NGINX_CONFIG += "pcre_jit on;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "# Configures default error logger.\n"
NGINX_CONFIG += "error_log /var/log/nginx/error.log warn;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "# Includes files with directives to load dynamic modules.\n"
NGINX_CONFIG += "include /etc/nginx/modules/*.conf;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "# Include files with config snippets into the root context.\n"
NGINX_CONFIG += "include /etc/nginx/conf.d/*.conf;\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "events {\n"
NGINX_CONFIG += "        # The maximum number of simultaneous connections that can be opened by\n"
NGINX_CONFIG += "        # a worker process.\n"
NGINX_CONFIG += "        worker_connections 1024;\n"
NGINX_CONFIG += "}\n"
NGINX_CONFIG += "\n"
NGINX_CONFIG += "http {\n"
NGINX_CONFIG += f"    proxy_cache_path /cache levels=1:2 keys_zone=cache:{config['cache_zone_size']} max_size={config['cache_max_size']} inactive=900m use_temp_path=off;\n"
NGINX_CONFIG += "    server {\n"
NGINX_CONFIG += "        proxy_cache cache;\n"
NGINX_CONFIG += "        proxy_cache_revalidate on;\n"
NGINX_CONFIG += "        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;\n"
NGINX_CONFIG += "        proxy_cache_background_update on;\n"
NGINX_CONFIG += "        proxy_cache_lock on;\n"

for location in config['locations']:
    NGINX_CONFIG += f"        sub_filter {config['locations'][location]} {location};\n"

NGINX_CONFIG += "        sub_filter_once off;\n"
NGINX_CONFIG += "        access_log on;\n"
NGINX_CONFIG += "        add_header Cache-Control \"public\";\n"

for location in config['locations']:
    NGINX_CONFIG += f"        location {location} {{\n"
    NGINX_CONFIG += f"            proxy_pass {config['locations'][location]};\n"
    NGINX_CONFIG += "            proxy_intercept_errors on;\n"
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
