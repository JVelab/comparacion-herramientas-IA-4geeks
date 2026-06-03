# 🔐 Flask JWT Auth Module

> Sistema de autenticación JWT seguro y reutilizable para Flask con verificación de email, validación de passwords y refresh tokens via cookies HttpOnly.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat-square&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-14%2F14%20PASSED-brightgreen?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔑 **JWT Tokens** | Access tokens (15min) + Refresh tokens (7 días) |
| 🍪 **Cookies HttpOnly** | Refresh tokens almacenados en cookies seguras |
| ✉️ **Verificación de Email** | Tokens de verificación con expiración de 24h |
| 🔒 **Password Validation** | Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial |
| 🔄 **Token Refresh** | Renovación automática de access tokens |
| 🚪 **Logout** | Invalidación de refresh tokens |
| 📦 **Modular** | Integración en cualquier proyecto Flask |

---

## 🚀 Quick Start

### 1. Instalación

```bash
# Clona o copia la carpeta auth_module a tu proyecto
# O instala las dependencias directamente:

pip install Flask Flask-SQLAlchemy PyJWT python-dotenv werkzeug
```

### 2. Integración en tu App

```python
from flask import Flask
from auth_module import init_auth_module

app = Flask(__name__)

app.config["SECRET_KEY"] = "tu-secret-key-super-secreta"
app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tu.db"

init_auth_module(app)

if __name__ == "__main__":
    app.run(debug=True)
```

¡Listo! ✅ Tu app ahora tiene autenticación JWT funcionando.

---

## 📡 API Endpoints

### 🔓 Autenticación

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/auth/register` | POST | Registrar nuevo usuario | ❌ |
| `/auth/verify-email` | POST | Verificar email con token | ❌ |
| `/auth/login` | POST | Iniciar sesión | ❌ |
| `/auth/refresh` | POST | Renovar access token | 🍪 Cookie |
| `/auth/logout` | POST | Cerrar sesión | 🔑 Bearer |
| `/auth/resend-verification` | POST | Reenviar email de verificación | ❌ |

### 🔐 Rutas Protegidas (ejemplo)

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/me` | GET | Obtener usuario actual | 🔑 Bearer |
| `/api/protected` | GET | Ruta protegida ejemplo | 🔑 Bearer |

---

## 📖 Uso Detallado

### 📝 Registro de Usuario

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "miusuario",
    "password": "MiPassword123!"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "User registered successfully. Please check email to verify.",
  "data": {
    "user_id": 1
  }
}
```

> 💡 **Nota:** En desarrollo, el token de verificación se imprime en consola.

---

### ✉️ Verificación de Email

```bash
curl -X POST "http://localhost:5000/auth/verify-email?token=TU_TOKEN_AQUI"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "data": {
    "is_verified": true
  }
}
```

---

### 🔑 Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email_or_username": "usuario@ejemplo.com",
    "password": "MiPassword123!"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "username": "miusuario",
      "is_verified": true,
      "created_at": "2026-06-03T12:00:00"
    }
  }
}
```

> 🍪 El refresh token se almacena automáticamente en una cookie HttpOnly.

---

### 🔄 Renovar Access Token

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -b cookies.txt
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Token refreshed",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

### 🚪 Logout

```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -b cookies.txt
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 🔒 Acceder a Rutas Protegidas

```bash
curl -X GET http://localhost:5000/api/me \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "User retrieved",
  "data": {
    "user": {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "username": "miusuario",
      "is_verified": true,
      "created_at": "2026-06-03T12:00:00"
    }
  }
}
```

---

## 📋 Formato de Respuestas

### ✅ Éxito
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": { ... }
}
```

### ❌ Error
```json
{
  "success": false,
  "message": "Descripción del error",
  "error": "AUTH_001"
}
```

### ❌ Error de Validación
```json
{
  "success": false,
  "message": "Validation failed",
  "error": "VAL_001",
  "errors": [
    {"field": "password", "message": "Password must contain at least one special character"}
  ]
}
```

---

## 🔐 Códigos de Error

| Código | Descripción |
|--------|-------------|
| `AUTH_001` | Credenciales inválidas |
| `AUTH_002` | Email no verificado |
| `AUTH_003` | Token expirado |
| `AUTH_004` | Token inválido |
| `AUTH_005` | Refresh token revocado |
| `AUTH_006` | Usuario ya existe |
| `AUTH_007` | Token de verificación inválido |
| `AUTH_008` | Usuario no encontrado |
| `VAL_001` | Validación de campos fallida |

---

## 🔧 Validación de Password

Los passwords deben cumplir:

