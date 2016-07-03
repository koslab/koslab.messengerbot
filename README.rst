.. contents::

Introduction
============

``koslab.messengerbot`` makes writing 
`Facebook Messenger Bot <https://developers.facebook.com/docs/messenger-platform/product-overview>`_
easier by providing a framework that handles and abstract 
the Bots API. It is originally developed using `Morepath <http://morepath.rtfd.com>`_
as the web request processor, but this library should work with any Python web frameworks

Example: Writing An Echo Bot on Morepath
==========================================

Lets install ``morepath`` and ``koslab.messengerbot``

.. code-block:: bash

   pip install morepath
   pip install https://github.com/koslab/koslab.messengerbot.git

Now lets write our EchoBot in ``echobot.py``

.. code-block:: python

   import morepath
   from koslab.messengerbot.bots import Bots
   from koslab.messengerbot.request import WebObRequestAdapter

   from koslab.messengerbot.bot import BaseMessengerBot

   # bot implementation
   class EchoBot(BaseMessengerBot):

      GREETING_TEXT = 'Hello!. EchoBot, at your service!'
      STARTUP_MESSAGE = {'text': 'Hi!, lets get started!' }

      def message_hook(self, event):
          text = event['message'].get('text', '')
          self.send(recipient=event['sender'], message={'text': text})


   # webhook implementation on morepath

   bots = Bots(validation_token='<YOUR WEBHOOK VALIDATION TOKEN>',
       page_bots={
           '<PAGE ID>': (EchoBot, {'page_access_token':'<YOUR PAGE ACCESS TOKEN>'})
       })

   class App(morepath.App):
       pass
   
   @App.path(path='')
   class Root(object):
       pass
   
   @App.view(model=Root, name='webhook', request_method='GET')
   def webhook_get(context, request):
       req = WebObRequestAdapter(request)
       resp = bots.webhook(req)
       return morepath.Response(**resp.params())
   
   @App.view(model=Root, name='webhook', request_method='POST')
   def webhook_post(context, request):
       req = WebObRequestAdapter(request)
       resp = bots.webhook(req)
       return morepath.Response(**resp.params())

   if __name__ == '__main__':
      bots.initialize()
      morepath.run(App())

Start the bot

.. code-block:: bash

   python echobot.py

Finally proceed to follow the `Messenger Platform Getting Started
<https://developers.facebook.com/docs/messenger-platform/quickstart>`_
guide to get your bot configured and registered in Facebook.

Bot Configuration
==================

``POSTBACK_HANDLERS``
   Dictionary mapping of payload to object method that will handle the payload.
   Payload pattern may be defined as regex pattern. Default  value is:

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
   on payload regex pattern. To define the mapping, configure
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

``KombuBots`` provides an implementation of bot manager with AMQP queuing. To
use this, just switch ``Bots`` to ``KombuBots`` and provide it with the
uri to the transport. The queue is implemented using 
`Kombu <http://kombu.rtfd.org>`_, so you may also use 
`other transports
<https://kombu.readthedocs.io/en/latest/userguide/connections.html#amqp-transports>`_
that are supported by Kombu

.. code-block:: python

   bots = KombuBots(validation_token='<YOUR WEBHOOK VALIDATION TOKEN>',
       page_bots={
           '<PAGE ID>': (EchoBot, {'page_access_token': '<YOUR PAGE ACCESS TOKEN>'})
       },
       transport='amqp://<username>:<password>@<host>:5672')
