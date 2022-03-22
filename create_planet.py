import bpy
import os
import sys
import csv
import math
blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)
import rings
import imp
imp.reload(rings)


def delete_planets():
    """Delete objects with names containing 'Planet*'"""
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern='Planet*')
    n = len(bpy.context.selected_objects)
    bpy.ops.object.delete()

    print("%d sphere(s) were deleted." % n)

    return


def delete_unused_materials():
    """Delete all unused materials (done automatically after reload)"""
    # This is done anyway when closing and reopening Blender or reloading
    # the blend-file.
    # But since one may want to rerun this script many times, it can be
    # nicer to remove the unused materials automatically, after deleting
    # objects.
    i = 0
    for mat in bpy.data.materials:
        if mat.users == 0:
            name = mat.name
            bpy.data.materials.remove(mat)
            i = i + 1
            print("Deleted material ", name)

    print("%d materials were deleted." % i)

    return


def delete_unused_textures():
    """Delete all unused textures"""
    # Be careful, since this really deletes all textures which are not currently 
    # used. It may thus delete more than you wanted.
    i = 0
    for tex in bpy.data.textures:
        if tex.users == 0:
            name = tex.name
            bpy.data.textures.remove(tex)
            i = i + 1
            print("Deleted texture ", name)
            
    print("%d textures were deleted." % i)
    
    return


def read_csv(filename):
    """Read content of a csv-file into a dictionary"""
    # With keys taken from first row, using csv-module.
    # Assumes a "usual" csv-file, comma-separated, text enclosed within "".
    # If you have a different csv-format, check the csv.Dictreader 
    # documentation on how to adjust the commands below.
  
    if not os.path.isfile(filename):
        print("Arquivo %s não encontrado!" % filename)
        raise RuntimeError("read_csv: parando o script porque o arquivo não foi encontrado.") 

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        lines = [r for r in reader if not r[reader.fieldnames[0]].startswith("#")]
                    
    return lines


def add_texture(mat, imgname):
    """Add image texture to given material, map as sphere
    mat -- material to which texture shall be added
    imgname -- name of texture image file, including file path
    """
    
    # create texture, add image
    img = bpy.data.images.load(imgname)
    tex = bpy.data.textures.new(imgname, type='IMAGE')
    tex.image = img
    
    # add texture to material, set mapping
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'ORCO'
    mtex.mapping='SPHERE' 

    return tex, mtex


def create_orbit_material(name, color=[1,0,0,1]):
    """Create a material for the orbits
    name -- basename to be added to material name
    color -- list of 3 color values: red, green and blue
    """
    matname = 'Material-'+name
    mat = bpy.data.materials.new(matname)
    mat.diffuse_color = color
    mat.specular_intensity = 0.1
    
    # orbits shall not cast any shadows
    # mat.use_cast_shadows = False
    # mat.use_cast_buffer_shadows = False
    # do not receive shadows from any objects (e.g. planets)
    # mat.use_shadows = False 
    
    # problem: pixel artefacts at border of light-shadow on the orbi,
    # thus maybe rather make orbit paths shadeless?
    # mat.use_shadeless = True
    mat.diffuse_color = [0.3,0.3,0.3,1]

    return mat    


def add_material(obj, name, color=[1,0,0,1]):
    """Add material to an object
    obj -- object to which the material is appended
    name -- basename to be added to material name
    color -- list of 3 color values: red, green and blue
    """
    
    # create a material
    matname = 'Material-'+name
    mat = bpy.data.materials.new(matname)
    mat.diffuse_color = color
    mat.specular_intensity = 0.1

    # add material to the object
    obj.data.materials.append(mat)

    return mat


def add_sphere(name, radius, location):
    """Add sphere to current scene at given location
    name -- name for new sphere object
    location -- location for the new sphere
    """
    
    # add object
    bpy.ops.mesh.primitive_uv_sphere_add(segments=72, ring_count=36, radius=radius,location=location, rotation=(0,0,0))
    
    # get object
    obj = bpy.context.object
    
    # set name, smooth shading
    obj.name = name
    bpy.ops.object.shade_smooth()
       
    print("Sphere '%s' created." % name)
   
    return obj


def add_circle(name, radius, location=(0,0,0), resolution=16):
    """Add a curve circle with given radius at given location
    name -- name for the new curve object
    location -- origin of the curve
    radius -- radius of the circle
    """
    
    # add circle
    bpy.ops.curve.primitive_bezier_circle_add(
        radius=radius, location=location)
    
    # get object
    obj = bpy.context.object
    
    # set name, resolution
    obj.name = name
    obj.data.resolution_u = resolution
        
    return obj


