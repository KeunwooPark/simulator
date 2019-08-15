import saze
import sys
import lgsvl
from lgsvl import Vector
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--uname',
        help='user name',
        required = True,
        type=str
    )

    return parser.parse_args()


def spawn_npc(sim):
    npc_pos = Vector(-48,0,-103)
    npc = saze.spawn_npc(sim, npc_pos, "Sedan")
    return npc

def get_npc_event(sim, npc):
    waypoints_vec = []
    waypoints_vec.append(Vector(46.3, 0, -103))

    # Setup waypoints for the NPC to follow
    speed = 30
    waypoints = []
    for v in waypoints_vec:
        waypoints.append(lgsvl.DriveWaypoint(v, speed))

    # This function will be triggered
    def npc_event_func():
        npc.follow(waypoints)

    npc_event = saze.Event(func = npc_event_func, params = None, only_once = True)

    return npc_event

def get_main_callback(sim, npc, gps_sensor, recorders = None):
    ego_trigger_point = Vector(-27,0,-78)
    dist_thrs = 25

    npc_event = get_npc_event(sim, npc)
    def callback():
        gps_data = gps_sensor.data
        ego_tr = sim.map_from_gps(latitude = gps_data.latitude,\
                            longitude = gps_data.longitude)
        dist = (ego_tr.position - ego_trigger_point).norm()
        if dist < dist_thrs:
            npc_event.trigger()
        if recorders:
            for rec in recorders:
                rec.capture_img()

    return callback

def main(args):
    app_tag = "Scenario 0"
    sim = saze.open_simulator("SimpleMap")
    saze.print_msg(app_tag, "Simulator opened")
    ego = saze.spawn_ego(sim)
    saze.print_msg(app_tag, "Ego vehicle spawned")
    gps_sensor = saze.get_gps_sensor(ego)
    saze.print_msg(app_tag,"GPS sensor ready")

    npc = spawn_npc(sim)
    saze.print_msg(app_tag,"NPC vehicle spawned")

    main_cam = saze.get_main_camera_sensor(ego)
    main_dir_name = saze.get_img_dir_name(args.uname, "Scenario0", "main")
    main_rec = saze.CamRecoder(main_dir_name, main_cam)

    seg_cam = saze.get_seg_camera_sensor(ego)
    seg_dir_name = saze.get_img_dir_name(args.uname, "Scenario0", "seg")
    seg_rec = saze.CamRecoder(seg_dir_name, seg_cam)

    main_callback = get_main_callback(sim, npc, gps_sensor, recorders = [main_rec, seg_rec])
    sim.run_with_callback(main_callback)

if __name__=="__main__":
    args = parse_args()
    main(args)
