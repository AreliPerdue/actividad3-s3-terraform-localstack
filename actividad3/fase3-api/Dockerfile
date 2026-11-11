# Versión MITIGADA — base node:18 (Alpine) endurecida.
# Etapa 1: instala solo dependencias de producción con el lockfile exacto.
FROM node:18-alpine AS dependencias
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force

# Etapa 2: imagen final mínima.
FROM node:18-alpine
# Parches del sistema y fuera las herramientas que la app no usa en ejecución
# (npm/npx/yarn y sus dependencias internas son la mayor superficie de CVE de la base).
RUN apk upgrade --no-cache \
 && rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx \
           /opt/yarn-* /usr/local/bin/yarn /usr/local/bin/yarnpkg
WORKDIR /app
ENV NODE_ENV=production
COPY --from=dependencias --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node src ./src
COPY --chown=node:node public ./public
# Usuario sin privilegios
USER node
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s \
  CMD node -e "fetch('http://127.0.0.1:3000/api/salud').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "src/servidor.js"]
