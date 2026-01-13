# 🏦 Bluecoins Spanish Bank Importers 🇪🇸

Este repositorio contiene un conjunto de scripts en Python diseñados para convertir los extractos bancarios de entidades españolas (en formato Excel o CSV) al formato estándar de importación de la App **Bluecoins**.

El objetivo es facilitar el seguimiento de finanzas personales sin tener que introducir cada movimiento manualmente.

## 🚀 Instalación y Requisitos

Para utilizar estos scripts, necesitas tener instalado **Python 3.x** en tu ordenador.

1. **Clona este repositorio** o descarga los archivos.
2. **Instala las librerías necesarias** mediante la terminal (macOS/Linux) o CMD (Windows):

   ```bash
   pip install -r requirements.txt
   ```

## 🏦 Bancos Soportados e Instrucciones

### 1. Ibercaja (.xlsx)

El script `ibercaja.py` está optimizado para procesar el archivo Excel oficial.

**Cómo descargar el archivo:**

- Entra en tu banca online de Ibercaja.
- Ve a **Mis cuentas > Movimientos**.
- Selecciona las fechas que te interesen.
- Pulsa el botón **Descargar** y elige el formato Excel (.xlsx).

> **Nota:** No modifiques el contenido del archivo antes de usar el script.

**Cómo convertirlo:**

```bash
python ibercaja_to_bluecoins.py
```

El script te pedirá la ruta del archivo y generará un nuevo archivo llamado `ibercaja_bluecoins.csv` listo para importar.

### 2. BBVA

En desarrollo / Próximamente.

## ⚙️ Configuración Crítica en Bluecoins

Para que tu contabilidad sea precisa, sigue estas reglas de oro:

- **Saldo Inicial:** En Bluecoins, antes de importar nada, edita tu cuenta y pon el "Saldo Inicial" manual. Este debe ser el saldo que tenías el día antes del primer movimiento que vas a importar. Esto evita que tu saldo aparezca en negativo.

- **Importación:**
  - Abre Bluecoins > Ajustes > Importar datos.
  - Elige el archivo `.csv` generado por el script.
  - La app mapeará automáticamente las columnas gracias a los encabezados estándar `(1)Type`, `(2)Date`, etc.

- **Evita Duplicados:** El script no detecta si ya importaste un movimiento anteriormente. Asegúrate de que las fechas del Excel no se solapen con transacciones que ya tengas en la app.

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia MIT. Eres libre de usarlo, modificarlo y compartirlo, siempre que mantengas la nota de autoría original.

## 🤝 ¿Quieres ayudar?

Si eres cliente de otro banco español (Santander, Caixa, Sabadell...) y quieres que incluyamos un conversor, puedes:

- Abrir un **Issue** con una muestra del formato de tu banco (¡borra tus datos personales primero!).
- Enviar un **Pull Request** si has programado tu propio script de conversión.

---

### Recordatorio técnico

No olvides crear también el archivo `requirements.txt` con este contenido para que las instrucciones de instalación funcionen:

```text
pandas
openpyxl
```
