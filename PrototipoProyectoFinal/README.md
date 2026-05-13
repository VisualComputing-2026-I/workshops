# Traductor en tiempo real de Lengua de Señas Colombiana

Prototipo en Python para reconocer letras del alfabeto dactilologico de la Lengua de Señas Colombiana (LSC) con webcam, convertirlas en texto y construir palabras.

El flujo del proyecto es:

1. Conseguir imagenes por letra, desde un dataset externo o capturas propias.
2. Extraer landmarks de mano con MediaPipe Hands.
3. Entrenar varios clasificadores y guardar el mejor por F1 macro.
4. Usar la app Streamlit o la demo OpenCV para reconocer letras en tiempo real.

## Requisitos

Use Python 3.10, 3.11 o 3.12. MediaPipe suele tardar en soportar versiones nuevas de Python, por eso no se recomienda Python 3.13 para este proyecto.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Datasets recomendados

Se encontraron dos fuentes utiles:

- LSC70, Universidad del Cauca / Mendeley Data: contiene alfabeto, numeros y palabras; licencia CC BY 4.0. Es la mejor fuente abierta para el prototipo academico. DOI: <https://doi.org/10.17632/9ssyn8tff5.2>
- Colombian Sign Language (LSC) - Alphabet, Kaggle: dataset especifico de alfabeto LSC, 5439 imagenes en 22 categorias; la licencia aparece como desconocida, asi que conviene usarlo con cuidado. <https://www.kaggle.com/datasets/danielrey96/colombian-sign-language-lsc-alphabet>

Intento de descarga automatica de LSC70:

```powershell
python scripts/download_lsc70.py --extract
```

Si el API de Mendeley no entrega los archivos directamente, descargue el dataset desde la pagina web y extraigalo en:

```text
data/external/lsc70/
```

Descarga via Kaggle, si tiene `kaggle.json` configurado:

```powershell
python scripts/download_kaggle_lsc_alphabet.py
```

## Captura propia

Para mayor precision con la camara y condiciones reales de la demo, capturen tambien muestras propias. Recomendacion inicial: 200 a 400 imagenes por letra, con varias personas, distancias, fondos e iluminaciones.

```powershell
python scripts/capture_samples.py --label A --samples 300
python scripts/capture_samples.py --label B --samples 300
python scripts/capture_samples.py --label N_TILDE --samples 300
```

Use `N_TILDE` para la letra Ñ. Las capturas quedan en `data/raw/<LETRA>/`.

Controles de captura:

- `Espacio`: activar o pausar captura automatica.
- `C`: guardar un frame manual.
- `Q`: salir.

## Entrenamiento

Construir el CSV de landmarks:

```powershell
python scripts/build_dataset.py --input data/raw data/external --output data/processed/features.csv
```

Entrenar y guardar el mejor modelo:

```powershell
python scripts/train_model.py --features data/processed/features.csv
```

El entrenamiento prueba `ExtraTrees`, `RandomForest`, `SVM RBF` y `MLP`, y selecciona el modelo con mejor F1 macro. Los resultados quedan en:

```text
models/best_model.joblib
models/metrics/metrics.json
models/metrics/confusion_matrix.csv
```

## LSC70

Si descargó y extrajo LSC70 en `data/external/lsc70`, puede entrenar de dos formas.

Para letras/números con imágenes de mano recortada (`LSC70ANH`):

```powershell
python scripts/build_dataset.py --input data/external/lsc70/LSC70/LSC70ANH --output data/processed/lsc70_letters_features.csv
python scripts/train_model.py --features data/processed/lsc70_letters_features.csv --model models/lsc70_letters_model.joblib --metrics-dir models/metrics_lsc70_letters
```

Para palabras dinámicas de `LSC70W`, el proyecto usa secuencias de 6 frames:

```powershell
python scripts/build_lsc70_sequences.py --input data/external/lsc70 --subset LSC70W --output data/processed/lsc70_words_sequences.csv
python scripts/train_model.py --features data/processed/lsc70_words_sequences.csv --model models/lsc70_words_model.joblib --metrics-dir models/metrics_lsc70_words --model-type sequence --sequence-length 6
```

Luego cargue el modelo deseado en la barra lateral de Streamlit:

```text
models/lsc70_letters_model.joblib
models/lsc70_words_model.joblib
```

## Uso

Interfaz presentable:

```powershell
streamlit run app.py
```

Demo OpenCV de respaldo:

```powershell
python scripts/run_opencv_demo.py
```

Controles en la demo OpenCV:

- `Espacio`: agregar espacio.
- `B` o `Backspace`: borrar.
- `C`: limpiar texto.
- `Q`: salir.

## Estructura

```text
app.py                         # interfaz Streamlit
scripts/
  capture_samples.py           # captura imagenes etiquetadas
  build_dataset.py             # imagenes -> landmarks CSV
  train_model.py               # entrenamiento y evaluacion
  run_opencv_demo.py           # demo local con OpenCV
  download_lsc70.py            # descarga asistida LSC70
  download_kaggle_lsc_alphabet.py
src/lsc_alphabet/
  landmarks.py                 # MediaPipe y vector de features
  dataset.py                   # construccion de dataset tabular
  training.py                  # modelos y metricas
  predictor.py                 # inferencia
  stabilizer.py                # letras estables -> palabras
  visualization.py             # overlays de camara
```

## Notas de precision

Para letras estaticas, un clasificador sobre landmarks normalizados suele ser mas practico que iniciar con LSTM o Transformer. Cuando tengan un dataset estable para todo el alfabeto, pueden extender el mismo flujo a secuencias temporales para letras dinamicas o palabras completas.
