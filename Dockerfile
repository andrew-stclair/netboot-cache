ARG TAG=latest
FROM alpine:${TAG}
RUN apk add --no-cache nginx
