# Criando planetas do sistema solar com Blender

<img width="100%" src="http://kristinriebe.github.io/solarsystem-workshop/images/planets-long.png"/>

Estas instruções irão guiá-lo através da criação de planetas do sistema solar em 3D usando o Blender e sua API Python. No final, você terá escrito um script Python que cria seus planetas, suas órbitas e até anima sua rotação do zero de uma só vez. Se você ficar preso em algum momento, você pode entrar em contato comigo em
kristinriebe@gmail.com.

Divita-se!


## Materiais
Os seguintes arquivos são fornecidos/necessários:

* [planets-template.blend](https://github.com/kristinriebe/solarsystem-workshop/blob/master/planets-template.blend):
    um arquivo blender com configuração básica
* [create_planet.py](https://github.com/kristinriebe/solarsystem-workshop/blob/master/create_planet.py):
    um script simples para criar um planeta
* [planets.csv](https://github.com/kristinriebe/solarsystem-workshop/blob/master/planets.csv):
    arquivo com os parâmetros mais básicos para cada planeta do sistema solar e o sol
* [texturas](http://kristinriebe.github.io/solarsystem-workshop/textures.zip):
    diretório com mapas de textura dos planetas, 17 MB
* [rings.py](https://github.com/kristinriebe/solarsystem-workshop/blob/master/rings.py):
    contém duas funções para adicionar anéis em torno de Saturno e Urano
* (Extra:) [animate_camera.py](https://github.com/kristinriebe/blendertools/blob/master/animate_camera.py):
    um script que define a câmera se movendo ao longo de um caminho olhando para um determinado objeto

Outras coisas que você precisa:

* Blender (baixe em [blender.org](http://www.blender.org)). Estas instruções foram testadas apenas com a versão 2.75. Espero que funcionem com versões de ~ 2.6 em diante. Instale-o de forma que você possa iniciar o Blender diretamente da linha de comando.
* Navegador da Web com conexão à Internet, para verificar a documentação on-line ou Blender StackExchange ocasionalmente para obter ajuda

Ajuda, se você já estiver um pouco familiarizado com a interface gráfica do usuário do Blender. Veja por exemplo o [manual do Blender](http://www.blender.org/manual/) ou siga estes breves [vídeos básicos do Blender](https://cgcookie.com/course/blender-basics/).

Pronto? Vamos começar!

## Instruções básicas
* Abra `planets-template.blend` com o Blender na linha de comando:

```cmd
    `blender planets-template.blend`
```

    Vá até `File`->`Save As` e salve-o com um nome que você goste, exemplo: 
```
    planets.blend.
```

* Sua cena 3D é mostrada na área *3D view*, que é a grande área central.
    O modelo já contém uma câmera, uma lâmpada de ponto brilhante no centro para iluminar os planetas que você vai criar e um fundo de mundo azul escuro com um pouco de luz ambiente ligada para que as sombras não fiquem muito escuras. Você não vê seus efeitos agora, somente mais tarde, ao renderizar sua cena (`F12`).
  

* O layout da janela já está alterado para `Scripting` para você (na barra de menu superior, ao lado de `File`, `Render`, `Window` e `Help`).
	Vá para a área *Text Editor*, (área principal esquerda) e carregue um script selecionando `Text`->`Open Text Block` e escolhendo `create_planet.py`.

* Selecione `Texto`->`Executar Script` para executar o script. Uma esfera azul chamada
    `Planet-Earth` deve aparecer na sua *vista 3D*.

Se isso funcionar, você pode ir em frente, expandir o script e experimentar as seguintes tarefas. Se não funcionou, verifique a saída no console a partir do qual você iniciou o Blender para mensagens de erro.


## Experimenting
* Look in the Python script in your *Text area* for the `add_sphere`-function.
    Improve it such that the `size` (radius) of the sphere is provided as an 
    additional parameter. This should be used in Blender's 
    `primitive_uv_sphere_add` function to create the sphere.

* Provide e.g. `size=2` in the `main`-function when creating the sphere and 
    rerun your script. Check if the size has changed correctly. Note that the 
    script contains a `delete_objects`-function that removes all objects with 
    names matching `Planet*` from the scene. This is useful to cleanup before 
    recreating your planet.

* Adjust the material settings in the `add_material` function to create a planet with a different base color (e.g. red for `diffuse_color`) and no specular. Colors are given as RGB-triplets in Blender, so red would be 
`[1,0,0]`.


## More planets
So far, all these things can be done much faster via the interface. But such a script becomes very useful when creating more than one planet at once. Let's do this! 

* Write a read-routine to read planet and sun parameters from the provided 
  csv-file. Blender comes with bundled Python that also includes the csv-module for reading comma-separated value files, which makes this task very easy, e.g like this:  

    ```python
    with open(myfilename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        lines = [r for r in reader 
                    if not r[reader.fieldnames[0]].startswith("#")]
    ```
    Be careful to provide the correct (full) path to your csv-file.
    Alternatively you can also create a dictionary or array with parameters for different planets directly in your script. The parameters we use here are:  

    - `name` of the planet (or sun) 
    - `radius` of the planet (at equator), in km  
    - `art_distance` - artificial distance for good visual impression, 
                       in Blender units  
    - `distance` of the planet from the sun (semi-major axis)  
    - `flattening` of the planet  
    - `tilt` of the planet's axis  
    - `rotperiod` - time for rotation of the planet around its axis in 
                    days  
    - `eccentricity` of the planet's orbit  
    - `orbitperiod` - time for rotation of the planet on its orbit 
                          around the sun  
    - `texture` image for the planet  
    - `color` RGB triplet for the planet  

* In your `main`-function, write a loop to create more than one planet at 
  once, with different names and sizes. Use the column `art_distance` from the 
  provided csv-file to set the planets apart, e.g. along the +`x`-axis, 
  using `location` when adding the sphere.

* Take care to **scale down the radii** of the planets and the Sun to something between 0 and 10 Blender units, otherwise they may be too big to be visible in your Blender scene. (A basic size scale factor of 1/100,000 is a good value. For better visual impressions, increase the size of rocklike planets (Mercury, Venus, Earth, Mars) by a factor of 6, gas planets by a factor of 2.)

## Sun material adjustments
The Sun is special, since it is a self-glowing star. Thus its material needs to be adjusted. 
In general, you can always discover the available attributes for objects and materials via the *Python Console*: 

* First get the Sun-object: `obj = bpy.data.objects['Planet-Sun']`.  
* Type `obj.` and press `Ctrl`+`Space` in the console to get autocomplete suggestions.
* You can select the (first) material of your object using:   
  `mat = obj.material_slots[0].material`.
* Type `mat.` and press `Ctrl`+`Space` in the console to explore the available attributes. You can also set them here and see their effects immediately.
* In your script, include:  

    ```python
    # suppress any shadows and don't receive any
    mat.use_shadeless = True
    mat.use_shadows = False
    
    # allow light of point source to transmit through the sun's surface
    mat.use_cast_shadows = False
    mat.use_cast_buffer_shadows = False
    ```
* These settings could also be adjusted in the GUI, in the *Properties* area, *Material* tab, in sections `Shading` and `Shadow`. They ensure that the Sun does not receive any shadows and does not cast any.


## Colors and texture
* It's boring if all the planets have got the same color, so use a different color triplet for each planet. You can use the values from the file (parse them and convert them to a list of three values) or choose your own. Pass the color-triplet on to the `add_material` function, use it for `diffuse_color` in the script and rerun the script. Check, if every planet got its own color now.

* Adjust the position of your camera, so you get a good view on all your planets. (Check by going into *Camera View*: *View*, *Camera* or `Numpad 0`.)
  Render your scene with *Render* (top menu), *Render Image* or hit `F12`.

* Let's make the planets even prettier by adding an image texture map to each 
  of them. Most planet textures are freely available from NASA. Download your own texture maps or use those from the *textures*-directory. Adjust the name of the texture image for each planet in your csv-file/dictionary.

* Enable the `add_texture` function in the script's `main`-function. Make sure
  to provide the correct path to your images; otherwise your script will fail. 
  This function will load the image to a texture and map it using spherical coordinates.

* Rerun your script. The texture will only be visible when rendered, so render your scene again (`F12`). 


## Flattening
* Actually, planets are rarely exact spheres, but mostly a bit flattened in z-direction. This is described by the flattening parameter, given e.g. at Wikipedia for each planet. `0` flattening is a perfect sphere. Adjust each planet-sphere's `z`-scale by the factor `1-flattening` in your script.


## Axial tilt
* Improve your script even further by adding a tilt to the planet's axis. The axial tilt is defined as deviation from the axis perpendicular to the planet's orbit, with Earth's north pole pointing upwards.
  The true direction to which the planet's north pole points is usually given in Earth's coordinate system. For simplicity, the provided csv-file already gives the correct precalculated rotation angles around x, y and z-axes for each planet in the global coordinate system. Thus you only need to set:

    `rotation_euler.x = tilt_x/180. * pi`

  etc. The angles in the file are given in degrees, thus they must be converted to radians first using angle[rad] = angle[degree] / 180 * pi.
* If you do not want to set pi manually, import the `math` module to use `math.pi` instead.

## Extra: Add rings
* Saturn is popular for its prominent ring system. Such rings are a bit tricky to set up, so there are functions prepared that take care of this for you, stored in `rings.py`. This uses more advances techniques which we won't discuss here. In principle, for Saturn we add a disk with a hole and put a ring texture on top of it; for Uranus we create one circle with a thin thickness. 

* Copy the functions over or load them as a module by adding following lines at the beginning of your script:  

    ```python
    blend_dir = os.path.dirname(bpy.data.filepath)
    if blend_dir not in sys.path:
        sys.path.append(blend_dir)
    import rings
    import imp
    imp.reload(rings)
    ```
  A reload-line garante que o módulo de anéis seja recarregado toda vez que você executar o script. Isso é importante se você quiser fazer alterações personalizadas lá.

* Adicione chamadas para as funções `add_saturn_rings` e `add_uranus_rings` à sua função `main`. Netuno e Júpiter também têm anéis, mas são muito finos e vamos ignorá-los aqui.


## Simple orbit paths
* Adicione um círculo como caminho de órbita para cada planeta (não para o Sol!), usando `art_distance` para raio. Isso pode ser feito através da interface do Blender, `Add`, `Curve`, `Circle`.

* Verifique no log-output (janela *Info* no topo) qual função foi usada. Escreva sua própria função `add_orbit` para seu script para adicionar um círculo de órbita para cada planeta. Não faça um caminho de órbita para o Sol.

* Nomeie os caminhos da órbita, por exemplo 'Planet-Earth-Orbit' etc. Se você usar o mesmo prefixo 'Planet-' para as esferas do planeta, elas também serão excluídas automaticamente toda vez que você executar o script novamente.

* Ajuste a resolução dos círculos para aumentar o número de pontos da curva e, portanto, sua suavidade (por exemplo, 60). Você pode encontrar essa configuração na área *Propriedades* no lado direito, na guia *Dados* (símbolo de linha pequena). Adicione isso à sua função `add_orbit` também.

* Os círculos não podem ser vistos em uma imagem renderizada, a menos que você dê a eles alguma espessura. Assim, aumente a espessura dos círculos definindo a profundidade do chanfro para 0,006 ou mais. Na interface, essas configurações são ajustadas na área *Propriedades*, na aba de *Dados* (símbolo de curva de dobra). Aqui você pode procurar os atributos corretos do Blender para seu objeto de círculo e experimentar quais configurações ficam boas para você. Adicione-os ao seu script também.

* Você pode querer adicionar um material às suas órbitas e ajustar suas opções de sombra e sombreamento, para que as órbitas não projetem ou recebam sombras. Isto é conseguido exatamente com as mesmas configurações do material Sun que foi explicado acima.

* De fato, os planetas se movem em elipses, com o Sol em um dos pontos focais. Ignoraremos isso neste workshop e nos ateremos aos círculos simplificados.


## Extra: Orbit eccentricity
* Take the orbit eccentricity into account:
shift the orbit path, so the sun lies at one of the focal points of the ellipse. I.e.: shift it in x-direction by `a*ecc` (semi-major axis times eccentricity).
Scale the x-direction by a/distance, the y-direction by b/distance. b is the semi-minor axis, `b = a*sqrt(1-ecc**2)`.
(Don't forget `import math` for sqrt!)

* The orbit orientation is not yet correct - in truth, the orbit axes of the planets are not aligned! But taking the true orientation and also the inclination angle against e.g. Earth's orbit plane into account is beyond the scope of this workshop.


## Camera Animation (may be skipped here)
* Let's get the camera moving and add a camera path. Follow the next steps first via Blender's graphical interface, then check the log-output and the mouse-over tips for the functions and attributes to script this part as well. 
  - Add a circle via `Add`, `Curve`, `Circle`. Rename it to something like *CameraPath*. Set its location to (0,0,0) (`Alt`+`G`). Scale it such that there is still some distance between the circle and the sun (view it from top view to check this, `Numpad 7`; scale factor ~ 3.3 if using the scales from above).
  - Switch to `Edit Mode` (`Tab` key), drag the right-most point of the circle beyond the last planet. Switch back to `Object Mode` (`Tab` key).
  - Select your camera. In the *Properties* area, switch to the *Constraints* tab (chain-symbol). Click on `Add Object Constraint` and select `Follow Path` at the right side in the menu.
  - Choose your camera path as `target` for the Follow Path constraint and click `Animate Path`. 

* Split the *Python console* window horizontally and switch the new frame to *Timeline*. Click and drag the green line to move forward/backward in time. Can you see the camera moving?

* We are not yet done, the camera still looks away from the planets. We need to constrain its look-direction as well by adding an empty object to look at and another constraint: 
  - Add an empty using `Add`, `Empty`, `Cube`. This adds a cube-object that will not be rendered. Place it e.g. directly at Jupiter.
  - Add another constraint to your camera, choose `Track To`. This must be added below the Follow Path constraint. Select the just created empty object as `target`.

* When you move the time slider, you should now see the camera always looking to your empty object. 

* Do the same steps via scripting (also see `animate_camera.py`), in order to be able to reproduce them, when needed.

* The camera moves quite fast, you can slow it down by adjusting the animation manually:
  - Select the camera path, in *Properties* area switch to the *Curve data* tab and look for the `Evaluation time`. It is marked in green, because it is animated. Right click with the mouse and select `Clear keyframes`. 
  - In the timeline, choose frame 1. Set the curve's evaluation time to 0 and hit the `I` key while hovering over the evaluation time field. This sets a new animation keyframe (yellow). 
  - Now set the time to e.g. 500 frames, set the evaluation time of the curve to 100 and again hit `I`. This sets the second (final) keyframe. Your camera will now move along the whole path within 500 frames.

* Further details of animations can be adjusted in the *Graph Editor*, we'll look into this in the next sections.


## Orbit animation
We will now let the planets move along their orbit paths.

* First do it for one planet and its path in the interface, then code the steps by checking which functions were used in the log/hover info. 

* Reset the position of the planet to (0,0,0).

* Select the planet's orbit. In the *Properties* area, switch to the *Constraints* tab. Click `Add Object Constraint` and select `Follow Path`.

* As `target`, choose the planet's orbit path. This will constrain the movement of the planet to its path! It is important that the path's rotation angles are set to 0 here, otherwise the planet will "inherit" the rotation and appear upside down or otherwise rotated.

* Split the *Python Console* window horizontally (drag the triangle) and switch the new window to *Timeline* (if you haven't done so yet). Here you can set start and end frame of your animation and set the current frame. 

* In order to get the planet moving, we need to set animation keyframes on the *Evaluation time* of the path:
  - Select the orbit path. In *Properties* area switch to *Curve data* tab and look for the `Evaluation time`. If the field is green, then right click with the mouse and select `Clear keyframes` first to reset everything. 
  - In the timeline, choose frame 1. Set the curve's evaluation time to 0 and hit the `I` key while hovering over the evaluation time field. This sets a new animation keyframe (yellow). 
  - Now set the time in your timeline to some duration, e.g. 365 frames. 
  - Set the evaluation time of the curve to 100 and again hit the `I` key. This sets the second (final) keyframe. 
  - Click and drag the green line to move forward/backward in time between these two keyframes. Can you see the planets moving on their orbits now?

* Switch the *Python Console* window to *Graph Editor* to fine tune your animation curve. When you have the orbit path selected, you should see a curve that represents the interpolation of the evaluation time between your two set keyframes. You can use the mouse wheel to zoom in and out and `Shift`+ middle mouse button (`MMB`) to pan the area.

* Adjust the interpolation type of the curve in the right toolbar within the *Graph Editor* (enable with `T` key, if you cannot see it). At *Active keyframe*, choose `Interpolation`: `Linear` instead of the default Bezier curve. 

* Planets also do not rotate only once, but repeatedly. To achieve this, we could repeat setting keyframes at multiples of the orbitperiod and evalution time, but we can simplify it by using a graph modifier. At *Modifiers* in the toolbar select `Cycles` and select `Repeat with Offset` for *Before* and *After*. 

* That's (nearly) it! Your planet should move now continuously around the Sun on its orbit.

* There is still something not quite right: the planets of our solar system rotate counter-clockwise when seen from the northern side of the ecliptic, i.e. when seen from +z downwards in our Blender setup. But your planet currently moves in clock-wise direction! That's because your orbit circle has clock-wise direction. The easiest way to switch the orbit direction is to rotate it via the `y`-axis by `180` degrees. Add another rotation via its `z`-axis by `90` degrees to put the first point of the orbit along the +x-axis. Now `Apply` the orbit rotation: `Object`, `Apply`, `Rotation`. This applies the rotation to the points of the curve, they are all shifted now, and resets the rotation angles to 0. As mentioned already above, this is important for maintaining the correct planet orientation, otherwise the planet would inherit its orbits orientations.

* Include all these steps in your script for each planet. Set the keyframes according to the actual orbit rotation period given in the planets-file (`orbitperiod`). This value is given in days; use a timefactor to make your planets move slower or faster than 1 frame for 1 day.  
*Hint:* use the `keyframe_insert`-function, e.g. like this: 
`orbit.data.keyframe_insert(data_path="eval_time", frame=1)`

* If you used ellipses, then the speed of the planets should be faster closer to the sun (according to Kepler's laws). Blender does not easily allow to do that, so we will ignore this here. Just be aware that the true speed would be different than what we currently have.


## Rotation animation
Planets also rotate around their own axes, that's given by `rotperiod` in the file. This gets slightly more complicated than just adding animation keyframes for the `z`-rotation values, because the planet's axes are already tilted. If a z-rotation is added, then the planet would rotate around the current z-axis, not around the planet-axis. You can see this easily with Saturn and its rings or Earth, when changing the z-rotation value in the *3D view*, properties panel (enable with `N` if it is hidden).

We therefore use a special trick: we add an axes object for each planet and assign it the axial tilt. Then we clear the rotation of the planet and *parent* it to the axes object. This has the effect that the planet is basically unrotated, but inherits the tilt from its parent axes object. Now it's possible to keyframe the z-rotation of the planet!

* Use `Add`, `Empty`, `Arrows` in the interface and check from the log-output which function was used. Add this function in your script to create such arrows for each planet. Give it a name like `Planet-Earth-Axes` etc. for clear identification and to include it in the deleting process at the beginning of the script. 

* Assign the planet's tilt angles to the corresponding axes object.

* Clear the planet's rotation angles, i.e. set them to (0,0,0).

* Add the axes-object as parent to each planet. In the interface, select a planet, go to the *Properties* area, switch to the *Object* tab and look for `Parent` at the *Relations*-section. Here one can enter the axes object. Check the tooltip for the field to get an idea how to include setting the parent in your script.

* So far, nothing much has changed, the planets should still look the same. But now we are ready to add the rotation animation. Let's do it first in the interface:
  - Select a planet (not it's axes!).
  - In the *Timeline*, set the time to frame 1.
  - In *3D view*, go to the properties region at the right side and look for the rotation. The `z rotation` should be 0. Hover with the mouse over this field and press the `I` key to insert a keyframe.
  - Set the time to the rotation period, e.g. 10, set the rotation to 360 degrees and again insert a keyframe.
  - Move the time slider to see the planet rotating around its axis.
  - Switch your *Python Console* area (or any other) to the *Graph Editor* area, again set the `Interpolation` type to `Linear`.
  - Add a `Cycles` modifier and set Before and After values to `Repeat with Offset`, just the same way as for the orbit animation. This ensures a continuous and smooth planet rotation.

* Include these steps in your script, for each planet and for the Sun.


## Render your animation
* Render your animation by selecting `Render`, `Render Animation` in the top menu. The render resolution and other properties can be adjusted in the *Properties* area, at the *Render* tab (photo camera symbol). By default, Blender will create one png-image for each frame in the `tmp`-directory. 

* You can stop the rendering any time using the `Esc` key.

* Play your rendered animation with Blender, using `Render`, `Play Rendered Animation`.

* It is also possible to render your frames in the background, using the command line:

    ```
    blender -b <blender-file> -s 1 -e 600 -a
    ```

  This will render the frames 1 to 600.


## Further improvements
The solar system that we built up to now is still lacking in many details. Here are some suggestions to improve it further:

* Use real distances (scaled down by the same factor) for planets from the Sun.
* Switch on shadows for the lamp, so that rings and moons can cast shadows on their planets. This was switched off initially, because we had the planets unrealistically close to each other.
* Make orbits eccentric, use correct orbit orientation.
* Use true (non-uniform) speed along eccentric orbits.
* Use different image textures (e.g including clouds for Earth and Venus).
* Use animated textures, e.g. for the Sun to mimick evolving Sun spots, or for Earth to have different clouds evolving with time.
* Use UV-unwrapping for a more accurate mapping of textures to the sphere, especially at the poles.
* Add moons, minor planets and asteroids.
* Add stars in the background as reference system, maybe even the true stars from the sky, using a sky map.


If you made it this far: thanks for staying with me and congratulations! I hope you enjoyed this tutorial. For comments and suggestions, mistakes or questions, please send a mail to kristinriebe@gmail.com.

Interested in my final version of the Python script, which includes the steps explained in this tutorial? I've uploaded it here: [create_planet_final.py](http://www.kristin-riebe.de/materials/create_planet_final.py). It doesn't contain the 'Further improvements' steps, however, since so far I didn't have enough time to include them all. If you manage to finish these, I would appreciate it if you share *your* final version! :-)

# Referência:
[https://nafergo.github.io/manual-livre-blender/intro_materiais.html](https://nafergo.github.io/manual-livre-blender/intro_materiais.html)
