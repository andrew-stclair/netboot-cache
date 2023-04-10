import json

config = json.loads(open("cache.json").read())

nginx_config = f"# /etc/nginx/nginx.conf\n"
nginx_config += f"\n"
nginx_config += f"user nginx;\n"
nginx_config += f"\n"
nginx_config += f"# Set number of worker processes automatically based on number of CPU cores.\n"
nginx_config += f"worker_processes auto;\n"
nginx_config += f"\n"
nginx_config += f"# Enables the use of JIT for regular expressions to speed-up their processing.\n"
nginx_config += f"pcre_jit on;\n"
nginx_config += f"\n"
nginx_config += f"# Configures default error logger.\n"
nginx_config += f"error_log /var/log/nginx/error.log warn;\n"
nginx_config += f"\n"
nginx_config += f"# Includes files with directives to load dynamic modules.\n"
nginx_config += f"include /etc/nginx/modules/*.conf;\n"
nginx_config += f"\n"
nginx_config += f"# Include files with config snippets into the root context.\n"
nginx_config += f"include /etc/nginx/conf.d/*.conf;\n"
nginx_config += f"\n"
nginx_config += f"events {{\n"
nginx_config += f"        # The maximum number of simultaneous connections that can be opened by\n"
nginx_config += f"        # a worker process.\n"
nginx_config += f"        worker_connections 1024;\n"
nginx_config += f"}}\n"
nginx_config += f"\n"
nginx_config += f"http {{\n"
nginx_config += f"    proxy_cache_path /cache keys_zone=cache:{config['cache_zone_size']} max_size={config['cache_max_size']};\n"
nginx_config += f"    server {{\n"
nginx_config += f"        proxy_cache cache;\n"

for location in config['locations']:
    nginx_config += f"        location {location} {{\n"
    nginx_config += f"            proxy_pass {config['locations'][location]};\n"
    nginx_config += f"            proxy_redirect off;\n"
    nginx_config += f"            sub_filter \"{config['locations'][location]}\" \"{location}\";\n"
    nginx_config += f"            sub_filter_once off;\n"
    nginx_config += f"        }}\n"

nginx_config += f"    }}\n"
nginx_config += f"}}\n"
nginx_config += f"\n"

nginx_config_file = open("config/nginx.conf", "w")
nginx_config_file.write(nginx_config)
nginx_config_file.close()
