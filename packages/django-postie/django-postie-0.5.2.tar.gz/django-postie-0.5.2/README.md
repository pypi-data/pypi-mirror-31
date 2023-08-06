# django-postie

This project allows you to send emails and manage them in the admin panel.

Basic example to use:


```python
# your_module.py

from postie.shortcuts import send_mail

send_mail(
    event='MAIL_EVENT',
    recipients=['email@email.com', 'email1@email1.com'],
    context={
        'var1': 'variable context',
        'var2': 'another value'
    },
    from_email='noreply@email.com',
    attachments=[{
        'file_name': open('path-to-the-file')
    }]
) 
```


### Available settings

`POSTIE_TEMPLATE_CHOICES` - Tuple of tuples. Where the first value is the 
value to use in code and second is stored in DB. 

`POSTIE_TEMPLATE_CONTEXTS` - dictionary with template choices as keys and 
dictionaries as values

`POSTIE_INSTANT_SEND` - whether to send letters instantly or to use celery 
task. If `False` `celery` is required.
