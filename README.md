# pygraj / webgraj

GUI and web-UI for hi-fi berry music player.

This project was made to modernize my hi-fi tower from 90s. I got myself Raspberry Pi Zero W and Hi-Fi berry board (DAC hat for RPi) and connected it
as external input to my tower. The device was also equipped with 7inch LCD and 9 buttons (I have used digital multiplexer chip to use fewer GPIOS).

There are tons of great open source software which would fullfill all my needs, but where is the fun in that?

The software was written for Raspbian lite. I use headless Audacious as an actual player and control it via dbus API.

Code is written in python and PyQt library. There is a simple "source" menu (CD / MP3 / internet radio) and playlist with album art.

There is also a web interface written in webpy framework that allows to control player via web page from laptop or smartphone.



