# hikatana
Tools for the Foundry's Katana

### How to Install ###
#### Linux ####
1. git clone https://github.com/ireneher/hikatana.git
2. cd hikatana
3. source setup.sh

This method works per session. If desired, modify ~/.bashrc to include the contents of setup.sh, in order to permanently append to path.

### Tools ###
#### HIMeshLights ####
SuperTool to create one mesh light per collected mesh (according to input CEL). Each Light Rig is driven by a Master Material, so all lights can be modified at once, but also accept local overrides.
![HIMeshLights](doc/images/meshlights/ui.png)

For the set-up above,  with only HIMeshLights providing all the lights in the scene, this is the result: 
![HIMeshLights](doc/images/meshlights/example.png)

[Model Credit](https://sketchfab.com/3d-models/fairy-lights-6167832a8ea04d0bb637315b45fb2d72 )

