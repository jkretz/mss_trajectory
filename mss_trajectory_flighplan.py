import xml.dom.minidom


def save_to_ftml(data):
    doc = xml.dom.minidom.Document()
    ft_el = doc.createElement("FlightTrack")
    ft_el.setAttribute("version", "1.9.1.")
    doc.appendChild(ft_el)
    # The list of waypoint elements.
    wp_el = doc.createElement("ListOfWaypoints")
    ft_el.appendChild(wp_el)

    for wp_num in data_trajectory['waypoint'].keys():
        wp = data_trajectory['waypoint'][wp_num]
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


data_trajectory = {'filename': 'test.ftml', 'waypoint': {}}
for wp_n in range(3):
    add_waypoint(data_trajectory['waypoint'], location='test_'+str(wp_n),
                 lat=78+(2*wp_n), lon=15-(5*wp_n), flightlevel=0, comments='')
save_to_ftml(data_trajectory)

exit()
