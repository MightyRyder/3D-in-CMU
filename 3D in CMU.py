# ------------------------------------------------------- #
#                                                         #
#                        3D in CMU                        #
#    --> WASD forward/left/down/right                     #
#    --> QE down/up                                       #
#    --> R to change rooms                                #
#    --> F to show stats                                  #
#                                                         # 
# ------------------------------------------------------- #

def setup_rooms():
    # ------------------------------------------------------- #
    #                 MAKE ROOMS HERE !!!!!                   #
    # ------------------------------------------------------- #
    # flags
    app.use_lighting = True # NO impact on performance, only boot time
    
    app.use_dynamic_lighting = True # small impact on performance,
    # updates lighting on moving objects. requires app.use_lighting
    
    app.use_fog = True # small impact on performance
    
    # note: objects with gradients are not impacted by fog or lighting
    
    app.ambient_light = 0.25 # how lit will the objects will be with no light nearby
    
    app.render_distance = 500**2 # makes the world of impact on performance
    
    app.hitboxSizeX, app.hitboxSizeY, app.hitboxSizeZ = 15, 15, 15 # hitbox size. by default
    # it's centered to the camera, it's around line 500
    
    # ----------------------------------- #
    # make objects
    
    # make(Object, Room #, Return Pointer)
    # make_settings(Setting/Settings, Room #)
    # Cube(x, y, z, size, color)
    # Rectoid(x, y, z, width, height, depth, color)
    # Hitbox(x, y, z, width, height, depth) <-- invisible rectoid
    # Floor(x, z, width, height, depth, color)
    # Pillar(x, z, width, height, color)
    # Wall(x, z, length, height, horizontal (True/False), color)
    # Portal(x, z, w, h, horizontal, to_room, spawn_x, spawn_y, spawn_z, color)
    # Light(x, y, z, color, intensity, range)) <-- requires app.use_lighting 
    
    make(Light(0, 50, 0, rgb(255, 255, 255), 2.0, 1000), 3)
    make(Cube(0, 50, 0, 40, gradient(rgb(255, 255, 255), rgb(255, 255, 255))), 3)
    make(Light(0, 50, 0, rgb(255, 255, 255), 1.5, 100000), 2)
    make(Cube(0, 50, 0, 40, gradient(rgb(255, 255, 255), rgb(255, 255, 255))), 2)
    
    make(Cube(0, 0, 400, 60, rgb(133, 237, 255)))
    make(Light(50, 50, 350, rgb(133, 237, 255), 2, 1000))
    make(Cube(400, 0, 0, 60, rgb(0, 255, 26)))
    make(Light(3, 50, 50, rgb(0, 255, 26), 2, 1000))
    
    make(Portal(-30, 200, 80, 70, False, 2, 0, 25, 0))
    
    app.rotation = make(Cube(0, 0, 0, 60, rgb(200, 200, 255)), 4, True)
    make(Light(0, 50, 0, rgb(255, 255, 255), 2, 500), 4)
    make(Cube(0, 50, 0, 15, gradient(rgb(255, 255, 255), rgb(255, 255, 255))), 4)
    app.cube = make(Cube(50, 0, 0, 60, gradient(rgb(136, 0, 255), rgb(198, 135, 255), start='top-left')), 1, True)
    
    # Tiled Floor
    for x in range(5):
        for z in range(5):
            make(Floor(x*100, z*100, 100, 100, 1, rgb(200, 200, 200)))
    
    # Baseplate Floor
    for x in range(30):
        for z in range(30):
            color = rgb(82, 82, 82) if (x+z)%2==1 else rgb(144, 144, 144)
            make(Floor(x*200-3000, z*200-3000, 200, 200, 1, color), 2)
            make(Floor(x*50-600, z*50-600, 50, 50, 1, color), 3)
    
    # City
    for x in range(15):
        for z in range(15):
            #make(Light(x*400-3000, 0, z*400-3000, rgb(255, 255, 255), 2, 1000), 2)
            make(Pillar(x*400-3000, z*400-3000, 200, 500+(x*z*5)%150), 2)
    
    # ----------------------------------- #
    # room-specific settings
    
    make_settings(['app.render_distance = 500**2', 'app.stepsPerSecond = 35'], 0)
    make_settings(['app.render_distance = 2000**2', 'app.stepsPerSecond = 10000'], 1)
    make_settings(['app.render_distance = 800**2', 'app.stepsPerSecond = 20'], 2)
    make_settings(['app.render_distance = 300**2', 'app.stepsPerSecond = 20'], 3)
    make_settings(['app.render_distance = 1000**2', 'app.stepsPerSecond = 60'], 4)
    
    # ----------------------------------- #
    # game tick for movement 
    
    # object.goTo(x, y, z)
    # object.hits(x, y, z)
    # object.hitsShape(object)
    # object.visible = True/False
    
    # RETURN POINTER VALUE & GLOBAL OR APP.* REQUIRED DURING OBJECT CREATION FOR
    # THIS TO WORK
