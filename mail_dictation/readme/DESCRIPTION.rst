Adds a microphone button to the chat composer, after the attachment button:
Discuss channels and chat windows, and the chatter of the records, also while a
message is edited. The user dictates the message instead of typing it.

* A click starts recording, and another click stops it and sends the audio for
  transcription. While it records, the button turns red and counts the
  seconds; Esc discards the recording, and nothing is sent.
* A recording stops by itself, and is transcribed, at two minutes.
* The text lands at the cursor, the way an emoji does, with a space between it
  and the words next to it. Nothing is ever sent by itself: the user checks the
  text and sends it.
* The text belongs to the conversation where it was recorded: when another one
  is shown before the text arrives, it waits in the box of the first one.
* No language is imposed: the transcription service detects it.
* Only internal users can dictate.

The Odoo server sends the audio to the transcription service chosen in the
settings. Each service comes with its own module, such as
``mail_dictation_openai``. The server keeps neither the audio nor the text, and
logs neither.
