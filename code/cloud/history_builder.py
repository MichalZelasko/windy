def find_predecessor(cloud, previous_clouds):
    min_distance, min_idx = 10000000000, 0
    for i, cld in enumerate(previous_clouds):
        if (cld.x - cloud.x) ** 2 + (cld.y - cloud.y) ** 2 < min_distance:
            min_distance = (cld.x - cloud.x) ** 2 + (cld.y - cloud.y) ** 2
            min_idx = i
    cloud.add_previous(previous_clouds[min_idx])

def find_predecessors(clouds, previous_cloud):
    for cloud in clouds:
        find_predecessor(cloud, previous_cloud)

def complete_successor(cloud, successor_clouds):
    min_distance, min_idx = 10000000000, 0
    for i, cld in enumerate(successor_clouds):
        if (cld.x - cloud.x) ** 2 + (cld.y - cloud.y) ** 2 < min_distance:
            min_distance = (cld.x - cloud.x) ** 2 + (cld.y - cloud.y) ** 2
            min_idx = i
    cloud.add_next(successor_clouds[min_idx])

def complete_successors(clouds, successor_clouds):
    for cloud in clouds:
        if not cloud.has_next():
            complete_successor(cloud, successor_clouds)