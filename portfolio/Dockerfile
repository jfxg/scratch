FROM node:22-alpine

WORKDIR /app

# Install dependencies first (layer cached until package.json changes)
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# Copy everything
COPY server.js ./
COPY src/ ./src/
COPY public/ ./public/
COPY content/ ./content/
COPY data/ ./data/

EXPOSE 3000

CMD ["node", "server.js"]
