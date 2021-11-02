# Sublime VintageEx
Sublime Text plugin that adds additional vim commands on top of the Vintage package.


https://user-images.githubusercontent.com/2120820/128536078-fcc6adbd-f8fe-4ad2-9685-2e67fb303fdd.mp4


### Installation
At the moment, there is no "official" pacakge to install this plugin, but you can still use it by copying `vintage_ex.py` into `<Sublime's Installation Path>/Packages/User`.

Afert you copied the file, just add these settings to your `key-bindings` file. (`Cmd+Shift+P -> Settings Key Bindings`)

```js
 // Overrides Sublime's default "Vintage prompt."
 { "keys": [":"],
      "context": [
          { "key": "setting.command_mode", "operand": true },
          { "key": "setting.is_widget", "operand": false }
      ],
    "command": "vintage_ex_prompt",
  },
  
  // Jumps back/forth between the previous and next cursor positions.
  { "keys": ["`", "`"],
      "context": [
          { "key": "setting.command_mode", "operand": true },
          { "key": "setting.is_widget", "operand": false }
      ],
    "command": "backticks_jump"
  },
```

And that's about it.
