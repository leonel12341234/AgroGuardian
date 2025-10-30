# AgroGuardian

## Descripción general
AgroGuardian es una aplicación web pensada para productores agropecuarios que almacenan granos (soja, maíz, trigo, girasol y cebada) en silos metálicos.  
El objetivo es mejorar el control, la conservación y la eficiencia del almacenamiento mediante algoritmos inteligentes y monitoreo en tiempo real.

Este proyecto fue desarrollado como parte de la tesina final de la especialidad en Informática en la **Escuela PROA Río Tercero (Córdoba, Argentina)** por los estudiantes **Leonel Soto (17 años)** y **Dylan Cabrera**.

---

## Funcionalidades principales
- Monitoreo en tiempo real de temperatura y humedad dentro del silo.  
- Alertas automáticas ante condiciones críticas de almacenamiento.  
- Algoritmos específicos según tipo de grano, basados en datos del clima argentino y recomendaciones del INTA.  
- Registro histórico de cosechas, mantenimientos y alertas.  
- Interfaz web optimizada para zonas rurales y dispositivos móviles.

---

## Algoritmos personalizados por tipo de grano
Cada tipo de grano tiene condiciones óptimas de conservación.  
AgroGuardian utiliza lógica específica para emitir alertas y recomendaciones precisas según los valores ideales de cada uno:

### Soja
- Humedad ideal: 13–14%  
- Temperatura ideal: 20–25 °C  

### Maíz
- Humedad ideal: 13–15%  
- Temperatura ideal: 15–25 °C  

### Trigo
- Humedad ideal: 12–14%  
- Temperatura ideal: 18–24 °C  

### Girasol
- Humedad ideal: 8–10%  
- Temperatura ideal: 15–22 °C  

### Cebada
- Humedad ideal: 12–13%  
- Temperatura ideal: 16–23 °C  

El sistema analiza los datos ingresados y, si los valores se desvían, muestra recomendaciones automáticas para corregir la situación (por ejemplo: ventilar, controlar humedad o revisar sellado).

---

## Tecnologías utilizadas
- **Frontend:** HTML + CSS  
- **Backend:** Python (framework Flask)  
- **Base de datos:** MySQL (local con XAMPP)  
- **Entorno de desarrollo:** Visual Studio Code  
- **ORM:** Flask SQLAlchemy  

---

## Instrucciones de ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu_usuario/agroguardian.git
cd agroguardian
