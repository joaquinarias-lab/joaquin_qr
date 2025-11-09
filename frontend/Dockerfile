# Etapa 1: Construcción
FROM node:18 AS build

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY package*.json ./

# Instalar dependencias (forzando resolución de peer dependencies)
RUN npm install --legacy-peer-deps

# Copiar todo el proyecto
COPY . .

# Construir la aplicación para producción (usa vite, react-scripts o lo que corresponda)
RUN npm run build

# Etapa 2: Servidor web con Nginx
FROM nginx:alpine

# Copiar los archivos generados a la carpeta de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
