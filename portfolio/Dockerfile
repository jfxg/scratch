FROM node:22-alpine

WORKDIR /app

# Install dependencies first (layer cached until package.json changes)
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# Copy application code
# content/ and data/ are NOT copied — they come in via volume mounts
COPY server.js ./
COPY src/ ./src/
COPY public/ ./public/

EXPOSE 3000

CMD ["node", "server.js"]
