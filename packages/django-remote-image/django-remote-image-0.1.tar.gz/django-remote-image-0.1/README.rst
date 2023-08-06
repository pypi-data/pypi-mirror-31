=====
Django-remote-image
=====

Django-remote-image is a Django app that adds a new form field for images.
The default widget is a text input, that accepts a URL of a image.

The image is downloaded and can be passed to a ``ImageField`` in a model. Pillow needs to be installed.

It is possible to whitelist and blacklist file extensions.

Examples are shown below.

Quick start
-----------

   $ pip install django-remote-image

Using
-----------
Using the field in a form:

.. code:: python
    import remote_image import RemoteImageField

    class ExampleForm(forms.Form):
        image = RemoteImageField()

Whitelisting file extensions (only the ones in the list will be permitted):

.. code:: python
    import remote_image import RemoteImageField

    class ExampleForm(forms.Form):
        image = RemoteImageField(ext_whitelist=['png', 'jpg'])

Blacklisting file extensions (the ones in the list will be blocked):

.. code:: python
    import remote_image import RemoteImageField

    class ExampleForm(forms.Form):
        image = RemoteImageField(ext_blacklist=['png', 'jpg'])