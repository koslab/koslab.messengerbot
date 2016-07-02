.. contents::

Introduction
============

``koslab.messengerbot`` makes writing Facebook Messenger Bot easier by providing
a framework that handles and abstract the webhook API. It is originally
developed using Morepath (http://morepath.rtfd.com) as the web request 
processor, but this library should work with any Python web frameworks

Example: Writing An Echo Bot on Morepath
==========================================

Lets install ``morepath`` and ``koslab.messengerbot``

.. code-block:: bash

   pip install morepath
   pip install https://github.com/koslab/koslab.messengerbot.git

Now lets write our EchoBot in ``echobot.py``

.. code-block:: python

   import morepath
   from koslab.messengerbot.webhook import WebHook
   from koslab.messengerbot.request import WebObRequestAdapter

   from koslab.messengerbot.bot import BaseMessengerBot

   # bot implementation
   class EchoBot(BaseMessengerBot):

      def message_hook(self, event):
          text = event['message'].get('text', '')
          self.send(recipient=event['sender'], message={'text': text})



   # webhook implementation on morepath

   webhook = WebHook(validation_token='<YOUR WEBHOOK VALIDATION TOKEN>',
       page_bots={
           '<PAGE ID>': EchoBot('<YOUR PAGE ACCESS TOKEN>')
       })

   class App(morepath.App):
       pass
   
   @App.path(path='')
   class Root(object):
       pass
   
   @App.view(model=Root, name='webhook', request_method='GET')
   def webhook_get(context, request):
       req = WebObRequestAdapter(request)
       resp = webhook.handle(req)
       return morepath.Response(**resp.params())
   
   @App.view(model=Root, name='webhook', request_method='POST')
   def webhook_post(context, request):
       req = WebObRequestAdapter(request)
       resp = webhook.handle(req)
       return morepath.Response(**resp.params())

   if __name__ == '__main__':
      morepath.run(App())

Start the bot

.. code-block:: bash

   python echobot.py

Finally proceed to follow the `Messenger Platform Getting Started
<https://developers.facebook.com/docs/messenger-platform/quickstart>`_
guide to get your bot configured and registered in Facebook.


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
   event.

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
