# Étape 1 : Build de l'application Angular
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npx ng build --configuration production

# Étape 2 : Servir avec Nginx
FROM nginx:alpine
COPY --from=build /app/dist/realstate-frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf  
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]