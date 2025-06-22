# LangGraph Agent

Una aplicación web que utiliza LangGraph y Anthropic para crear un asistente AI interactivo.

## Características

- Interfaz web moderna con chat en tiempo real
- Integración con Anthropic Claude-2
- Memoria conversacional persistente
- Configurable a través de la interfaz web
- Diseño responsivo

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior
- npm
- API Key de Anthropic

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL DEL REPOSITORIO]
cd reactAgent
```

2. Instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Instalar dependencias del frontend:
```bash
cd ../frontend
npm install
```

## Configuración

El proyecto requiere las siguientes variables de entorno:

- `ANTHROPIC_API_KEY`: La clave de API de Anthropic.
- `LLM_MODEL`: El modelo de LLM a utilizar (por defecto: claude-3-5-sonnet-20241022).
- `REDIS_HOST`: Host de Redis (por defecto: localhost).
- `REDIS_PORT`: Puerto de Redis (por defecto: 6379).
- `REDIS_PASSWORD`: Contraseña de Redis (opcional).

### Modelo de LLM

Por defecto, el proyecto utiliza el modelo `claude-3-5-sonnet-20241022` de Anthropic. Puedes cambiar el modelo configurando la variable de entorno `LLM_MODEL`. Por ejemplo, para usar un modelo diferente, crea un archivo `.env` con:

```env
LLM_MODEL=claude-3-sonnet-20240215
```

Asegúrate de que el modelo que elijas sea compatible con el SDK de Anthropic y que tu clave de API tenga acceso a él.

1. Establecer la variable de entorno con la API Key de Anthropic:
```bash
export ANTHROPIC_API_KEY="tu_api_key_aqui"
```

## Ejecución

1. Iniciar el servidor backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Iniciar el servidor frontend:
```bash
cd frontend
npm start
```

La aplicación estará disponible en `http://localhost:3000`

## Estructura del Proyecto

```
reactAgent/
├── backend/          # API FastAPI
│   ├── main.py      # Punto de entrada del backend
│   └── requirements.txt
├── frontend/         # Aplicación React
│   ├── src/
│   │   ├── App.js   # Componente principal
│   │   └── App.css  # Estilos
│   └── package.json
└── README.md
```

## Tecnologías Utilizadas

- Backend: FastAPI
- Frontend: React
- LLM: Anthropic Claude-2
- Framework: LangGraph
- Gestión de Estado: React useState

## Contribución

1. Fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT - ve el archivo LICENSE para más detalles.
