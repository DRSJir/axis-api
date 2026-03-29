# AXIS Precision Tools - API

### **Description**
**AXIS-API** es el núcleo de procesamiento y gestión de datos para la plataforma AXIS. Es un backend ligero diseñado bajo una arquitectura de microservicios desacoplados, encargado de gestionar el inventario de herramientas de micro-electrónica de alta precisión. 

El sistema garantiza la **integridad ACID** mediante el uso de SQLAlchemy y cuenta con un sistema de **auto-seeding** que asegura la disponibilidad de datos de prueba en entornos de despliegue efímeros como la capa gratuita de Render.

### **Badges**
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)
![Render](https://img.shields.io/badge/Render-%2346E3B7.svg?style=flat&logo=render&logoColor=white)

### **Uso**

#### **Requisitos previos**
* Docker instalado (Recomendado)
* O Python 3.11 con un entorno virtual (`venv`)

#### **Instalación y Ejecución Local (Docker)**
1. Construir la imagen:
   ```bash
   docker build -t axis-api .
   ```
2. Ejecutar el contenedor:
   ```bash
   docker run -p 5000:5000 axis-api
   ```

#### **Endpoints Principales**
| Método | Ruta | Descripción | Requiere Auth |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/products` | Obtiene el catálogo completo | No |
| **POST** | `/api/products` | Agrega un nuevo producto | **Sí (X-API-KEY)** |
| **PUT** | `/api/products/<id>` | Actualiza el stock de un item | **Sí (X-API-KEY)** |

#### **Autenticación**
Para los métodos de escritura, se debe incluir el siguiente header en la petición:
`X-API-KEY: axis_secret_2026`

### **Autores**
* **Jair** - [GitHub](https://github.com/tu-usuario)

### **Project status**
🟡 **En Desarrollo**: 
Actualmente, el backend es funcional y está desplegado en Render. 
Siguientes pasos
- Lógica de compras.
- Desarrollo e integración del frontend (AXIS-Web) en Netlify.
