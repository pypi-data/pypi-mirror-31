k8s-build-maps
==============

Build a directory of Kubernetes ConfigMap/Secret manifests, inserting
data from files.

Example
-------

Given this directory:

-  example-manifests/

   -  configmaps/

      -  mymap.yaml
      -  mymap.yaml.files/

         -  file1
         -  file2

Where ``mymap.yaml`` looks like::

   apiVersion: v1
   kind: ConfigMap
   metadata:
     namespace: mynamespace
     name: something
     labels:
       mylabel: value

Running ``k8s-build-maps example-manifests example-manifests-built`` creates this
directory:

-  example-manifests-built/

   -  configmaps/

      -  mymap.yaml

Where ``mymap.yaml`` has the following content:

   apiVersion: v1
   kind: ConfigMap
   metadata:
     namespace: mynamespace
     name: something
     labels:
       mylabel: value
   data:
     file2: dGVzdDI=
     file1: dGVzdDE=

Installation
------------

::

   pip install k8s-build-maps

Usage
-----

::

   k8s-build-maps SOURCE [DEST] [--clean] [--no-clean] [-q/--quiet] [--debug]

Where:

- ``SOURCE``: Required. The source manifest directory.
- ``DEST``: Optional if present in build config (see below). The destination manifest directory.
- ``--clean/--no-clean``: Pass ``--clean`` to remove existing files in ``DEST`` before building the manifests.
- Defaults to ``--no-clean``.
- ``-q/--quiet``: Hide output.
- ``--debug``: Enable debug logging.

Config file
~~~~~~~~~~~

The ``SOURCE`` directory can have an optional ``.build-maps.yaml`` config
file. This may contain the following values:

-  ``dest``: ``DEST`` path, relative to ``SOURCE``. Can be overridden on
   the command line.
-  ``clean``: ``true`` or ``false``. Can be overridden on the command
   line by ``--clean/--no-clean``