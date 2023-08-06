
Usage
=====

Add url:

    url(r'^docs/', include('django_rest_swagger_docstring.urls', namespace='docs')),


Notes
=====

This is similar to django-rest-swagger's
[YAML docstrings feature](http://django-rest-swagger.readthedocs.io/en/stable-0.3.x/yaml.html)
which was
[deprecated in 2.0](http://marcgibbons.com/django-rest-swagger/#changes-in-20).

For the most simple / purely RESTful cases the
`rest_framework.schemas.SchemaGenerator` is sufficient.
