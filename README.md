# TCDS — Índice Operativo (Evaluación Técnica)

Repositorio técnico para evaluación independiente de **estados críticos previos**
mediante análisis de coherencia y reducción entrópica sobre **datos sísmicos públicos**
(USGS / IRIS).

El sistema es:
- No intrusivo  
- Reproducible  
- Auditable  
- Ejecutable directamente en la nube (Google Colab)

No requiere instalación local.

---

## 🚀 Ejecución directa en Google Colab

> **Importante**  
> Los accesos se realizan mediante notebooks lanzadores (`.ipynb`), que preparan
> el entorno y ejecutan los programas del repositorio.

---

### 1) Programa principal — AERC (ejecución completa)

Ejecuta el análisis completo en una sola corrida:
- Ingesta de datos
- Cálculo de métricas internas
- Generación de artefactos verificables (JSON, hash, visuales)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_AERC.ipynb
)

---

### 2) Verificación de integridad (sello criptográfico)

Permite comprobar que un resultado no ha sido alterado.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_verify_seal.ipynb
)

---

### 3) Generación de sello criptográfico

Genera el hash asociado a una corrida específica para trazabilidad.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_make_seal.ipynb
)

---

## ▶️ Flujo recomendado de uso

1. Ejecutar **AERC**
2. Revisar resultados generados
3. Generar sello criptográfico
4. Verificar integridad del artefacto

Cada paso es independiente y repetible.

---

## 📁 Estructura del repositorio