def game_tick(room):
    check_portals(room)
    # GAME TICKS ARE GLOBAL! NOT RENDER-DISTANCE DEPENDENT!
    if room == 0:
        pass
    if room == 1:
        app.cube.goTo(0, 0, 50)
        if app.cube.hits(camera.x, camera.y, camera.z): # collision detection method #1
            app.stop()
    if room == 2:
        pass
    if room == 3:
        pass
    if room == 4:
        app.rotation.goTo(math.cos(time.time())*200, -50, math.sin(time.time())*200)

# ------------------------------------------------------- #
#                     engine code                         #
# ------------------------------------------------------- #

import math
import time

app.lastTime = time.time()
app.dtLastTime = time.time()
app.dt = 0
app.fpsCount = 0
fps = Label(20, 20, 20, size=20, bold=True, fill=rgb(255, 255, 255))
stats = Label('x: 0, y: 0, z: 0, angle: 0, room: 0, poly drawn: 0, poly pool: 0, obj pool: 0, skipped: 0', 200, 380, size=8, visible=False, fill=rgb(255, 255, 255))

app.background = rgb(0, 0, 0)
print('Loading...')
all_start = time.time()
checkpoint_start = time.time()
print('Setting up camera...')
app.stepsPerSecond = 35
app.setMaxShapeCount(999999)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.angle = 0
        self.rotSpeed = 0
        self.pitch = 0
        self.pitchSpeed = 0
        self.speed = 5
        self.cosA = 1
        self.sinA = 0

camera = Camera()
app.scene_objects = []
app.scene_lights = []
deadZoneSize = 50

app.poly_pool = []
rooms = []
rooms_lights = []
rooms_settings = []
rooms_portals = []

app.MAX_FACES = 1

