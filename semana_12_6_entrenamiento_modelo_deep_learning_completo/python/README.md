# Proyecto Python - Entrenamiento Deep Learning

Este proyecto implementa el flujo solicitado en el taller usando MNIST:

- carga y visualizacion del dataset;
- division entrenamiento/validacion/prueba;
- entrenamiento de una red neuronal simple;
- validacion hold-out en cada epoca;
- validacion cruzada K-Fold;
- metricas de evaluacion y matriz de confusion;
- fine-tuning con ResNet18 preentrenada;
- guardado y reutilizacion del modelo.

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion completa

```bash
python train_mnist.py
```

El script descarga MNIST en `data/`, guarda modelos en `models/` y genera graficas en `outputs/`.

## Ejecucion rapida

Para probar que todo funciona en menos tiempo:

```bash
python train_mnist.py --epochs 2 --kfold-epochs 1 --finetune-epochs 1 --finetune-samples 1000
```

Si no se quiere descargar pesos preentrenados de ResNet18:

```bash
python train_mnist.py --no-pretrained
```

## Archivos generados

- `outputs/sample_mnist.png`: ejemplo del dataset.
- `outputs/loss_curves.png`: curvas de perdida.
- `outputs/confusion_matrix.png`: matriz de confusion.
- `outputs/fold_accuracies.png`: resultados de K-Fold.
- `outputs/model_comparison.png`: comparacion MLP, ResNet congelada y ResNet con fine-tuning.
- `models/modelo_final.pth`: pesos del modelo MLP entrenado.
