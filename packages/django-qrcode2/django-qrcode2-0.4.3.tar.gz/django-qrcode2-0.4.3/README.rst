=====
django-qrcode2
=====

提供qrcode相关的filter和view，用pillow在本地生成

Quick start
-----------
1. Install::

    pip install django_qrcode2


2. Add "qrcode2" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'qrcode2',
    ]

3. [Optional] Include the qrcode2 URLconf in your project urls.py like this::

    url(r'^qrcode/', include('qrcode2.urls')),

4. No migration needed

5. Add filter to template like this::

    {% load qrcode2 %}

    <!-- if an view with name 'qrcode' is provided, 'src' will be an url, otherwise it's an base64 data blob -->
    <img src="{{ 'some text' | qrcode_src }}">

    <!-- insert an <img> with template inclusion -->
    {% include 'qrcode2/img.html' with text='hello' %}