checkpoint_end = time.time()
print('Set up camera. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
checkpoint_start = time.time()
print('Setting up helpers...')

# helper functions
def set_room(room):
    app.roomIndex = room
    app.scene_objects = rooms[room]
    app.scene_lights = rooms_lights[room]
    # empty the pool
    target_size = poly_count(room)
    current_size = len(app.poly_pool)
    if target_size < current_size: # trim
        for poly in app.poly_pool[target_size:]:
            poly.visible = False
        del app.poly_pool[target_size:]
        app.MAX_FACES = target_size
    app.obj_poly_pool = target_size
    if room < len(rooms_settings):
        for setting in rooms_settings[app.roomIndex]:
            exec(setting)
            # update fog
    app.fog_end = math.sqrt(app.render_distance)
    app.fog_start = app.fog_end*(4/5)
def check_portals(room):
    for portal in rooms_portals[room]:
        cam_hitbox.goTo(camera.x-7.5, camera.y-7.5, camera.z-7.5)
        if portal.hitsShape(cam_hitbox): # collision detection method #2
            camera.x = portal.spawn_x
            camera.y = portal.spawn_y
            camera.z = portal.spawn_z
            set_room(portal.to_room)

def poly_count(room):
    total = 0
    for obj in rooms[room]:
        total += len(obj.faces)
    return total

def lerp_rgb(c1, c2, t):
    # clamping
    if t < 0: t = 0
    if t > 1: t = 1
    
    r = c1.red + (c2.red - c1.red) * t
    g = c1.green + (c2.green - c1.green) * t
    b = c1.blue + (c2.blue - c1.blue) * t
    return rgb(r, g, b)

def project(rx, ry, rz): 
    sx = (rx * 200 / rz) + 200
    sy = 200 - (ry * 200 / rz)
    return [sx, sy]

def make(obj, room=0, return_pointer=False):
    if room < 0:
        print('Error: Room # must be greater than 0.')
        return
    if room >= len(rooms):
        for i in range(room-len(rooms)+1):
            rooms.append([])
            rooms_lights.append([])
            rooms_portals.append([])
    if isinstance(obj, Light):
        if return_pointer:
            light = obj
            rooms_lights[room].append(light)
            return light
        else:
            rooms_lights[room].append(obj)
    else:
        if isinstance(obj, Portal):
            thingy = obj
            rooms[room].append(thingy)
            rooms_portals[room].append(thingy)
            if return_pointer: return thingy
        elif return_pointer:
            thingy = obj
            rooms[room].append(thingy)
            return thingy
        else:
            rooms[room].append(obj)

def make_settings(settings, room=0):
    if room < 0:
        print('Error: Room # must be greater than 0.')
        return
    if room >= len(rooms):
        print('Error: You must create the room first.')
        return
    if room >= len(rooms_settings):
        for i in range(room-len(rooms_settings)+1):
            rooms_settings.append([])
    if isinstance(settings, str):
        rooms_settings[room].append(settings)
    else:
        for setting in settings:
            rooms_settings[room].append(setting)

for i in range(app.MAX_FACES):
    p = Polygon(0, 0, 0, 0, 0, 0, 0, 0, visible=False, border='black', borderWidth=1)
    app.poly_pool.append(p)

def update_object_lighting(obj, idx):
    if isinstance(obj.fill, gradient) or not app.use_lighting:
        return
    new_face_colors = []
    room_lights = rooms_lights[idx]
    for face_indices in obj.faces:
        cx = 0
        cy = 0
        cz = 0
        for idx in face_indices:
            v = obj.vertices[idx]
            cx += v[0]
            cy += v[1]
            cz += v[2]
        length = len(face_indices)
        cx /= length
        cy /= length
        cz /= length            
        
        # vertex retrieval of points in space
        v0, v1, v2 = [obj.vertices[i] for i in face_indices[:3]]
        # calculate the normal vector
        nx = (v1[1]-v0[1])*(v2[2]-v0[2]) - (v1[2]-v0[2])*(v2[1]-v0[1])
        ny = (v1[2]-v0[2])*(v2[0]-v0[0]) - (v1[0]-v0[0])*(v2[2]-v0[2])
        nz = (v1[0]-v0[0])*(v2[1]-v0[1]) - (v1[1]-v0[1])*(v2[0]-v0[0])
        
        mag = math.sqrt(nx**2 + ny**2 + nz**2)
        if mag == 0: mag = 1
        
        r = app.ambient_light
        g = app.ambient_light
        b = app.ambient_light
        
        nx, ny, nz = nx/mag, ny/mag, nz/mag
        for light in room_lights:
            lx = light.x - cx
            ly = light.y - cy
            lz = light.z - cz
            dist_sq = lx**2 + ly**2 + lz**2
            dist = math.sqrt(dist_sq)
            
            if dist < light.range:
                lx /= dist; ly /= dist; lz /= dist
                dot = max(0, nx*lx + ny*ly + nz*lz)
                falloff = 1 - (dist / light.range)
                diffuse = dot * falloff * light.intensity
                r += diffuse * (light.color.red / 255)
                g += diffuse * (light.color.green / 255)
                b += diffuse * (light.color.blue / 255)
        
        fill = obj.fill
        baked_color = rgb(min(255, fill.red * r), min(255, fill.green * g), min(255, fill.blue * b))
        new_face_colors.append(baked_color)
        
    obj.face_colors = new_face_colors

def update_lighting():
    for r in range(len(rooms)):
        room = rooms[r]
        room_lights = rooms_lights[r]
        
        for obj in room:
            if isinstance(obj.fill, gradient):
                continue
            new_face_colors = []
            for face_indices in obj.faces:
                cx = 0
                cy = 0
                cz = 0
                for idx in face_indices:
                    v = obj.vertices[idx]
                    cx += v[0]
                    cy += v[1]
                    cz += v[2]
                length = len(face_indices)
                cx /= length
                cy /= length
                cz /= length            
                
                # vertex retrieval of points in space
                v0, v1, v2 = [obj.vertices[i] for i in face_indices[:3]]
                # calculate the normal vector
                nx = (v1[1]-v0[1])*(v2[2]-v0[2]) - (v1[2]-v0[2])*(v2[1]-v0[1])
                ny = (v1[2]-v0[2])*(v2[0]-v0[0]) - (v1[0]-v0[0])*(v2[2]-v0[2])
                nz = (v1[0]-v0[0])*(v2[1]-v0[1]) - (v1[1]-v0[1])*(v2[0]-v0[0])
                
                mag = math.sqrt(nx**2 + ny**2 + nz**2)
                if mag == 0: mag = 1
                
                r = app.ambient_light
                g = app.ambient_light
                b = app.ambient_light
                
                nx, ny, nz = nx/mag, ny/mag, nz/mag
                for light in room_lights:
                    lx = light.x - cx
                    ly = light.y - cy
                    lz = light.z - cz
                    dist_sq = lx**2 + ly**2 + lz**2
                    dist = math.sqrt(dist_sq)
                    
                    if dist < light.range:
                        lx /= dist; ly /= dist; lz /= dist
                        dot = max(0, nx*lx + ny*ly + nz*lz)
                        falloff = 1 - (dist / light.range)
                        diffuse = dot * falloff * light.intensity
                        r += diffuse * (light.color.red / 255)
                        g += diffuse * (light.color.green / 255)
                        b += diffuse * (light.color.blue / 255)
                
                fill = obj.fill
                baked_color = rgb(min(255, fill.red * r), min(255, fill.green * g), min(255, fill.blue * b))
                new_face_colors.append(baked_color)
                
            obj.face_colors = new_face_colors

checkpoint_end = time.time()
print('Set up helpers. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
checkpoint_start = time.time()
print('Setting up objects..')

# objects
class Cube:
    def update_vertices(self):
        x, y, z = self.x, self.y, self.z
        s = self.size / 2
        self.vertices = [
            [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y+s, z-s], [x-s, y+s, z-s],
            [x-s, y-s, z+s], [x+s, y-s, z+s], [x+s, y+s, z+s], [x-s, y+s, z+s]
        ]
    def __init__(self, x, y, z, size, color):
        self.x, self.y, self.z = x, y, z
        self.size = size
        self.visible = True
        self.update_vertices()
        
        self.faces = [
            [3, 2, 1, 0],
            [6, 7, 4, 5],
            [7, 3, 0, 4],
            [2, 6, 5, 1],
            [7, 6, 2, 3],
            [0, 1, 5, 4]
        ]
        self.fill = color
        self.face_colors = [color] * 6
    def goTo(self, toX, toY, toZ):
        self.x = toX
        self.y = toY
        self.z = toZ
        self.update_vertices()
        if app.use_dynamic_lighting:
            update_object_lighting(self, app.roomIndex)
    def hits(self, x, y, z):
        self.rw = self.rh = self.rd = self.size/2
        if (self.x - self.rw) <= x <= (self.x + self.rw):
            if (self.y - self.rh) <= y <= (self.y + self.rh):
                if (self.z - self.rd) <= z <= (self.z + self.rd):
                    return True
        return False
    def hitsShape(self, other):
        for vertex in other.vertices:
            if self.hits(vertex[0], vertex[1], vertex[2]):
                return True
        for vertex in self.vertices:
            if other.hits(vertex[0], vertex[1], vertex[2]):
                return True
        return False
    
class Rectoid:
    def update_vertices(self):
        rw, rh, rd = self.rw, self.rh, self.rd
        x, y, z = self.x, self.y, self.z
        self.vertices = [
            [x-rw, y-rh, z-rd], [x+rw, y-rh, z-rd], [x+rw, y+rh, z-rd], [x-rw, y+rh, z-rd],
            [x-rw, y-rh, z+rd], [x+rw, y-rh, z+rd], [x+rw, y+rh, z+rd], [x-rw, y+rh, z+rd]
        ]
    def __init__(self, x, y, z, w, h, d, color):
        self.rw, self.rh, self.rd = w/2, h/2, d/2
        self.x, self.y, self.z = x, y, z
        self.width, self.height, self.depth = w, h, d
        self.visible = True
        self.update_vertices()
        self.faces = [
            [3, 2, 1, 0],
            [6, 7, 4, 5],
            [7, 3, 0, 4],
            [2, 6, 5, 1],
            [7, 6, 2, 3],
            [0, 1, 5, 4]
        ]
        self.fill = color
        self.face_colors = [color] * 6
    def goTo(self, toX, toY, toZ):
        self.x = toX
        self.y = toY
        self.z = toZ
        self.update_vertices()
        if app.use_dynamic_lighting:
            update_object_lighting(self, app.roomIndex)
    def hits(self, x, y, z):
        if (self.x - self.rw) <= x <= (self.x + self.rw):
            if (self.y - self.rh) <= y <= (self.y + self.rh):
                if (self.z - self.rd) <= z <= (self.z + self.rd):
                    return True
        return False
    def hitsShape(self, other):
        for vertex in other.vertices:
            if self.hits(vertex[0], vertex[1], vertex[2]):
                return True
        for vertex in self.vertices:
            if other.hits(vertex[0], vertex[1], vertex[2]):
                return True
        return False

class Floor(Rectoid):
    def __init__(self, x, z, w, h, d, color):
        super().__init__(x, -50, z, w, d, h, color)

class Pillar(Rectoid):
    def __init__(self, x, z, w, h, color=rgb(100, 0, 0)):
        super().__init__(x, h/2 - 50, z, w, h, w, color)

class Hitbox(Rectoid):
    def __init__(self, x, y, z, w, h, d):
        super().__init__(x, y, z, w, h, d, rgb(0, 0, 0))
        self.visible = False

class Wall(Rectoid):
    def __init__(self, x, z, w, h, horizontal=True, color=rgb(255, 255, 255)):
        if horizontal:
            super().__init__(x, h/2 - 50, z, w, h, 10, color)
        else:
            super().__init__(x, h/2 - 50, z, 10, h, w, color)

class Portal(Rectoid):
    def __init__(self, x, z, w, h, horizontal=True, to_room=0, spawn_x=0, spawn_y=0, spawn_z=0, color=gradient(rgb(50, 255, 50), rgb(255, 50, 50), rgb(50, 50, 255), start='top-right')):
        if horizontal:
            super().__init__(x, h/2 - 50, z, w, h, 10, color)
        else:
            super().__init__(x, h/2 - 50, z, 10, h, w, color)
        self.to_room = to_room
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.spawn_z = spawn_z
        
class Light:
    def __init__(self, x, y, z, color, intensity=1.0, range=500):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.intensity = intensity
        self.range = range

checkpoint_end = time.time()
print('Set up objects. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
checkpoint_start = time.time()
print('Setting up rooms...')
setup_rooms()
cam_hitbox = Hitbox(camera.x-app.hitboxSizeX, camera.y-app.hitboxSizeY/2, camera.z-app.hitboxSizeZ/2, app.hitboxSizeX, app.hitboxSizeY, app.hitboxSizeZ)
checkpoint_end = time.time()
print('Set up rooms. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')

app.fog_end = math.sqrt(app.render_distance)
app.fog_start = app.fog_end*0.6

if app.use_lighting:
    checkpoint_start = time.time()
    print('Baking lighting...')
    update_lighting()
    checkpoint_end = time.time()
    print('Baked lighting. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
else:
    print('Skipping lighting... (check app.use_lighting)')
    
app.roomIndex = 0
app.scene_objects = rooms[app.roomIndex]
app.scene_lights = rooms_lights[app.roomIndex]
app.obj_poly_pool = poly_count(app.roomIndex)

checkpoint_start = time.time()
print('Setting up inputs...')

# input hooks
def onMouseMove(mouseX, mouseY):
    dx = mouseX - 200
    dy = mouseY - 200
    
    if abs(dx) > deadZoneSize:
        offset = deadZoneSize if dx > 0 else -deadZoneSize
        camera.rotSpeed = (dx - offset) * 0.0005 * app.dt
    else:
        camera.rotSpeed = 0
    if abs(dy) > deadZoneSize:
        offset = deadZoneSize if dy > 0 else -deadZoneSize
        camera.pitchSpeed = (dy - offset) * 0.0003 * app.dt
    else:
        camera.pitchSpeed = 0

def onKeyHold(key):
    cosA = camera.cosA * app.dt # speed up by deltatime
    sinA = camera.sinA * app.dt 
    
    if 'w' in key:
        camera.z += camera.speed * cosA
        camera.x += camera.speed * sinA
    if 's' in key:
        camera.z -= camera.speed * cosA
        camera.x -= camera.speed * sinA
    if 'a' in key:
        camera.x -= camera.speed * cosA
        camera.z += camera.speed * sinA
    if 'd' in key:
        camera.x += camera.speed * cosA
        camera.z -= camera.speed * sinA
    if 'q' in key: camera.y -= camera.speed * app.dt
    if 'e' in key: camera.y += camera.speed * app.dt

def onKeyPress(key):
    if 'r' in key:
        # next room mechanism
        app.roomIndex = (app.roomIndex + 1) % len(rooms)
        set_room(app.roomIndex)
    if 'f' in key:
        stats.visible = not stats.visible

checkpoint_end = time.time()
print('Set up inputs. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
checkpoint_start = time.time()
print('Setting up tick...')

def onStep():
    app.fpsCount += 1
    if time.time() > app.lastTime + 1:
        fps.value = app.fpsCount
        app.lastTime = time.time()
        app.fpsCount = 0
    app.dt = (time.time() - app.dtLastTime) * 60
    app.dtLastTime = time.time()
    
    camera.angle += camera.rotSpeed
    camera.pitch -= camera.pitchSpeed
    if camera.pitch > 1.5: camera.pitch = 1.5
    if camera.pitch < -1.5: camera.pitch = -1.5
    camera.cosA = math.cos(camera.angle)
    camera.sinA = math.sin(camera.angle)
    cosP = math.cos(camera.pitch)
    sinP = math.sin(camera.pitch)
    skipped = 0
    for p in app.poly_pool:
        p.visible = False
    all_faces_to_draw = []
    game_tick(app.roomIndex)
    
    for obj in app.scene_objects:
        if not obj.visible: continue
        num_faces = len(obj.faces)
        dx = obj.vertices[0][0] - camera.x
        dy = obj.vertices[0][1] - camera.y
        dz = obj.vertices[0][2] - camera.z
        if (dx**2 + dz**2 + dy**2) > app.render_distance:
            skipped += num_faces
            continue
        obj_rz = dy * sinP + (dx * camera.sinA + dz * camera.cosA) * cosP
        if obj_rz < -200:
            skipped += num_faces
            continue
        
        for face_idx, face_indices in enumerate(obj.faces):
            transformed_vertices = []
            for idx in face_indices:
                # calculate where the point is relative to the camera
                v = obj.vertices[idx]
                tx = v[0] - camera.x
                ty = v[1] - camera.y
                tz = v[2] - camera.z
                
                # horizontal
                rx = tx * camera.cosA - tz * camera.sinA
                rz_temp = tx * camera.sinA + tz * camera.cosA
                
                ry = ty * cosP - rz_temp * sinP
                rz = ty * sinP + rz_temp * cosP
                
                transformed_vertices.append([rx, ry, rz])

            
            # vertex retrieval of points in space
            v0 = transformed_vertices[0]
            v1 = transformed_vertices[1]
            v2 = transformed_vertices[2]
            # calculate the normal vector
            nx = (v1[1]-v0[1])*(v2[2]-v0[2]) - (v1[2]-v0[2])*(v2[1]-v0[1])
            ny = (v1[2]-v0[2])*(v2[0]-v0[0]) - (v1[0]-v0[0])*(v2[2]-v0[2])
            nz = (v1[0]-v0[0])*(v2[1]-v0[1]) - (v1[1]-v0[1])*(v2[0]-v0[0])
            # calculate the points
            vx = v0[0]
            vy = v0[1]
            vz = v0[2]
            # backface culling, in other words hide the faces that arent shown to the camera
            # i googled the equation for these because i dont want to reinvent the wheel
            if (nx*vx + ny*vy + nz*vz) >= 0:
                skipped += 1
                continue
            
            clipped_vertices = []
            near_z = 1
            
            for i in range(len(transformed_vertices)):
                v1 = transformed_vertices[i]
                v2 = transformed_vertices[(i + 1) % len(transformed_vertices)]
                
                if v1[2] >= near_z:
                    clipped_vertices.append(v1)
                if (v1[2] >= near_z) != (v2[2] >= near_z):
                    t = (near_z - v1[2]) / (v2[2] - v1[2])
                    ix = v1[0] + t * (v2[0] - v1[0])
                    iy = v1[1] + t * (v2[1] - v1[1])
                    clipped_vertices.append([ix, iy, near_z])
            
            # if at least one of the points are showing on the camera, render it
            if len(clipped_vertices) > 2:
                projected_pts = []
                sum_z = 0
                for cv in clipped_vertices:
                    projected_pts.append(project(cv[0], cv[1], cv[2]))
                    sum_z += cv[2]
                
                avg_z = sum_z / len(clipped_vertices)
                all_faces_to_draw.append({
                    'points': projected_pts,
                    'z': avg_z,
                    'fill': obj.face_colors[face_idx]
                })
    # IMPORTANT! sort the faces to give the illusion of 3d
    all_faces_to_draw.sort(key=lambda f: f['z'], reverse=True)
    
    # the actual rendering part
    for i in range(len(all_faces_to_draw)):
        if i >= app.MAX_FACES:
            p = Polygon(0, 0, 0, 0, 0, 0, 0, 0, visible=False, border='black', borderWidth=1)
            app.poly_pool.append(p)
            app.MAX_FACES += 1
        
        # fog calc
        f = all_faces_to_draw[i]
        pts = f['points']
        poly = app.poly_pool[i]
        
        poly.pointList = pts
        
        if app.use_fog:
            dist = f['z']
            t = (dist - app.fog_start) / (app.fog_end - app.fog_start)
            
            if isinstance(f['fill'], gradient):
                poly.fill = f['fill']
            else:
                # apply lighting before lerping the fog effect
                if t >= 1:
                    poly.fill = app.background
                elif t <= 0:
                    poly.fill = f['fill']
                else:
                    poly.fill = lerp_rgb(f['fill'], app.background, t)
        else:
            poly.fill = f['fill']
        poly.visible = True
    
    fps.toFront()
    
    if stats.visible:
        stats.value = 'x: '+str(rounded(camera.x))+', y: '+str(rounded(camera.y))+', z: '+str(rounded(camera.z))+', angle: '+str(rounded(math.degrees(camera.angle)%360))+'-'+str(rounded(math.degrees(camera.pitch)%360))+', room: '+str(app.roomIndex)+', poly drawn: '+str(len(all_faces_to_draw))+', poly pool: '+str(len(app.poly_pool))+', room poly: '+str(app.obj_poly_pool)+', skip poly: '+str(skipped)
        stats.toFront()

checkpoint_end = time.time()
print('Set up tick. ('+str(rounded((checkpoint_end-checkpoint_start)*1000)/1000)+'s)')
all_end = time.time()
print('Finished. ('+str(rounded((all_end-all_start)*1000)/1000)+'s)')