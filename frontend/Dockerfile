# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build argument
ARG NG_APP_API_URL

# Make it available to Node
ENV NG_APP_API_URL=${NG_APP_API_URL}

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .

RUN npm run build:prod

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist/upsc-study-os/browser /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]