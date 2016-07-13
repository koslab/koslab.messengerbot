.. contents::

Introduction
============

``koslab.messengerbot`` makes writing 
`Facebook Messenger Bot <https://developers.facebook.com/docs/messenger-platform/product-overview>`_
easier by providing a framework that handles and abstract 
the Bots API. It is originally developed using `Morepath <http://morepath.rtfd.org>`_
as the web request processor and the default hub implementation is on morepath, but this library should
work with any Python web frameworks

Example: Writing An Echo Bot 
=============================

Lets install ``koslab.messengerbot``

.. code-block:: bash

   pip install koslab.messengerbot

Now lets write our EchoBot in ``echobot.py``

.. code-block:: python

   from koslab.messengerbot.bots import Bots
   from koslab.messengerbot.bot import BaseMessengerBot

   # bot implementation
   class EchoBot(BaseMessengerBot):

      GREETING_TEXT = 'Hello!. EchoBot, at your service!'
      STARTUP_MESSAGE = {'text': 'Hi!, lets get started!' }

      def message_hook(self, event):
          text = event['message'].get('text', '')
          self.send(recipient=event['sender'], message={'text': text})


And now lets write a hub config file, ``config.yml``.

.. code-block:: yaml

   webhook: webhook
   use_message_queue: false
   message_queue: amqp://guest:guest@localhost:5672//
   hub_verify_token: <MY-VERIFY-TOKEN>
   bots:
     - page_id: <PAGE-ID>
       title: EchoBot
       class: echobot:EchoBot
       access_token: <PAGE-ACCESS-TOKEN>


Start the bot

.. code-block:: bash

   messengerbot_hub config.yml

Finally proceed to follow the `Messenger Platform Getting Started
<https://developers.facebook.com/docs/messenger-platform/quickstart>`_
guide to get your bot configured and registered in Facebook.

Bot Configuration
==================

``POSTBACK_HANDLERS``
   Dictionary mapping of payload to object method that will handle the payload.
   Default value is:

   .. code-block:: python

      POSTBACK_HANDLERS = {}

``GREETING_TEXT``
   `Greeting text
   <https://developers.facebook.com/docs/messenger-platform/thread-settings/greeting-text>`_ 
   for new threads. Default value is:

   .. code-block:: python

      GREETING_TEXT = 'Hello World!'

``STARTUP_MESSAGE``
   Message object to be sent when **Get Started** menu is clicked. Default value is:

   .. code-block:: python

      STARTUP_MESSAGE = { 'text' : 'Hello World!' }

``PERSISTENT_MENU``
   `Persistent menu <https://developers.facebook.com/docs/messenger-platform/thread-settings/persistent-menu>`_ ``call_for_action`` buttons configuration. Default value is:

   .. code-block:: python

      PERSISTENT_MENU = [{
         'type': 'postback',
         'title': 'Get Started',
         'payload': 'messengerbot.get_started'
      }]
 

Bot Hooks
==========

Following are the list of hooks that can be implemented on the bot

``message_hook``
   Handles `Message Received
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/message-received>`_ 
   and `Message Echo
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/message-echo>`_
   event.

``postback_hook``
   Handles `Postback Received
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/postback-received>`_
   event. This hook have a default implementation which triggers methods based
   on payload value. To define the mapping, configure
   ``POSTBACK_HANDLERS`` class variable.


``authentication_hook``
   Handles `Authentication
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/authentication>`_
   event. 

``account_linking_hook``
   Handles `Account Linking
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/account-linking>`_
   event.

``message_delivered_hook``
   Handles `Message Delivered
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/message-delivered>`_
   event.

``message_read_hook``
   Handles `Message Read
   <https://developers.facebook.com/docs/messenger-platform/webhook-reference/message-read>`_
   event

Send API
=========

``BaseMessengerBot`` class provide a ``send`` method to send responses to
Facebook Messenger Bot service. Parameters are:

``recipient``
   Recipient object. Eg: ``{ 'id': '12345678'}``

``message``
   Message object. Refer to `Facebook Send API reference
   <https://developers.facebook.com/docs/messenger-platform/send-api-reference>`_
   for supported messages

``sender_action``
   Sender actions. Supported values: ``mark_seen``, ``typing_on``,
   ``typing_off``

**Note:** If ``message`` is defined, ``sender_action`` value will be ignored.

A convenience method ``reply`` can also be used to send a response. Parameters
are:

``event``
   Event object

``message``
   Accepts string, callable or message object. Strings are automatically 
   converted into message object. Callable will be called with the event 
   object as its parameter.

Postback Payload
================

Postback values may be a JSON object or a string. In the case of
Postback in JSON object format, an ``event`` key is required for routing postbacks
to the right handler by ``postback_hook``. For string postback values, the
whole string is treated as the event key.

Session 
========

Session Management is provided through a thin wrapper around `Beaker Cache
<http://beaker.readthedocs.io/en/latest/caching.html>`_. Current conversation
session variable may be acquired through ``get_session`` method on
``BaseMessengerBot`` class. Session object is ``dict``-like and may be treated
as such.

.. code-block:: python

      def message_hook(self, event):
          session = self.get_session(event)

Messenger Bot with AMQP
========================

AMQP queuing is supported by the hub process. To use this, in ``config.yml``
simply set ``use_message_queue`` to ``true`` and configure the transport uri 
to the message queue on ``message_queue`` setting. The queue is implemented using 
`Kombu <http://kombu.rtfd.org>`_, so you may also use 
`other transports
<https://kombu.readthedocs.io/en/latest/userguide/connections.html#amqp-transports>`_
that are supported by Kombu

.. code-block:: yaml

   use_message_queue: true
   message_queue: amqp://guest:guest@localhost:5672//

   
Conversation API
=================

**NOTE:** This is a draft spec. Not yet implemented. Inputs are welcomed.

Spec

.. code-block:: yaml

   conversation: myconversation
   steps:
      - message: What is your name?
        type: text
        store: name
      - message: Please share your photo
        type: image-attachment
        store: photo
      - message: Please share your location
        type: location-attachment
        store: location
      - message: 
          - type: generic-template
            elements:
               - title: Summary
                 subtitle: Summary
                 image_url: ${data['photo']['url']}
                 buttons: 
                     - type: postback
                       title: Save
                       payload: myconversation.save 

            
