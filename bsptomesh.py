import sys
import bsp_tool


class Mesh:
    def __init__(self):
        self.vertices = []
        self.normals = []

    

def createMesh():
    for idx, face in enumerate(bsp.FACES):
        texinfo = bsp.TEXTURE_INFO[face.texture_info]
        texdata = bsp.TEXTURE_DATA[texinfo.texture_data]
        materialName = bsp.TEXTURE_DATA_STRING_DATA[texdata.name_index]

        #if materialName.startswith("TOOLS/"):
        #    continue

        #skip over triggers and skybox
        #need to skip over more materials to fix weird brushes/objects at origin??
        #also, removing this skip causes even more formations to be created at the origin.
        if "TRIGGER" in materialName or "TOOLSSKYBOX" in materialName:
            continue

        if face.displacement_info > -1:
            #dont want to handle displacements
            print("disp")
        else:
            generateBspFace(face, idx)



def generateBspFace(face, faceindex):
    planeNormal = bsp.PLANES[face.plane].normal

    #faceverts = bsp.vertices_of_face(faceindex) #gives me an error?
    faceSurfEdges = bsp.SURFEDGES[face.first_edge:(face.first_edge + face.num_edges)]

    rootIndex = 0
    for idx, surfEdge in enumerate(faceSurfEdges):
        edge = bsp.EDGES[abs(surfEdge)]
        e1 = 0
        e2 = 1
        if surfEdge < 0:
            e1 = 1
            e2 = 0

        if idx == 0:
            rootIndex = edge[e1]
        else:
            vertex1 = (bsp.VERTICES[rootIndex].x, bsp.VERTICES[rootIndex].y, bsp.VERTICES[rootIndex].z)
            AddVertex(vertex1)
            normal1 = (planeNormal.x, planeNormal.y, planeNormal.z)
            AddNormal(normal1)

            vertex2 = (bsp.VERTICES[edge[e1]].x, bsp.VERTICES[edge[e1]].y, bsp.VERTICES[edge[e1]].z)
            AddVertex(vertex2)
            normal2 = (planeNormal.x, planeNormal.y, planeNormal.z)
            AddNormal(normal2)

            vertex3 = (bsp.VERTICES[edge[e2]].x, bsp.VERTICES[edge[e2]].y, bsp.VERTICES[edge[e2]].z)
            AddVertex(vertex3)
            normal3 = (planeNormal.x, planeNormal.y, planeNormal.z)
            AddNormal(normal3)


def AddVertex(vertex):
    bspmesh.vertices.extend(vertex)
    
def AddNormal(normal):
    bspmesh.normals.extend(normal)



def ToBabylonCoords(mesh):
    converted = Mesh()
    #swap y and z, since y is up/down in babylonjs
    converted.vertices = [0.0] * len(mesh.vertices)
    converted.normals = [0.0] * len(mesh.normals)

    for i in range(0, len(mesh.vertices), 3):
        converted.vertices[i] = mesh.vertices[i]
        converted.vertices[i + 1] = mesh.vertices[i + 2]
        converted.vertices[i + 2] = mesh.vertices[i + 1]
        converted.normals[i] = mesh.normals[i]
        converted.normals[i + 1] = mesh.normals[i + 2]
        converted.normals[i + 2] = mesh.normals[i + 1]

    return converted


def WriteToBabylon(mesh):
    converted = ToBabylonCoords(mesh)

    numVertices = len(mesh.vertices) // 3
    numIndices = numVertices
    print(numVertices)
    indices = [0] * numIndices

    for i in range(numIndices):
        indices[i] = numIndices - 1 - i

    meshDecl = f'var mesh = new BABYLON.Mesh("bsp1", scene);\n'
    output_file.write(meshDecl)
    output_file.write('var vertexData = new BABYLON.VertexData();\n')

    output_file.write('vertexData.indices = [')
    indices_str = ",".join(map(str, indices))
    output_file.write(indices_str)
    output_file.write('];\n')

    output_file.write('vertexData.positions = [')
    for i, vertex in enumerate(converted.vertices):
        output_file.write(',' if i > 0 else '')
        formatted_vertex = int(vertex) if vertex.is_integer() else vertex
        output_file.write(str(formatted_vertex))
    output_file.write('];\n')

    output_file.write('vertexData.normals = [')
    for i, normal in enumerate(converted.normals):
        output_file.write(',' if i > 0 else '')
        formatted_normal = int(normal) if normal.is_integer() else normal
        output_file.write(str(formatted_normal))
    output_file.write('];\n')
    

    output_file.write('vertexData.applyToMesh(mesh);\n')



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    bsp = bsp_tool.load_bsp(filename)


    with open("output.txt", "w") as output_file:
        bspmesh = Mesh()
        createMesh()
        WriteToBabylon(bspmesh)
        
    print("Output has been written to output.txt")







