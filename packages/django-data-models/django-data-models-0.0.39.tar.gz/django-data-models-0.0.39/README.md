# Django Data Models

Provides DataModel that to load data for all DataModel child classes using `datamodels_loaddata`
and `datamodels_loaddata_default` command.

It allows to keep db synchronized with fixtures without writing thousands of migrations with fixtures reloading.

### Installation

```
pip install django-data-models
```


### API

```python
from datamodels import DataModel

class PostType(DataModel):
    ...

    class DataModelMeta:
        fixtures = ['django_datamodels_test_fixtures']
        default_fixtures = ['django_datamodels_test_default_fixtures']
        dependencies = ['auth.User']
        readonly = True
    ...
```

`DataModelMeta`'s attributes:

 - `fixtures` — data from these fixtures will be loaded on every `datamodels_loaddata` command
 - `default_fixtures` — data frome these fixtures will be loaded on every `datamodels_loaddata_default` command without
   updating existing objects.
 - `dependencies` — set up a dependecies that must be loaded before current model.
 - `readonly` — model could not be modified/deleted and will raise an `DataModelsReadOnlyException`


### Commands
 - `datamodels_loaddata` loads fixtures given in `DataModelMeta.fixtures`. You can provide model labels f.e.
 `datamodels_loaddata app1 app2 app3.Model1`
rr

### Settings
 - `DATAMODELS_LOADDATA_COMMAND_CLASS` — class path (for django 1.9+) for example `django.core.management.commands.loaddata.Command`
    or a command name (1.8+) like `loaddata` to be used as a command to load fixtures. By default it is `loaddata`.


<a href="https://travis-ci.org/TriplePoint-Software/django-data-models">
<img src="https://travis-ci.org/TriplePoint-Software/django-data-models.svg?branch=master">
</a>
