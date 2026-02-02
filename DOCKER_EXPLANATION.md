# 🐳 Explicación de la Dockerización del Proyecto

Este documento detalla cómo se ha containerizado la aplicación para asegurar que funcione exactamente igual en cualquier máquina, eliminando el clásico problema de "en mi máquina funciona".

---

## 1. El Fichero `Dockerfile`

El `Dockerfile` es la "receta" paso a paso para construir la imagen de nuestro contenedor.

```dockerfile
# 1. Imagen Base
FROM python:3.10-slim

# 2. Directorio de Trabajo
WORKDIR /app

# 3. Copia de Dependencias
COPY requirements.txt .

# 4. Instalación de Librerías
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia del Código Fuente
COPY . .

# 6. Puerto
EXPOSE 8501

# 7. Comando de Inicio
CMD ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Desglose paso a paso:

1.  **`FROM python:3.10-slim`**: Empezamos con una versión ligera ("slim") de Linux que ya tiene Python 3.10 instalado. Esto hace que la descarga sea rápida y ocupe menos espacio (~150MB en lugar de 1GB).
2.  **`WORKDIR /app`**: Creamos una carpeta `/app` dentro del contenedor y nos metemos en ella. Todo lo que hagamos a partir de ahora ocurrirá ahí.
3.  **`COPY requirements.txt .`**: Copiamos **solo** el archivo de requisitos primero. ¿Por qué? Para aprovechar la "caché" de Docker. Si cambias tu código pero no tus dependencias, Docker se saltará el paso de instalación en futuras construcciones, ahorrando mucho tiempo.
4.  **`RUN pip install ...`**: Instalamos las librerías necesarias (pandas, streamlit, xgboost, etc.). Usamos `--no-cache-dir` para no guardar archivos temporales de instalación y mantener la imagen pequeña.
5.  **`COPY . .`**: Ahora sí, copiamos todo el resto de tu código (App.py, carpetas de datos, modelos) al contenedor.
6.  **`EXPOSE 8501`**: Documentamos que el contenedor escuchará en el puerto 8501 (el estándar de Streamlit).
7.  **`CMD [...]`**: Es el comando que se ejecuta automáticamente al iniciar el contenedor. Le decimos a Streamlit que arranque `App.py` y que acepte conexiones externas (`0.0.0.0`), ya que por defecto solo aceptaría conexiones desde *dentro* del contenedor.

---

## 2. El Fichero `docker-compose.yml`

Docker Compose es una herramienta para orquestar y ejecutar contenedores fácilmente sin tener que escribir comandos largos de Docker en la terminal.

```yaml
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
```

### Desglose paso a paso:

*   **`services`**: Define los contenedores que vamos a correr. En este caso solo uno, que hemos llamado `app`.
*   **`build: .`**: Le dice a Compose que busque el `Dockerfile` en el directorio actual (`.`) para construir la imagen.
*   **`ports: "8501:8501"`**: Conecta el puerto de tu máquina (izquierda) con el puerto del contenedor (derecha).
    *   Si abres `localhost:8501` en tu navegador, tu ordenador redirige el tráfico al puerto 8501 del contenedor.
*   **`environment: PYTHONUNBUFFERED=1`**: Configuración importante para Python en Docker. Asegura que los mensajes de `print()` o logs de errores aparezcan instantáneamente en tu terminal, sin quedarse "atascados" en un búfer de memoria.
*   **`volumes: .:/app`**: Esta es la parte mágica para el desarrollo.
    *   "Espeja" tu carpeta actual (`.`) dentro de la carpeta `/app` del contenedor.
    *   **Beneficio**: Si cambias algo en `App.py` en tu editor de código, el cambio se refleja **inmediatamente** dentro del contenedor. No tienes que volver a construir la imagen cada vez que haces un cambio pequeño.

---

## 3. Cómo Usarlo

Gracias a esta configuración, todo el proceso de instalación y ejecución se reduce a un solo comando:

```bash
docker-compose up --build
```

Esto hace todo: descarga Python, instala librerías, copia el código y arranca la aplicación.
