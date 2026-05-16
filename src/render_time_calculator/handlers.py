def handleV1(data):
    device_name = data["data"]["device_info"]["compute_devices"][0]
    device_type = data["data"]["device_info"]["device_type"]

    fieldAttributes = []
    scenes = data["data"]["scenes"]

    for scene in scenes:
        if scene["stats"]["result"] != "OK":
            continue

        fieldAttributes.append({
            "renderTime": scene["stats"]["render_time_no_sync"],
            "renderedObject": scene["name"],
            "gpuName": device_name,
            "gpuBackend": device_type,
        })

    return fieldAttributes


def handleV2(data):
    device_name = data["data"]["device_info"]["compute_devices"][0]["name"]
    device_type = data["data"]["device_info"]["device_type"]

    fieldAttributes = []
    scenes = data["data"]["scenes"]

    for scene in scenes:
        if scene["stats"]["result"] != "OK":
            continue

        fieldAttributes.append({
            "renderTime": scene["stats"]["render_time_no_sync"],
            "renderedObject": scene["name"],
            "gpuName": device_name,
            "gpuBackend": device_type,
        })

    return fieldAttributes


def handleV3(data):
    fieldAttributes = {
        "renderTime": data["data"][0]["stats"]["render_time_no_sync"],
        "renderedObject": data["data"][0]["scene"]["label"],
        "gpuName": data["data"][0]["device_info"]["compute_devices"][0]["name"],
        "gpuBackend": data["data"][0]["device_info"]["device_type"],
    }

    return [fieldAttributes]


def handleV4(data):
    fieldAttributes = []
    for entry in data["data"]:
        fieldAttributes.append({
            "renderTime": entry["stats"]["render_time_no_sync"],
            "renderedObject": entry["scene"]["label"],
            "gpuName": entry["device_info"]["compute_devices"][0]["name"],
            "gpuBackend": entry["device_info"]["device_type"],
        })
    return fieldAttributes
