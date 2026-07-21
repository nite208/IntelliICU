# =====================================================
# IntelliICU Frontend - Production Dockerfile
# =====================================================

# =====================================================
# Stage 1: Build React + Vite Application
# =====================================================

FROM node:20-bookworm-slim AS build

WORKDIR /app

# -----------------------------------------------------
# Vite Production Build Variables
# -----------------------------------------------------
# Railway provides these variables during the Docker
# build. Vite requires VITE_* variables to be available
# when `npm run build` executes.
# -----------------------------------------------------

ARG VITE_API_BASE_URL
ARG VITE_WS_BASE_URL

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_WS_BASE_URL=${VITE_WS_BASE_URL}

# Copy package manifest first.
COPY package.json ./

# Install dependencies inside Linux environment.
# This avoids Windows-generated lockfile issues with
# Linux native optional packages used by Rolldown,
# LightningCSS, etc.
RUN npm install \
    --include=optional \
    --no-audit \
    --no-fund

# Copy complete frontend application.
COPY . .

# Build production Vite application.
# VITE_API_BASE_URL and VITE_WS_BASE_URL are embedded
# into the generated frontend bundle here.
RUN npm run build


# =====================================================
# Stage 2: Production Nginx Server
# =====================================================

FROM nginx:alpine AS production

# Remove default Nginx static content.
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled Vite application.
COPY --from=build /app/dist /usr/share/nginx/html

# Create SPA-compatible Nginx configuration.
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
        try_files $uri =404;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]