def add_flattening(obj, flattening):
    """Add flattening of planet-sphere
    obj -- sphere object that shall be flattened
    flattening -- amount of flattening (between 0 and 1)
    """
    
    # radius in file is equatorial radius, flattening thus affects z-scale
    obj.scale.z = (1-flattening) * obj.scale.z
    
    return


def create_axis_parent(name, planetobj):
    """Add empty (arrows) as parent object for the planet and tilt it.
    This allows to add planet rotation around itself (its z-axis) later on.
    name -- basename of the planet
    planetobj -- planetobj
    """
    location = planetobj.location
    bpy.ops.object.empty_add(type='ARROWS', radius=1, location=location)
    emptyobj = bpy.context.object
    emptyobj.name = 'Planet-'+name+'-Axes'
    
    planetobj.location = (0,0,0)
    planetobj.parent = emptyobj
    
    # add line along z-axis of the planet, just for checking visually
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01,
        depth=1.4*planetobj.dimensions.x, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = 'Planet-'+name+'-Pole'
    obj.parent = emptyobj
    
    # hide in render
    # especially important, if it is the sun!
    # (otherwise its shadow hides the light from the lamp!)
    #if planetobj.name == 'Planet-Sun':
    obj.hide_render = True
    
    return emptyobj


def add_axial_tilt(obj, tilt, angx, angy, angz):
    """Add axial tilt to given object.
    obj -- either the planet sphere or a parent object (axis-object)
    tilt -- axial tilt, in degrees, deviation from z-axis
    angx, angy, anz -- tilt angles, in degrees
    """
    
    # NOTE: for simplicity we tilt here all planet axes in the same direction.
    # Actually, they all point in different directions, see e.g.
    # https://en.wikipedia.org/wiki/Axial_tilt
    #obj.rotation_euler.y = tilt/180. * math.pi
    
    # alternatively: use correct x, y, z rotation values from the file
    obj.rotation_euler.x = angx/180.*math.pi
    obj.rotation_euler.y = angy/180.*math.pi
    obj.rotation_euler.z = angz/180.*math.pi

    return


def add_orbit(orbitname):
    """Add orbit path as a circle
    orbitname -- name of the orbit path
    """
    
    orbitobj = add_circle(orbitname, d, location=(0,0,0), resolution=100)
      
    # switch direction (because most planets rotate counter-clockwise when 
    # seen from earth's northern side)
    bpy.context.scene.objects.active = orbitobj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.switch_direction()
    bpy.ops.object.mode_set(mode='OBJECT')
        
    # rotate orbit path to start at +x
    orbitobj.rotation_euler.z = math.pi
    # apply rotation, to avoid problems with axis orientation later on
    bpy.context.scene.objects.active = orbitobj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
           
    # add bevel depth to make lines visible
    orbitobj.data.fill_mode = 'FULL'
    orbitobj.data.bevel_depth = 0.006
    orbitobj.data.bevel_resolution = 4

    # TODO: orbits are actually ellipses

    return orbitobj


def add_orbit_animation(orbitobj, startframe, duration):
    """Add animation for the orbit path.
    This only works if the planet is connected to the 
    orbit path via a Follow_Path constraint.
    orbitobj -- orbit path object
    startframe -- first frame, for start of animation
    duration -- duration for complete orbital period, number of frames
    """
    
    orbitobj.data.use_path = True
    orbitobj.data.path_duration = 100
    
    # insert keyframes for evaluation time
    orbitobj.data.eval_time = 0
    orbitobj.data.keyframe_insert(data_path="eval_time", frame=startframe)

    endframe = startframe + duration
    orbitobj.data.eval_time = 100
    orbitobj.data.keyframe_insert(data_path="eval_time", frame=endframe)

    # Change interpolation type for animation curve to linear,
    # don't want to slow down the orbit at the wrong point.
    # Add cycles-modifier for repeating the orbit animation.
    # (modifier only works if Follow_Path is used, but not, 
    # if we only use parenting!)
    for fcu in orbitobj.data.animation_data.action.fcurves:
        if fcu.data_path == 'eval_time':
            for p in fcu.keyframe_points:
                p.interpolation = 'LINEAR'
            mod = fcu.modifiers.new('CYCLES')
            mod.mode_before = 'REPEAT_OFFSET'
            mod.mode_after = 'REPEAT_OFFSET'
                                    
    return


