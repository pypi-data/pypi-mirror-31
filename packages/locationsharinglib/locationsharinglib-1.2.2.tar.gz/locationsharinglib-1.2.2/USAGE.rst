=====
Usage
=====

To use locationsharinglib in a project:

.. code-block:: python

    from locationsharinglib import Service
    service = Service(username, password, 'connection.cookies')
    for person in service.get_all_people():
        print(person)
