FROM node:latest as build

WORKDIR /src/gingko-web

COPY package.json .

RUN yarn

COPY . .

RUN yarn build

FROM caddy:latest

COPY --from=build /src/gingko-web/dist /gingko

ENTRYPOINT [ "caddy", "file-server", "--listen", ":80", "--root", "/gingko" ]