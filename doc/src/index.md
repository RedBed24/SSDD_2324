---
title: "Documentación IceDrive Blob Service"
author: "Samuel Espejo Gil"
---

IceDrive nos proporciona esta interfaz:

![Interfaz](interfaces.svg)

Aquí sólo se muestran aquellas clases de las que se tiene que preocupar BlobService, otras como Directory, y los Query y Response de otros servicios no se tienen en cuenta.

Se puede encontrar información a fondo sobre cada interfaz y clase en la página correspondiente a cada una:

- BlobService
- DataTransfer
- Discovery
- BlobQuery
- BlobQueryResponse

Respecto al Authentication, sólo nos preocupa su método `verifyUser`, del cual no nos tenemos que preoucupar por implementar.
Tenemos más información al respecto en la página del BlobService.
Ocurre lo mismo con User.

# Implementación

Para abordar esto, se plantea el siguiente diagrama de clases:

![Uso de interfaces](uso_interfaces.svg)

