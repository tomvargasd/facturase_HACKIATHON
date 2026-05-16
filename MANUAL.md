# Manual de Usuario — Facturase

Sistema de auditoría inteligente de facturas automotrices con IA.  
Versión 1.0.0 · HackIAThon 2026

---

## Índice

1. [Acceso y login](#1-acceso-y-login)
2. [Tour guiado de la aplicación](#2-tour-guiado-de-la-aplicación)
3. [Dashboard](#3-dashboard)
4. [Auditar Factura](#4-auditar-factura)
5. [Cola de revisión](#5-cola-de-revisión)
6. [Historial de auditorías](#6-historial-de-auditorías)
7. [Gestión de Siniestros](#7-gestión-de-siniestros)
8. [Tarifario](#8-tarifario)
9. [Notion Sync](#9-notion-sync)
10. [Modo prueba](#10-modo-prueba)
11. [Gestión de usuarios (CLI)](#11-gestión-de-usuarios-cli)
12. [Despliegue en producción](#12-despliegue-en-producción)

---

## 1. Acceso y login

Al abrir la aplicación se muestra una pantalla de acceso con:

- **Campo usuario** — nombre de usuario registrado en el sistema.
- **Campo contraseña** — contraseña definida al crear la cuenta.
- **Captcha matemático** — operación aritmética simple para verificar que no es un bot. Si no es legible, haz clic en **↺ Nuevo captcha**.
- **Botón Ingresar** — valida las credenciales. Si son incorrectas, muestra un mensaje de error sin revelar qué campo es incorrecto.

> Las contraseñas se almacenan con **PBKDF2-SHA256 + sal aleatoria**. Nunca se guardan en texto plano.

Para crear el primer usuario administrador, usa el CLI (ver sección 11).

---

## 2. Tour guiado de la aplicación

Al iniciar sesión por primera vez se activa automáticamente un **tour interactivo** que recorre cada sección de la app:

- Un **overlay oscuro** cubre la pantalla y destaca la zona que se está explicando con un recuadro luminoso.
- Una **tarjeta flotante** describe la sección actual.
- Botones de navegación: **← Anterior**, **Siguiente →** y **Omitir tour**.

El tour se marca como completado cuando llegas al último paso o pulsas "Omitir". Una vez completado, no vuelve a aparecer automáticamente.

**Volver a ver el tour:** en el sidebar, botón **"Tour de la aplicación"** → disponible en cualquier momento.

---

## 3. Dashboard

Pantalla principal con métricas globales y acciones rápidas.

### Acciones rápidas

Tres tarjetas con acceso directo a los módulos más usados:

| Acción | Destino |
|---|---|
| Nueva auditoría | Módulo Auditar Factura |
| Agregar a cola | Módulo Cola de revisión |
| Nuevo siniestro | Módulo Siniestros |

### Métricas

Se calculan sobre **todas las auditorías** almacenadas:

| Métrica | Descripción |
|---|---|
| Total auditadas | Número total de facturas procesadas |
| Aprobadas / Observadas / Rechazadas | Conteo y porcentaje por resultado |
| Rev. humana | Casos que requieren revisión de un ajustador |
| Ahorro detectado | Suma de discrepancias económicas encontradas |

### Gráficos

- **Distribución de resultados** — gráfico de dona (Aprobada / Observada / Rechazada).
- **Confianza por resultado** — boxplot de la confianza de la IA por tipo de resultado.
- **Tipos de discrepancia más frecuentes** — gráfico de barras.

---

## 4. Auditar Factura

Módulo principal de análisis.

### Paso 1 — Expediente del siniestro

Selecciona el expediente contra el cual se va a auditar la factura. Puedes expandir el detalle para ver tipo de accidente, vehículo, póliza y partes afectadas.

### Paso 2 — Factura a auditar

Dos pestañas:

**Subir PDF** — arrastra o selecciona un archivo PDF de la factura. La IA extrae los ítems automáticamente con Gemini Vision.

**Factura de demostración** — disponible en Modo prueba. Selecciona una de las tres facturas demo precargadas para hacer pruebas sin necesidad de un PDF real.

### Paso 3 — Acción

| Botón | Descripción |
|---|---|
| **Ejecutar auditoría ahora** | Procesa la factura inmediatamente y muestra el dictamen |
| **Agregar a cola de procesamiento** | Acumula el caso para procesarlo en lote más adelante |

### Dictamen

Una vez ejecutada la auditoría se muestra el resultado con:

- **Badge de resultado:** APROBADA (verde) / OBSERVADA (amarillo) / RECHAZADA (rojo).
- **4 métricas:** confianza IA, ítems aprobados, ítems observados, discrepancias en $.
- **Alerta de revisión humana** si el nivel de confianza o el monto superan los umbrales configurados.
- **Razonamiento del agente** — explicación detallada de la decisión.
- **Tabla de discrepancias** — ítems con precio excedido, código no encontrado, duplicados o incoherencias.
- **Gráfico de discrepancias** — dona por tipo de discrepancia.
- **Botón "Abrir en Notion"** — si Notion está configurado, abre la página sincronizada.

---

## 5. Cola de revisión

Permite acumular múltiples casos y procesarlos todos de una vez.

### Pestaña "Ver cola"

- **Métricas:** total en cola, pendientes, completados, con error.
- **Lista de ítems** con estado visual (azul=pendiente, verde=completado, rojo=error).
- **Botón "x"** para eliminar un ítem individual.
- **Procesar todos los pendientes** — ejecuta la auditoría en secuencia con barra de progreso.
- **Limpiar completados / errores** — limpia la cola sin afectar el historial.

### Pestaña "Agregar a cola"

Formulario para agregar un caso manualmente seleccionando siniestro y factura demo.

> En modo producción (PDF), los casos se agregan a la cola directamente desde el módulo "Auditar Factura" con el botón "Agregar a cola de procesamiento".

---

## 6. Historial de auditorías

Registro completo de todos los análisis realizados.

- **Tabla resumen** con código de colores por resultado.
- **Selector de detalle** — elige cualquier auditoría para ver el dictamen completo con todos sus datos.
- Si Notion está configurado, cada dictamen muestra el botón **"Abrir en Notion"** o **"Subir a Notion"** si aún no fue sincronizado.

---

## 7. Gestión de Siniestros

### Lista de siniestros

Tabla con todos los expedientes. Puedes expandir para ver el detalle completo o para eliminar un siniestro.

> Los siniestros demo (`SIN-2025-001/002/003`) solo se muestran con **Modo prueba** activado.

### Registrar nuevo siniestro

Formulario con los campos:

| Campo | Formato |
|---|---|
| ID del siniestro | Texto libre, p.ej. `SIN-2026-001` |
| Número de póliza | Texto libre, p.ej. `POL-MX-00012345` |
| Tipo de accidente | Lista desplegable |
| Fecha del accidente | Selector de fecha |
| Descripción del vehículo | Texto libre |
| Partes afectadas | Lista separada por comas |
| Descripción del accidente | Área de texto |

---

## 8. Tarifario

Base de precios de referencia para las auditorías.

### Lista de precios

Tabla filtrable por categoría (`insumo`, `mano_obra`, `servicio`) con los precios mínimo y máximo por código.

### Agregar ítem

Formulario con: código, descripción, precio mínimo, precio máximo, unidad, categoría, vigencia desde/hasta.

### Eliminar ítem

Selector con confirmación antes de eliminar permanentemente.

---

## 9. Notion Sync

Integración opcional con Notion para visualizar los datos de forma externa.

### Conectar por primera vez

1. Ve a [notion.so/my-integrations](https://www.notion.so/my-integrations) y crea una integración de tipo **Internal**.
2. Copia el **Token** (comienza con `secret_`).
3. En Notion, abre la página donde quieres las bases de datos → `···` → **Add connections** → selecciona tu integración.
4. Copia el **ID de la página** desde la URL (32 caracteres hex).
5. En Facturase → Notion Sync → ingresa los dos valores y haz clic en **"Conectar y crear bases de datos"**.

La app crea automáticamente tres bases de datos en Notion:
- **Auditorias — Facturase**
- **Siniestros — Facturase**
- **Tarifario — Facturase**

### Sincronización automática

Cada vez que se ejecuta una auditoría, el resultado se sube automáticamente a Notion. Los datos son de **solo lectura** en Notion (no editar manualmente).

### Sincronización manual

Desde la página Notion Sync puedes forzar la sincronización de:
- Todas las auditorías históricas
- Todos los siniestros
- El tarifario completo

### Abrir en Notion

En cada dictamen (módulo Auditar y módulo Historial) aparece el botón **"Abrir en Notion"** que lleva directamente a la página correspondiente.

### Desconectar

Botón **"Desconectar Notion"** elimina la configuración local. Los datos en Notion no se borran.

---

## 10. Modo prueba

Toggle en el sidebar. Cuando está activo (por defecto):

- Se muestran los tres siniestros demo (`SIN-2025-001/002/003`).
- Se habilitan las tres facturas demo en el módulo de auditoría.
- Aparece un indicador naranja "Datos de demo activos".

Desactívalo para trabajar exclusivamente con datos reales.

---

## 11. Gestión de usuarios (CLI)

### Crear un usuario

```bash
python scripts/add_user.py
```

Se pedirá interactivamente el nombre de usuario y la contraseña (dos veces para confirmar).

### Verificar usuarios existentes

```bash
python -c "
from app.database import listar_usuarios_count
print(f'Usuarios registrados: {listar_usuarios_count()}')
"
```

---

## 12. Despliegue en producción

### Requisitos del servidor

- Ubuntu 22.04 LTS (o compatible)
- Python 3.12+
- Apache 2 con módulos `proxy` y `proxy_http`
- Certbot (Let's Encrypt)

### Instalación en el servidor

```bash
# Como root o con sudo
useradd -m -s /bin/bash facturase
su - facturase

# Clonar el repo
git clone https://github.com/tomvargasd/facturase_HACKIATHON.git facturase_HACKIATHON
cd facturase_HACKIATHON

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # Agregar GEMINI_API_KEY

python -m scripts.seed_database
python scripts/add_user.py
```

### Servicio systemd

Crear `/etc/systemd/system/facturase.service`:

```ini
[Unit]
Description=Facturase Streamlit App
After=network.target

[Service]
User=facturase
WorkingDirectory=/home/facturase/facturase_HACKIATHON
ExecStart=/home/facturase/facturase_HACKIATHON/.venv/bin/streamlit run dashboard/streamlit_app.py --server.port 8501 --server.address 127.0.0.1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable facturase
systemctl start facturase
```

### Apache Virtual Host con SSL

```apache
<VirtualHost *:80>
    ServerName facturase.dpdns.org
    Redirect permanent / https://facturase.dpdns.org/
</VirtualHost>

<VirtualHost *:443>
    ServerName facturase.dpdns.org

    SSLEngine on
    SSLCertificateFile    /etc/letsencrypt/live/facturase.dpdns.org/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/facturase.dpdns.org/privkey.pem

    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:8501/
    ProxyPassReverse / http://127.0.0.1:8501/

    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteRule /(.*) ws://127.0.0.1:8501/$1 [P,L]
</VirtualHost>
```

### Obtener certificado SSL

```bash
systemctl stop facturase
certbot certonly --standalone -d facturase.dpdns.org
systemctl start facturase
systemctl restart apache2
```

### Actualizar la aplicación

```bash
su - facturase
cd facturase_HACKIATHON
git pull
source .venv/bin/activate
pip install -r requirements.txt
exit
systemctl restart facturase
```

---

*Manual generado para Facturase v1.0.0 · HackIAThon 2026*
