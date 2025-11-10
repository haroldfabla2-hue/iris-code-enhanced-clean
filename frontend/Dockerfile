FROM node:18-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 3000

# Comando por defecto
CMD ["npm", "start"]
