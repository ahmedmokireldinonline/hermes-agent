FROM node:20-bookworm-slim
WORKDIR /crawler
COPY package.json .
RUN npm install --omit=dev && npx playwright install --with-deps chromium
COPY index.js .
CMD ["npm", "start"]
