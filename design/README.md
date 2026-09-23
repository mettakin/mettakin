# Design sources

`og.html` is the source of `static/og.png`, the image shown when someone shares a Mettakin link. To change it, edit the HTML and render it again:

```sh
google-chrome --headless --hide-scrollbars --window-size=1200,627 --screenshot=static/og.png "file://$PWD/design/og.html"
```
