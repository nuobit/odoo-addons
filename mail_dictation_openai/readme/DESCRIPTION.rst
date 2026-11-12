Adds an OpenAI-compatible transcription service to ``mail_dictation``. The Odoo
server sends the audio to ``POST <address>/audio/transcriptions``, with the
configured model and key, and puts the text it gets back in the chat.

It works with any service that speaks this API, such as OpenAI, Groq or
DeepInfra. No language is sent: the service detects it.

The server keeps neither the audio nor the text, and logs neither.
