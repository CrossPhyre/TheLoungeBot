# TheLoungeBot
This Discord bot is built in Python and contains custom functionality. Currently, this functionality includes functionality to playback audio from YouTube videos and functionality to manage tasks.

### Setup
Below are some notes about how to set up this code to work for your bot.

#### Add Your Bot Token
Add a file named .\shared\secrets\\_\_init\_\_.py directory that contains a "bot_token" property that is set to a string representing your bot's token.

#### ffmpeg Dependency
This implementation depends on an ffmpeg executable. This file is too large to include directly in the repository, so this executable must be included at the .\shared\dependencies\ffmpeg\ directory.
