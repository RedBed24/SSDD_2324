# IceDrive Blob Service

Implementación del servicio blob para IceDrive.
Es una implementación completa, con descubrimiento y resolución diferida.

# Instalación

```
pip install .
```

# Uso

```
icedrive-blob <archivo de configuración>
```

# Configuración

Existe un [archivo de configuración de ejemplo](config/blob.config).

## Interna

Se esperan los siguientes campos:

1. BlobsDirectory: Indica el directorio donde se guardan los blobs
2. LinksDirectory: Indica el directorio donde se guardan los links
3. PartialUploadsDirectory: Indica el directorio donde se descargan los blobs, que luego serán movidos
4. DataTransferSize: Indica el tamaño en bytes que se usan para las transferencias de blobs

## Ice

Esto es como todos los otros servicios.

# Documentación

Se pueden encontrar explicaciones sobre el funcionamiento interno del servicio en la [página de la documentación oficial](https://redbed24.github.io/SSDD_2324).

# Autor

[Samuel Espejo Gil](mailto:samuel.espejo@alu.uclm.es).

