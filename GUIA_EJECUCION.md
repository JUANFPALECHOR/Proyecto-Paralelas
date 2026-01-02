# Guía de Ejecución del Proyecto

Esta guía explica paso a paso cómo ejecutar el proyecto de análisis de correlación Noticias vs COLCAP.

## 📋 Prerrequisitos

- **Docker Desktop** instalado y ejecutándose
- **Windows PowerShell** (o terminal de comandos)

## 🚀 Ejecución con Docker Compose (Recomendado)

Esta es la forma más simple de ejecutar el proyecto completo.

### Paso 1: Abrir Terminal

Abre **PowerShell** o **Command Prompt** y navega al directorio del proyecto:

```powershell
cd "C:\Carpetas de tu sistema\Proyecto-Paralelas"
```

### Paso 2: Construir las Imágenes Docker

**En la misma terminal**, ejecuta:

```powershell
docker-compose build
```

Este comando:
- Construye las imágenes Docker para el API y el Dashboard
- Instala todas las dependencias (incluyendo PySpark y Java)
- Tarda varios minutos la primera vez

**Espera a que termine completamente** (verás mensajes de "Successfully built" y "DONE").

### Paso 3: Iniciar los Servicios

**En la misma terminal**, ejecuta:

```powershell
docker-compose up -d
```

Este comando:
- Inicia el servicio API en el puerto 8000
- Inicia el servicio Dashboard en el puerto 8501
- Ejecuta los servicios en segundo plano (`-d`)

### Paso 4: Verificar que los Servicios Están Corriendo

**En la misma terminal**, ejecuta:

```powershell
docker-compose ps
```

Deberías ver ambos servicios con estado "Up" y "healthy":
- `analysis-api` - Puerto 8000
- `news-dashboard` - Puerto 8501

### Paso 5: Acceder al Dashboard

Abre tu navegador web y ve a:

```
http://localhost:8501
```

Aquí encontrarás:
- Interfaz para subir archivos CSV
- Selector de backends (pandas, multiprocessing, dask, spark)
- Visualización de resultados con gráficas

### Paso 6: Probar la API (Opcional)

**En una nueva terminal**, puedes probar que la API funciona:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Deberías ver: `{"status": "healthy"}`

También puedes abrir en el navegador:
```
http://localhost:8000/docs
```

Esto muestra la documentación interactiva de la API (Swagger UI).

---

## 📊 Uso del Dashboard

1. **Subir archivos CSV:**
   - **CSV de noticias**: Sube `data\output.csv` (ya incluido en el proyecto)
   - **CSV de COLCAP**: Sube `data\colcap_sample.csv` (ya incluido en el proyecto)

2. **Configurar backend:**
   - Selecciona el backend deseado: `pandas`, `multiprocessing`, `dask`, o `spark`
   - Ajusta parámetros si es necesario (procesos, particiones, etc.)

3. **Ejecutar análisis:**
   - Click en "Calcular correlación"
   - Espera a que termine el procesamiento
   - Verás tablas con los resultados y gráficas interactivas

---

## 🔍 Ver Logs de los Servicios

Si necesitas ver qué está pasando, **en una terminal** ejecuta:

```powershell
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs solo del API
docker-compose logs -f analysis-api

# Ver logs solo del Dashboard
docker-compose logs -f dashboard
```

Presiona `Ctrl+C` para salir de los logs.

---

## 🛑 Detener los Servicios

**En una terminal**, ejecuta:

```powershell
docker-compose down
```

Esto detiene y elimina los contenedores.

---

## 🔄 Reiniciar los Servicios

Si necesitas reiniciar después de hacer cambios:

```powershell
# Detener
docker-compose down

# Reconstruir (solo si cambiaste código)
docker-compose build

# Iniciar de nuevo
docker-compose up -d
```

---

## ⚠️ Solución de Problemas

### Error: "port is already allocated"
El puerto 8000 o 8501 ya está en uso. Solución:
```powershell
# Ver qué proceso usa el puerto
Get-NetTCPConnection -LocalPort 8000
Get-NetTCPConnection -LocalPort 8501

# O simplemente detener todos los contenedores
docker-compose down
```

### Error: "Cannot connect to Docker daemon"
Docker Desktop no está corriendo. Abre Docker Desktop y espera a que esté completamente iniciado (ícono verde).

### Los servicios no inician correctamente
```powershell
# Ver logs para identificar el error
docker-compose logs

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### El dashboard muestra error al calcular correlación
- Verifica que ambos archivos CSV estén subidos
- Verifica que los archivos CSV tengan el formato correcto
- Revisa los logs: `docker-compose logs analysis-api`

---

## 📝 Resumen de Comandos

| Acción | Comando |
|--------|---------|
| Construir imágenes | `docker-compose build` |
| Iniciar servicios | `docker-compose up -d` |
| Ver estado | `docker-compose ps` |
| Ver logs | `docker-compose logs -f` |
| Detener servicios | `docker-compose down` |
| Reiniciar | `docker-compose down && docker-compose up -d` |

---

## 🌐 URLs Importantes

- **Dashboard**: http://localhost:8501
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

¡Listo! Ya puedes usar el proyecto. 🎉