def add_rotation_animation(obj, startframe, rottime):
    """Add rotation of planet around its axis
    obj -- planet object or an axis object, if exists
    startframe -- first frame, for start of animation
    rottime -- time for one rotation around its axis, number of frames
    """
    # NOTE: Only works if the planet's rotation axis points along the 
    # global z-axis. If the planet's axis is tilted, then add an axis-parent 
    # and tilt this parent, but keep the planet-object's axis unrotated. 
    # Otherwise the tilted axis would precess around global z-axis. 
    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=startframe)

    endframe = startframe + rottime
    obj.rotation_euler.z = 2*math.pi
    obj.keyframe_insert(data_path='rotation_euler', frame=endframe)

    # adjust animation graph: type linear, repeat
    for fcu in obj.animation_data.action.fcurves:
        if fcu.data_path == 'rotation_euler':
            for p in fcu.keyframe_points:
                p.interpolation = 'LINEAR'
            mod = fcu.modifiers.new('CYCLES')
            mod.mode_before = 'REPEAT_OFFSET'
            mod.mode_after = 'REPEAT_OFFSET'
            
    return


if __name__ == '__main__':

    dir = os.path.dirname(bpy.data.filepath) + os.sep
#    filename = dir + 'Planets-simple.csv'
    filename = dir + 'planets.csv'
    imgpath = dir + 'textures' + os.sep

    # size scale factor
    sizescale_basic = 1/100000.

    # additional factors for sizes (enlarge planets for better visibility)
    sizefactor_rockplanet = 2 #6
    sizefactor_gasplanet = 2 #2

    # time factor to convert from days to number of frames
    timefactor = 80
    
    # clear things first
    delete_planets()
    delete_unused_materials()
    delete_unused_textures()
    
    # read planet data from file (including sun)
    planets = read_csv(filename)
    
    # make one material for all orbits of planets
    orbitmaterial = create_orbit_material('Material-Orbits', color=[0.3,0.3,0.3,1])
        
    for planet in planets:
        
        name = planet['name']
        objname = 'Planet-' + name

        if name in ['Mercurio', 'Venus', 'Terra', 'Marte']:
            sizescale = sizescale_basic * sizefactor_rockplanet
        elif name != 'Sun':
            sizescale = sizescale_basic * sizefactor_gasplanet
        else:
            sizescale = sizescale_basic
        
        radius = float(planet['radius']) * sizescale
        
        # just put at some distance, not the true one
        d = float(planet['art_distance'])
        location = (d,0,0)

        # parse color value
        color = [float(c) for c in planet['color'][1:-1].split(',')]
                
        # create planet sphere and add material
        obj = add_sphere(objname, radius, location)
        mat = add_material(obj, name, color=color)
        
        # add texture
        imgname = imgpath + planet['texture']
        add_texture(mat, imgname)

        # add flattening of planet-sphere
        flattening = float(planet['flattening'])
        add_flattening(obj, flattening)
        
        # add axis tilt
        # via a parent for the axis-orientation,
        # This allows to add planet rotation around itself (its z-axis) later on.
        axisobj = create_axis_parent(name, obj)
        
        tilt = float(planet['tilt'])
        tiltx = float(planet['tilt_x'])
        tilty = float(planet['tilt_y'])
        tiltz = float(planet['tilt_z'])
        add_axial_tilt(axisobj, tilt, tiltx, tilty, tiltz)
        
        # add orbit paths, with planet distance as radius
        # link with orbit material defined outside of loop
        if (name != 'Sun'):
            
            orbitname = 'Planet-' + name + '-Orbit'
            orbitobj = add_orbit(orbitname)
            
            # add Follow_Path to planet, to stick it to its orbit
            axisobj.location = (0,0,0)
            c = axisobj.constraints.new(type='FOLLOW_PATH')
            c.target = orbitobj

            # add orbit animation
            startframe = 50
            duration = int( float(planet['orbitperiod'])*timefactor  + 0.5)
            add_orbit_animation(orbitobj, startframe, duration)
            
        # add rotation of planet around its axis
        # Beware of axis tilt!!  
        startframe = 1
        time = int(  float(planet['rotperiod'])*timefactor  + 0.5)
        add_rotation_animation(obj, startframe, time)

        # add Saturn rings
        img = imgpath + 'Saturn_rings_thin.png'

        if name == 'Saturn':
            rings.add_saturn_rings(obj, name, sizescale, img)
        
        # add Uranus ring
        if name == 'Uranus':
            rings.add_uranus_rings(obj, name, sizescale)

    # sun adjustments
    obj = bpy.data.objects['Planet-Sun']
    sunmat = obj.material_slots[0].material
    sunmat.use_shadows = False # otherwise orbits cast shadow on sun-surface
    sunmat.use_shadeless = True # now also no shadow received
    
    # allow light of point source to transmit through the sun's surface
    sunmat.use_cast_shadows = False
    sunmat.use_cast_buffer_shadows = False
    