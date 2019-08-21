import os
import lgsvl
from lgsvl import Transform, Vector
import cv2
import shutil

def print_msg(tag, msg):
    print("{0}: {1}".format(tag, msg))

def open_simulator(map_name, sim_host = "127.0.0.1", port = 8181):
    sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", sim_host), port)
    if sim.current_scene == map_name:
        sim.reset()
    else:
        sim.load(map_name)

    return sim
def get_img_dir_name(uname, senario, cam_type):
    return "{}_{}_{}".format(uname, senario, cam_type)

def spawn_ego(sim, pos = None):
    state = lgsvl.AgentState()
    if pos:
        state.transform = sim.map_point_on_lane(pos)
    else:
        spawns = sim.get_spawn()
        state.transform = spawns[0]
    ego = sim.add_agent("XE_Rigged-lgsvl", lgsvl.AgentType.EGO, state)

    return ego

def spawn_npc(sim, pos, car_type, offset = Vector(0, 0, 0)):
    state = lgsvl.AgentState()
    state.transform = sim.map_point_on_lane(pos)
    state.transform.position += offset
    npc = sim.add_agent(car_type, lgsvl.AgentType.NPC, state)
    return npc

def spawn_pedestrian(sim, pos, name, offset = Vector(0, 0, 0), rotation = Vector(0, 0, 0)):
    state = lgsvl.AgentState()
    spawns = sim.get_spawn()
    state.transform = sim.map_point_on_lane(pos)
    state.transform.position += offset
    state.transform.rotation += rotation
    ped = sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
    return ped

def get_gps_sensor(ego):
    return get_sensor(ego, sensor_name = "GPS")

def get_sensor(ego, sensor_name):
    target_sensor = None
    for sensor in ego.get_sensors():
        if sensor.name == sensor_name:
            target_sensor = sensor
    return target_sensor

def get_main_camera_sensor(ego):
    return get_sensor(ego, sensor_name = "Main Camera")

def get_seg_camera_sensor(ego):
    return get_sensor(ego, sensor_name = "Segmentation Camera")

def get_npc_event(sim, npc, way_vecs, speeds):
    waypoints = []
    for i, vec in enumerate(way_vecs):
        on_lane_vec = sim.map_point_on_lane(vec).position
        wp = lgsvl.DriveWaypoint(on_lane_vec, speeds[i])
        waypoints.append(wp)

    def npc_event_func():
        npc.follow(waypoints)

    npc_event = Event(func = npc_event_func, params = None, only_once = True)
    return npc_event

def get_pedestrian_event(ped, waypoints):
    def event_func():
        ped.follow(waypoints, False)
    event = Event(func = event_func, params = None, only_once = True)
    return event

class Event:
    def __init__(self, func, params, only_once):
        self.func = func
        self.params = params
        self.only_once = only_once

        self.triggered = False

    def trigger(self):
        if self.only_once:
            if not self.triggered:
                self._run_func()
        else:
            self._run_func()

    def _run_func(self):
        if self.params and len(self.params) > 0:
            self.func(*self.params)
        else:
            self.func()
        self.triggered = True

class CamRecoder:
    def __init__(self, dir_name, cam_sensor, visualize = True):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.dir_path = "{}/data/{}".format(this_dir, dir_name)
        self.cam_sensor = cam_sensor
        self.img = None
        self.img_id = 0
        if os.path.isdir(self.dir_path):
            shutil.rmtree(self.dir_path, ignore_errors=True)
        os.mkdir(self.dir_path)

    def show_img(self):
        if self.img is not None:
            #print(img.shape)
            cv2.imshow('image', img)
            cv2.waitKey(1)

    def capture_img(self):
        rslt = self.cam_sensor.save_series(self.dir_path, self.img_id, quality = 100, compression=5)
        self.img_id += 1
