ARG TAG=latest
FROM alpine:${TAG}
RUN mkdir -p /cache; apk add --no-cache nginx
COPY ./config/nginx.conf /etc/nginx/nginx.conf
VOLUME [ "/cache" ]
EXPOSE 80
ENTRYPOINT [ "nginx", "-g", "daemon off;" ]
