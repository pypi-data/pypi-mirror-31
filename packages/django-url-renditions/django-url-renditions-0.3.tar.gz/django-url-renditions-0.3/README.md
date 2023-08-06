# django-url-renditions

django-url-renditions allows to define rendition process to django url fields. This works pretty well with https://github.com/bradleyg/django-s3direct and Heroku.

It comes with a Graphene `Query` that enable renditions in your GraphQL schema.

## Install

```
pip install django-url-renditions
```

Add `url_renditions` to your `INSTALLED_APPS`


## Define your model


```python
from django.db import models
from url_renditions.fields import FileUrlWithRenditions

# django-url-renditions comes with a simple image resizer method.
# Look at the implementation if you need something more specific
from url_renditions.resize_image import ResizeImage

class Track(models.Model):
    original_artwork = models.URLField()
    artwork = FileUrlWithRenditions(
        source='original_artwork',
        use_job_runner=True, #  if we want to queue the job with django_rq
        renditions={
            'small': ResizeImage('80x80'),
            'medium': ResizeImage('300x300'),
        }
    )

```


That way, when a `Track` model get created with an `original_artwork`, `artwork` will be automatically polulated with two renditions: `small` and `medium`.

To access them, use:
```python
r = my_track.artwork.rendition_set.get(name='small')
print('url:', r.href, 'width:', r.width, 'height:', r.height)
```


## Graphql with Graphene

Add `url_renditions.graphql_schema.Query` to your root query.
```python
import graphene
import url_renditions.graphql_schema  # noqa

class Query(
        ...
        url_renditions.graphql_schema.Query,
        graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
```

Then when you ask for

```graphql
{
  track(id: "VHJhY2s6OA==") {
    artwork {
      renditions {
        medium {
          href
          width
          height
        }
      }
    }
  }
}
```

You get


```json
{
  "data": {
    "track": {
      "artwork": {
        "renditions": {
          "medium": {
            "href": "https://images.unsplash.com/photo-1474314170901-f351b68f544f",
            "width": 300,
            "height": 300
          }
        }
      }
    }
  }
}
```