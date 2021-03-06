import bpy


def add_camera_path(pathname, radius, location):
    """Add a circle as camera path
    pathname -- name of the object that shall be created
    radius -- radius of the circle
    location -- position of the circle, (x,y,z)-triplet
    """
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=location)

    # get object
    ob = bpy.context.object

    # switch direction (I just like it better that way)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.switch_direction()
    bpy.ops.object.mode_set(mode='OBJECT')

    # set name
    ob.name = pathname

    return ob


def add_trackto_object(tracktoname, location):
    """Add an object as viewpoint for the camera
    tracktoname -- name of the object that shall be created
    location -- position of this object, (x,y,z)-triplet
    """

    # add empty cube, at (0,0,0)
    bpy.ops.object.empty_add(type='CUBE', radius=0.1, location=location)
    objempty = bpy.context.object
    objempty.name = tracktoname
    objempty.hide_render = True

    return objempty


def animate_camera(objcamera, objpath, objtrackto, startframe=1, duration=200):
    """Animate the camera by following along the given path, 
    with the view locked to the given trackto-object.
    NOTE: this also clears any animation data of the path beforehand, 
    so use with care!
    objcamera   -- camera object which shall be animated
    objpath     -- curve object along which the camera should fly
    objtrackto  -- object (e.g. empty), to which the camera's view
                   will be locked
    startframe  -- frame at which animation will start, default: 1
    duration    -- duration of one complete fly-around along the path, 
                   in frames
    """

    # add FollowPath constraint
    c = objcamera.constraints.new(type='FOLLOW_PATH')
    c.target = objpath

    # add TrackTo constraint to camera
    c = objcamera.constraints.new(type='TRACK_TO')
    c.target = objtrackto
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'

    # animate camera path
    # by inserting key frames on evaluation time of path
    objpath.data.use_path = True

    # delete previously created keyframes
    # -> need to loop over all animation-fcurves for this object and 
    #    delete the f-curve with corresponding data_path
    actions = set()
    if objpath.animation_data is not None:
        actions.add(objpath.animation_data.action)
    if objpath.data.animation_data is not None:
        actions.add(objpath.data.animation_data.action)

    for act in actions:
        for fcu in act.fcurves:
            if fcu.data_path == 'eval_time':
                act.fcurves.remove(fcu)

    # insert keyframes
    objpath.data.path_duration = 100
    objpath.data.eval_time = 0
    objpath.data.keyframe_insert(data_path="eval_time", frame=startframe)

    endframe = startframe + duration
    objpath.data.eval_time = 100
    objpath.data.keyframe_insert(data_path="eval_time", frame=endframe)

    # set end-frame in Blender at least to the duration time
    # (comment this out, if you do not want this)
    if bpy.context.scene.frame_end < endframe:
        bpy.context.scene.frame_end = endframe

    return


def run():
    pathname = "Camera-Path"
    tracktoname = "Camera-TrackTo"

    # create camera path and trackto-object
    objpath = add_camera_path(pathname, 5, (0,0,1))
    objtrack = add_trackto_object(tracktoname, (0,0,0))

    # alternatively choose your own paths and trackto-objects
    #objpath = bpy.data.objects[pathname]
    #objtrack = bpy.data.objects[tracktoname]

    # reset camera location or define offset from camera path here
    objcamera.location = (0,0,0)

    # animate camera 
    # -- NOTE THAT THIS REMOVES ANY PREVIOUS CAMERA PATH ANIMATION!
    objcamera = bpy.data.objects["Camera"]
    animate_camera(objcamera, objpath, objtrack, startframe=0, duration=300)

    return


if __name__ == '__main__':
    run()