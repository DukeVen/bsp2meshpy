import sys
import bsp_tool
from bsp_tool.branches.valve import source


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    bsp = bsp_tool.load_bsp(filename)


    # bsp.FACES
    # bsp.PLANES
    # bsp.TEXTURE_INFO
    # bsp.BRUSHES
    # bsp.BRUSH_SIDES
    # bsp.MODELS
    # bsp.ENTITIES

    #get first spawn position and exit loop
    for entity in bsp.ENTITIES:
        if entity.get('classname', '').startswith('info_player_'):

            origin_values = entity.get('origin', '').split()
            if len(origin_values) == 3:
                sX, sY, sZ = origin_values
                break

    
    with open("output.txt", "w") as output_file:
        output_file.write("var mesh = new BABYLON.Mesh('collisionGroups', scene);\n")

        #init spawn pos
        otpt = f"mesh.spawnPos = new BABYLON.Vector3({sX}, {sZ}, {sY});\n"
        output_file.write(otpt)

        output_file.write("mesh.collGroup = [];\n")

        excludeBrushes = ["TOOLS/TOOLSTRIGGER", "TOOLS/TOOLSSKYBOX"]
        
        for brush_index, brush in enumerate(bsp.BRUSHES):
            #use source.ContentsMask.PLAYER_SOLID instead?
            if (brush.contents & source.ContentsMask.SOLID) == 0:
                continue


            isPlayerClip = (brush.contents & source.Contents.PLAYER_CLIP) != 0

            brushSides = bsp.BRUSH_SIDES[brush.first_side:(brush.first_side + brush.num_sides)]
            

            # check if this brush is 100% textured by tools
            # if so, then just skip it
            # note: player clip brushes get compiled into nodraw textured faces
            if not isPlayerClip:
                allToolTextures = True
                brushTextures = bsp.textures_of_brush(brush_index)
                for side in brushSides:
                    isAnyToolsTexture = False

                    for texture in brushTextures:
                       if texture in excludeBrushes:
                           isAnyToolsTexture = True

                    if not isAnyToolsTexture or isPlayerClip:
                        allToolTextures = False
                        break
                if allToolTextures:
                    continue
                
            
            planes = [bsp.PLANES[side.plane] for side in brushSides]

            output_file.write("var bspPlanes = [];\n")
            for sidePlane in planes:
                dist = str(sidePlane.distance)
                x = str(round(sidePlane.normal[0], 6))
                y = str(round(sidePlane.normal[2], 6))
                z = str(round(sidePlane.normal[1], 6))
                s = f'bspPlanes.push({{dist: {dist}, normal: new BABYLON.Vector3({x}, {y}, {z})}});\n'
                output_file.write(s)
            output_file.write("mesh.collGroup.push(bspPlanes);\n")
    print("Output has been written to output.txt")







