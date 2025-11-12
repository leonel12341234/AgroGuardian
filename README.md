# AgroGuardian 🌾 | Monitoreo Inteligente de Granos

## 💡 Introducción y Descripción General

AgroGuardian es una **aplicación web** diseñada específicamente para productores agropecuarios que realizan el almacenamiento de granos (soja, maíz, trigo, girasol y cebada) en silos metálicos.

El objetivo principal es **mejorar el control, la conservación y la eficiencia** del almacenamiento. Esto se logra mediante la implementación de algoritmos inteligentes y un sistema de **monitoreo en tiempo real** de las condiciones internas del silo.

Este proyecto fue desarrollado como parte de la tesina final de la especialidad en Informática en la **Escuela PROA Río Tercero (Córdoba, Argentina)** por los estudiantes **Leonel Soto (17 años)** y **Dylan Cabrera**.

---

## ✅ Funcionalidades Principales

El sistema AgroGuardian ofrece las siguientes capacidades clave:

* **Monitoreo en tiempo real:** Visualización instantánea de la temperatura y humedad dentro del silo.
* **Alertas Inteligentes:** Notificaciones automáticas ante condiciones que comprometen el almacenamiento (temperatura o humedad crítica).
* **Algoritmos Específicos:** Lógica de análisis basada en datos climáticos locales y **recomendaciones del INTA** para cada tipo de grano.
* **Registro Histórico:** Almacenamiento de datos de cosechas, mantenimientos y eventos de alerta pasados.
* **Interfaz Responsiva:** Diseño web optimizado para zonas rurales y adaptabilidad total a dispositivos móviles y computadoras.

### 📊 Condiciones Óptimas por Tipo de Grano

AgroGuardian utiliza estos rangos para emitir alertas y recomendaciones precisas:

| Grano | Humedad ideal | Temperatura ideal |
| :--- | :--- | :--- |
| **Soja** | 13–14% | 20–25 °C |
| **Maíz** | 12–14% | 18–24 °C |
| **Trigo** | 12–13% | 16–22 °C |
| **Girasol** | 8–9% | 18–22 °C |
| **Cebada** | 12–13% | 15–20 °C |

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología |
| :--- | :--- |
| **Backend** | Python (Flask) |
| **Frontend** | HTML5 + CSS3 |
| **Base de datos** | MySQL (con XAMPP) |
| **Desarrollo** | Visual Studio Code |

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone [https://github.com/tu_usuario/agroguardian.git](https://github.com/tu_usuario/agroguardian.git)
cd agroguardian
