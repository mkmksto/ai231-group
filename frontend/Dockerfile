# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app .
# EXPOSE 4173
EXPOSE 5173
# CMD ["npm", "run", "preview", "--", "--host"]
CMD ["npm", "run", "dev", "--", "--host"]
