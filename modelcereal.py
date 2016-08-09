"""
Fully serializes django models and their related and M2M fields.

This is in contrast to just outright using a django serializer
which simply serializes foreign keys as the key itself without
also serializing the foreign object, meaning it cannot be
deserialized without access to the original data source.

YMMV, AYOR.
"""
import collections

from django.db.models import fields
import django.core.serializers

models = list()

def add_object(obj, replace_fields=None, ignore_models=None, invoker=None):
    if obj is not None and (not ignore_models or obj._meta.model_name not in ignore_models):
        for field in obj._meta.fields:
            if isinstance(field, fields.related.RelatedField):
                instance = getattr(obj, field.name)
                if instance != invoker and instance not in models:
                    add_object(instance, replace_fields=replace_fields, ignore_models=ignore_models)
            field_key = obj._meta.model_name + '.' + field.name
            if replace_fields is not None and field_key in replace_fields:
                setattr(obj, field.name, replace_fields[field_key])
        for m2m_field in obj._meta.local_many_to_many:
            for m2m_obj in getattr(obj, m2m_field.name).all():
                add_object(m2m_obj, replace_fields=replace_fields, ignore_models=ignore_models, invoker=obj)
        if obj not in models:
            models.append(obj)
    
def serialize(objects, replace_fields=None, ignore_models=None, *args, **kwargs):
    for obj in objects:
        add_object(obj, replace_fields=replace_fields, ignore_models=ignore_models)
    return django.core.serializers.serialize('json', models, *args, **kwargs)
