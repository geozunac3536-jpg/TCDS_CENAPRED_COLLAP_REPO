# TCDS_CENAPRED_COLLAP_REPO — Índice Operativo (Colab + Sellado)

Repositorio técnico para evaluación reproducible basada en datos sísmicos públicos (USGS / IRIS).
Ejecución en nube vía **Google Colab** (sin instalación local).

---

## 🚀 Ejecutar (3 botones)

> Nota: Colab abre **notebooks `.ipynb`** (los `.py` se descargan y ejecutan desde ahí).

### 1) Ejecutar sistema (AERC)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_AERC.ipynb
)

### 2) Generar sello (SHA256)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_make_seal.ipynb
)

### 3) Verificar integridad (archivo vs sello)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/colab/run_verify_seal.ipynb
)

---

## ✅ Flujo recomendado (simple)
1. **Abrir AERC** → en Colab: *Entorno de ejecución → Ejecutar todas*  
2. El sistema genera un **resultado** (ej. `result.json`)  
3. **Abrir “Generar sello”** → subir el resultado → ejecutar → genera `result.json.sha256`  
4. **Abrir “Verificar”** → subir resultado + `.sha256` → ejecutar → confirma **OK / FAIL**

---

## 📄 Licencia (acceso directo)
- Licencia: `LICENSE.md`
- Avisos: `NOTICE.md`

Acceso directo (GitHub):
- https://github.com/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/LICENSE.md
- https://github.com/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/NOTICE.md

---

## 📁 Estructura mínima
TCDS_CENAPRED_COLLAP_REPO/ │ ├── index.html ├── README.md ├── requirements.txt ├── LICENSE.md ├── NOTICE.md │ ├── colab/ │   ├── run_AERC.ipynb │   ├── run_make_seal.ipynb │   └── run_verify_seal.ipynb │ ├── code/ │   └── code.py │ └── tools/ ├── make_seal.py └── verify_seal.py
---

## 👤 Contacto (autor)
- **Nombre:** Genaro Carrasco Ozuna  
- **ORCID:** https://orcid.org/0009-0005-6358-9910  
- **Email:** geozunac3536@gmail.com  
- **GitHub:** https://github.com/geozunac3536-jpg  
- **WhatsApp / Tel:** +52 812 598 9868
