def getPreferredOrientation(yaw, widthChunks, lengthChunks):
    norm_yaw = (yaw % 360 + 360) % 360
    # 45 to 135 is West, 225 to 315 is East (along X)
    facing_x = (45 <= norm_yaw < 135) or (225 <= norm_yaw < 315)
    
    if widthChunks == lengthChunks:
        return [[widthChunks, lengthChunks]]
        
    if facing_x:
        # Prefer horizontal (span along X)
        return [[max(widthChunks, lengthChunks), min(widthChunks, lengthChunks)],
                [min(widthChunks, lengthChunks), max(widthChunks, lengthChunks)]]
    else:
        # Prefer vertical (span along Z)
        return [[min(widthChunks, lengthChunks), max(widthChunks, lengthChunks)],
                [max(widthChunks, lengthChunks), min(widthChunks, lengthChunks)]]

print("Yaw 90 (East):", getPreferredOrientation(90, 1, 2))
print("Yaw 0 (South):", getPreferredOrientation(0, 1, 2))