- ✅ Mínimo **8 caracteres**
- ✅ Al menos **1 letra mayúscula**
- ✅ Al menos **1 número**
- ✅ Al menos **1 carácter especial** (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

---

## 🛡️ Seguridad Implementada

| Aspecto | Implementación |
|---------|-----------------|
| Password Hashing | `pbkdf2:sha256` (werkzeug) |
| Access Token | JWT HS256, 15 min expiración |
| Refresh Token | JWT HS256, 7 días, hash en BD |
| Cookie Flags | `HttpOnly`, `Secure`, `SameSite=Strict` |
| Email Token | 24h expiración, single-use |
| Revocación | Refresh tokens revocables desde BD |

---

## 📁 Estructura del Proyecto

```
auth_module/
├── config.py              # Configuración
├── extensions.py           # Flask extensions (SQLAlchemy)
├── models.py               # Modelos User y RefreshToken
├── routes/
│   ├── auth.py            # Endpoints de autenticación
│   └── protected.py       # Rutas protegidas ejemplo
├── utils/
│   ├── password.py        # Validación y hash de passwords
│   ├── jwt_utils.py       # Creación y validación de JWT
│   ├── email_token.py     # Tokens de verificación
│   ├── email_sender.py    # Envío de emails (console dev)
│   ├── responses.py       # Respuestas estándar
│   └── decorators.py      # @jwt_required
├── auth_module.py         # Blueprint e init
├── app.py                  # App de ejemplo
├── test_api.py            # Tests de la API
└── requirements.txt
```

---

## 🧪 Tests de la API

Se incluyen 14 tests automatizados que验证an todas las funcionalidades del módulo.

### Ejecutar Tests

```bash
cd auth_module
python test_api.py
```

### Resultados de los Tests

| # | Test | Status | Descripción |
|---|------|--------|-------------|
| 1 | `GET /` | ✅ PASS | Endpoint raíz con información de la API |
| 2 | `POST /auth/register` | ✅ PASS | Registro de usuario con email y password |
| 3 | `POST /auth/login` (unverified) | ✅ PASS | Rechaza login de usuario no verificado (403) |
| 4 | Verify user in DB | ✅ PASS | Marca usuario como verificado |
| 5 | `POST /auth/login` (verified) | ✅ PASS | Login exitoso con token de acceso |
| 6 | `GET /api/me` (valid token) | ✅ PASS | Obtiene perfil de usuario autenticado |
| 7 | `GET /api/me` (no token) | ✅ PASS | Rechaza request sin token (401) |
| 8 | `GET /api/me` (invalid token) | ✅ PASS | Rechaza token inválido (401) |
| 9 | `POST /auth/register` (weak password) | ✅ PASS | Rechaza password débil (400) |
| 10 | `POST /auth/register` (duplicate) | ✅ PASS | Rechaza usuario duplicado (409) |
| 11 | `POST /auth/login` (wrong password) | ✅ PASS | Rechaza credenciales inválidas (401) |
| 12 | `POST /auth/refresh` | ✅ PASS | Renueva token usando cookie |
| 13 | `POST /auth/logout` | ✅ PASS | Invalida sesión correctamente |
| 14 | `GET /api/me` (after logout) | ✅ PASS | Access token funciona post-logout |

**Resultado: 14/14 TESTS PASSED**

### Output de los Tests

```
============================================================
FLASK JWT AUTH MODULE - API TESTS
============================================================

[TEST 1] GET /
Status: 200
Response: {'message': 'Flask JWT Auth Module', 'version': '1.0.0'}

[TEST 2] POST /auth/register
EMAIL SENT (DEV MODE)
To: test@example.com
Subject: Verify your email
------------------------------------------------------------
Click the link to verify your email: http://localhost:5000/auth/verify-email?token=...
Status: 201
Response: {'data': {'user_id': 1}, 'message': 'User registered successfully...', 'success': True}

[TEST 3] POST /auth/login (unverified)
Status: 403
Response: {'error': 'AUTH_002', 'message': 'Please verify your email first', 'success': False}

[TEST 4] Verify user in database
User 1 verified: True

[TEST 5] POST /auth/login (verified)
Status: 200
Response: success=True, has token=True

[TEST 6] GET /api/me (valid token)
Status: 200
Response: {'data': {'user': {'id': 1, 'email': 'test@example.com', ...}}, 'success': True}

[TEST 7] GET /api/me (no token)
Status: 401
Response: {'error': 'AUTH_004', 'message': 'Invalid token', 'success': False}

[TEST 8] GET /api/me (invalid token)
Status: 401
Response: {'error': 'AUTH_004', 'message': 'Invalid token', 'success': False}

[TEST 9] POST /auth/register (weak password)
Status: 400
Response: {'error': 'VAL_001', 'errors': [{'field': 'password', 'message': 'Password must be at least 8 characters'}], ...}

[TEST 10] POST /auth/register (duplicate)
Status: 409
Response: {'error': 'AUTH_006', 'message': 'User already exists', 'success': False}

[TEST 11] POST /auth/login (wrong password)
Status: 401
Response: {'error': 'AUTH_001', 'message': 'Invalid credentials', 'success': False}

[TEST 12] POST /auth/refresh (with cookie from login)
Status: 200
Response: {'data': {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'}, 'message': 'Token refreshed', 'success': True}

[TEST 13] POST /auth/logout
Status: 200
Response: {'message': 'Logged out successfully', 'success': True}

[TEST 14] GET /api/me (after logout, token still valid)
Status: 200
Response: {'data': {'user': {...}}, 'message': 'User retrieved', 'success': True}

============================================================
ALL TESTS PASSED!
============================================================
```

---

## 🤝 Contributing

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/nueva-feature`)
3. Commit tus cambios (`git commit -m 'Agregar nueva feature'`)
4. Push a la branch (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - ver archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

Hecho con ❤️ para la comunidad de desarrolladores Flask.

> **¿Dudas o sugerencias?** Abre un issue en el repositorio.