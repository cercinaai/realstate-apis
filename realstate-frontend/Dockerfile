# Étape 1 : Build de l'application Angular
FROM node:18 AS build
WORKDIR /app

# Utiliser l'utilisateur root pour installer les dépendances globales
USER root

# Copie les fichiers de dépendances
COPY package*.json ./

# Installe les dépendances et Angular CLI globalement
RUN npm install -g @angular/cli@17.3.8 && npm install

# Copie le reste des fichiers
COPY . .

# Construit l'application Angular
RUN ng build --configuration production

# Étape 2 : Servir avec Nginx
FROM nginx:alpine
COPY --from=build /app/dist/realstate-frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]