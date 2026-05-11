def handleV1(data):
    device_name = data['data']['device_info']['compute_devices'][0]
    device_type = data['data']['device_info']['device_type']

    fieldAttributes = []
    scenes = data['data']['scenes']

    for scene in scenes:

        if scene['stats']['result'] != 'OK':
            continue

        fieldAttributes.append({
                "renderedObject": scene['name'],
                "renderTime": scene['stats']['render_time_no_sync'],
                "gpuName": device_name,
                "gpuBackend": device_type
            }
        )

    return fieldAttributes


def handleV2(data):
    device_name = data['data']['device_info']['compute_devices'][0]["name"]
    device_type = data['data']['device_info']['device_type']

    fieldAttributes = []
    scenes = data['data']['scenes']

    for scene in scenes:

        if scene['stats']['result'] != 'OK':
            continue

        fieldAttributes.append({
                "renderedObject": scene['name'],
                "renderTime": scene['stats']['render_time_no_sync'],
                "gpuName": device_name,
                "gpuBackend": device_type
            }
        )

    return fieldAttributes


def handleV3(data):
    fieldAttributes = {
                "renderedObject": data["data"][0]["scene"]["label"],
                "renderTime": data['data'][0]["stats"]["render_time_no_sync"],
                "gpuName": data['data'][0]["device_info"]["compute_devices"][0]["name"],
                "gpuBackend": data['data'][0]["device_info"]["device_type"]
            }

    return [fieldAttributes]


def handleV4(data):
    fieldAttributes = []
    for entry in data["data"]:
        fieldAttributes.append({
                "renderedObject": entry["scene"]["label"],
                "renderTime": entry["stats"]["render_time_no_sync"],
                "gpuName": entry["device_info"]["compute_devices"][0]["name"],
                "gpuBackend": entry["device_info"]["device_type"]
            })
    return fieldAttributes
