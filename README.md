# UPBGE Addons
###### Created by Guilherme Teres Nunes

These addons where created by me to help creating games using UPBGE (software [available here](download.upbge.org)). 

Feel free to open issues whenever needed or if you want to suggest some good addon.

Here is a list of the addons:

## Component Helper
###### File: **Addons/component_helper.py**

This addon will help you to handle your Python Components, such as creating or adding new components to the objects.
Once you installed the addon, go to **Logic Editor > Properties tab > Component Helper** to use the addon.

![](Images/component_helper_1.png)

In this image you can see an small example of the addon in action: 

- The first block will display all the existing Components (+ Script name) found in the .blend file. Note that you will need to click on the icon located on the top right (the arrows) to update the list.

- The second block is a small tool to create a new component: you just have to type the script name and the class name (white spaces will be automatically ignored and add the ".py" at the end of the script name is optional) and mark/unmark the two aditional options if you want to: (1) Include some instructions (comments) in the initial component code or (2) also add the created component to the current selected object.

## Easy Ragdoll
###### File: **Addons/easy_ragdoll.py**
Easy Ragdoll creation tool from an Armature and usage in game using a Python Component.
Properties > Physics > Ragdoll Panel (with an Armature selected)


## Console Output Display
###### File: **Addons/console_output_display.py**

Handle Python Errors may be very confused and complicated. Especially because blender may print thousands of times the same errors. Thinking in a way to fix this, I created this addon: An easy way to see what is wrong with your code. It will output the errors inside blender's interface and group together identical and sequential errors.

Of course, if you want to disable this for a moment, there is an option to do this.

![](Images/console_output_display.png)

In this image you can see the addon showing an output, which is something printed by the user, and 30 consecutive python errors grouped together (to make visualization easier).

A HUGE thanks to [marechal-p](https://github.com/marechal-p) which helped me a lot to figure out how to steal the console output from the blender's system console. This add-on would not be possible without him. 


## Input Mapping
###### File: **Addons/input_mapping.py**

This addon will help you to handle keyboard, mouse and joystick (wip) inputs. Once you installed the addon, go to **Properties > Scene > Input Mapping** to use the addon.

First you have to create one or more **Input Maps**, then, rename it and add as much keys as you want. Here is a small example:

![](Images/input_mapping_1.png)

In this image you can see a list of three maps: Forward, Side and Jump. The selected one (Forward) where created to handle Front and Back movements with the keys W and S and also Up and Down Arrows.

Once you setup your input maps, click in **Generate Script** and, then, you will be able to import these values in your own scripts by typing:

```
import InputMapping
```

If you want to acces the value of the Forward map, or if the user just pressed or released any key of this map, I can do:

```
value = InputMapping.Forward.value()
pressed = InputMapping.Forward.pressed()
released = InputMapping.Forward.released()
```

You can check which values can you add to the key field here:

https://pythonapi.upbge.org/bge.events.html#keys-constants

**Note:** Don't include the "bge.events." part. Also, the addon is a little bit smart so you don't need to type everything using Capitals or without spaces.
