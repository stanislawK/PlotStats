FROM node:20-slim

RUN npm install -g pnpm
COPY ./frontend/package*.json ./frontend/next.config.js ./frontend/pnpm-lock.yaml ./frontend/tsconfig.json /frontend/
WORKDIR /frontend
RUN pnpm install

COPY ./frontend /frontend/

EXPOSE 4200

CMD pnpm run dev