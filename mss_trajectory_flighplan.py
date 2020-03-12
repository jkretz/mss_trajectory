import xml.dom.minidom
import os
import numpy as np


def pressure2flightlevel(p):

    # g and R are used by all equations below.
    g = 9.80665
    R = 287.058

    if p < 3.956:
        raise ValueError("pressure to flight level conversion not "
                         "implemented for z > 71km (p ~ 4 Pa)")

    elif p <= 66.952:
        # ICAO standard atmosphere between 51 and 71 km: T(z=51km) = -2.5 degC,
        # p(z=71km) = 0.66939 hPa. Temperature gradient is 2.8 K/km.
        z0 = 51000.
        T0 = 270.65
        gamma = 2.8e-3
        p0 = 66.952

        # Hydrostatic equation with linear temperature gradient.
        z = z0 + 1. / gamma * (T0 - T0 * np.exp(gamma * R / g * np.log(p / p0)))

    elif p < 110.928:
        # ICAO standard atmosphere between 47 and 51 km: T(z=47km) = -2.5 degC,
        # p(z=47km) = 1.10906 hPa. Temperature is constant at -2.5 degC.
        z0 = 47000.
        p0 = 110.928
        T = 270.65

        # Hydrostatic equation with constant temperature profile.
        z = z0 - (R * T) / g * np.log(p / p0)

    elif p < 868.089:
        # ICAO standard atmosphere between 32 and 47 km: T(z=32km) = -44.5 degC,
        # p(z=32km) = 54.75 hPa. Temperature gradient is -2.8 K/km.
        z0 = 32000.
        T0 = 228.66
        gamma = -2.8e-3
        p0 = 868.089

        # Hydrostatic equation with linear temperature gradient.
        z = z0 + 1. / gamma * (T0 - T0 * np.exp(gamma * R / g * np.log(p / p0)))

    elif p < 5474.16:
        # ICAO standard atmosphere between 20 and 32 km: T(z=20km) = -56.5 degC,
        # p(z=20km) = 54.75 hPa. Temperature gradient is -1.0 K/km.
        z0 = 20000.
        T0 = 216.65
        gamma = -1.0e-3
        p0 = 5475.16

        # Hydrostatic equation with linear temperature gradient.
        z = z0 + 1. / gamma * (T0 - T0 * np.exp(gamma * R / g * np.log(p / p0)))

    elif p < 22632.:
        # ICAO standard atmosphere between 11 and 20 km: T(z=11km) = -56.5 degC,
        # p(z=11km) = 226.32 hPa. Temperature is constant at -56.5 degC.
        z0 = 11000.
        p0 = 22632.64
        T = 216.65

        # Hydrostatic equation with constant temperature profile.
        z = z0 - (R * T) / g * np.log(p / p0)

    else:
        # ICAO standard atmosphere between 0 and 11 km: T(z=0km) = 15 degC,
        # p(z=0km) = 1013.25 hPa. Temperature gradient is 6.5 K/km.
        z0 = 0
        T0 = 288.15
        gamma = 6.5e-3
        p0 = 101325.

        # Hydrostatic equation with linear temperature gradient.
        z = 1. / gamma * (T0 - T0 * np.exp(gamma * R / g * np.log(p / p0)))

    # Convert from m to flight level (ft).
    flightlevel = z * 0.0328083989502

    return flightlevel


def save_to_ftml(data):
    doc = xml.dom.minidom.Document()
    ft_el = doc.createElement("FlightTrack")
    ft_el.setAttribute("version", "1.9.1.")
    doc.appendChild(ft_el)
    # The list of waypoint elements.
    wp_el = doc.createElement("ListOfWaypoints")
    ft_el.appendChild(wp_el)

    for wp_num in data['waypoint'].keys():
        wp = data['waypoint'][wp_num]
        element = doc.createElement('Waypoint')
        wp_el.appendChild(element)
        for var in wp.keys():
            element.setAttribute(var, str(wp[var]))
        comments = doc.createElement('Comments')
        comments.appendChild(doc.createTextNode(str(wp['comments'])))
        element.appendChild(comments)
    with open(data['filename'], 'w') as file_object:
        doc.writexml(file_object, indent="  ", addindent="  ", newl="\n", encoding="utf-8")


def add_waypoint(dict_in, **kwargs):
    entry_key = len(dict_in.keys())
    dict_in[entry_key] = {}
    for var in kwargs.keys():
        dict_in[entry_key][var] = kwargs[var]
    return


def create_dict_entry(dict_in, num_traj_in):
    trajecotries[num_traj_in] = {}
    trajecotries[num_traj_in]['time'] = list()
    trajecotries[num_traj_in]['lat'] = list()
    trajecotries[num_traj_in]['lon'] = list()
    trajecotries[num_traj_in]['p'] = list()
    trajecotries[num_traj_in]['alt'] = list()


ifile = 'trajectory_input/example_foreward_trajectory_2march.txt'
f = open(ifile, 'r').read().split('\n')[1::]

num_traj = 1
trajecotries = {}
create_dict_entry(trajecotries, num_traj)
for nl, line in enumerate(f):
    if line == '':
        if f[nl-1] == '':
            num_traj += 1
            create_dict_entry(trajecotries, num_traj)
            continue
        continue
    line_split = line.split(' ')
    trajecotries[num_traj]['time'].append(line_split[1])
    trajecotries[num_traj]['lat'].append(line_split[4])
    trajecotries[num_traj]['lon'].append(line_split[5])
    trajecotries[num_traj]['p'].append(line_split[6])
    trajecotries[num_traj]['alt'].append(line_split[7])

# 2=hourly, 6=3-hourly
density = 6
for traj in trajecotries.keys():
    if not trajecotries[traj]['time']:
        continue
    else:
        os.system('mkdir -p mss_ftml_trajectory/'+str(trajecotries[traj]['time'][0]))

    data_trajectory = {'filename': 'mss_ftml_trajectory/'+str(trajecotries[traj]['time'][0])
                                   +'/traj_'+str(traj)+'.ftml', 'waypoint': {}}
    for nv, val in enumerate(zip(trajecotries[traj]['time'], trajecotries[traj]['lat'], trajecotries[traj]['lon'],
                   trajecotries[traj]['alt'], trajecotries[traj]['p'])):
        if nv % density == 0:
            add_waypoint(data_trajectory['waypoint'], location=val[0][6::]+'_'+str(traj),
                         lat=val[1], lon=val[2], flightlevel=pressure2flightlevel(float(val[4])*100.), comments='')
    save_to_ftml(data_trajectory)

exit()
