Nino Violino

Temporary readme that will eventually get updated. 

Basically, it is an improvement over the old nino_pianino. The code is (supposed to be) cleaner, and I hope to package it a bit better. 
To use it, just do `python setup.py`, and if that doesn't work, then you just need midiutil, for the moment, so `pip install midiutil`. 

Midiutil seems to have a bug as of writing this. If it works fine then go with it. If it shows a "pop from empty list" error, here's how to fix it: 

Open /lib/python2.7/site-packages/midiutil/MidiFile.py (or wherever midiutil is installed)
Find the line with 'elif event.type == 'NoteOff':'
Replace the entire block below it with this: 

```
    if len(stack[str(event.pitch)+str(event.channel)]) > 1:
        event.time = stack[str(event.pitch)+str(event.channel)].pop()
        tempEventList.append(event)
    else:
        if len(stack[str(event.pitch)+str(event.channel)]) > 0:  ### MODIFIED TO CONDITIONALLY POP ###
            stack[str(event.pitch)+str(event.channel)].pop()
        tempEventList.append(event)
```

The entire article is here - https://cyberspy.io/articles/2017-10-29t150250-0400--maestro-cue-the-music/ - though it is unrelated to this repo (still, credit to them for the bugfix!)

Then, you need fluidsynth. `apt-get install fluidsynth` should do it. 
And finally, a soundfont. Any old soundfont bank will do it, but you should get a GM one. I personally use https://osdn.net/projects/sfnet_androidframe/downloads/soundfonts/SGM-V2.01.sf2/ for no real reason - just one of many I've tried. 


Then go `python block_generator.py` and wait a bit. It will generate a test.wav file, which yes, this is still a very early phase. 

TODO: 
  - Write a proper readme
  - Make this a pip package
  - Make it easier to use (some sort of a cli)
  - Use AI to make better songs
