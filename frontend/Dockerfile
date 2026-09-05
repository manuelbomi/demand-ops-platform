# Dev-mode Dockerfile: runs `next dev` so the container matches what a
# developer sees locally. A production image would instead run
# `next build && next start` (or export a static build) behind a
# reverse proxy -- see the "Taking this further" section in the README.
FROM node:20-alpine

WORKDIR /app
COPY package.json .
RUN npm install

COPY . .

ENV BACKEND_URL=http://backend:8000
EXPOSE 3000
CMD ["npm", "run", "dev"]
