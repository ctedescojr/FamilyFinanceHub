# Frontend Dockerfile - React + Vite + Tailwind CSS 4.1

# Estágio de desenvolvimento
FROM node:24-alpine as development

WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY . .

# Expor porta de desenvolvimento
EXPOSE 5173

# Comando de desenvolvimento com hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Estágio de build para produção
FROM node:18-alpine as build

WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências incluindo devDependencies para build
RUN npm ci

# Copiar código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Estágio de produção com nginx
FROM nginx:alpine as production

# Copiar configuração personalizada do nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos buildados
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar script de inicialização para variáveis de ambiente em runtime
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expor porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Entrypoint para injetar variáveis de ambiente em runtime
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]