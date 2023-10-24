# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "CSVToMesh",
    "author" : "Gxxxxx",
    "description" : "Convert csv file exported from RenderDoc to mesh",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Tool > CsvToMesh",
    "warning" : "",
    "category" : "Add Mesh"
}
import bpy
from bpy.types import Context
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

import csv
import os


def CreateMesh(data,uvindex,name):
    minId=65535
    maxId=0
    
    count=len(data)
    triangleCount=count/3

    for i in range(count):
        minId=min(minId,int(data[i][1]))
        maxId=max(maxId,int(data[i][1]))
    vertexCount=maxId-minId+1
    vertices=[(0,0,0) for _ in range(vertexCount)]
    uv_data=[(0,0) for _ in range(vertexCount)]
    triangles=[]
    
    k=0
    n=0
    while k<count:
        tri=[0,0,0]
        for i in range(3):
            IDX=int(data[k+i][1])
            realIDX=IDX-minId
            tri[i]=realIDX
            vertex=(float(data[k+i][2]),float(data[k+i][3]),float(data[k+i][4]))
            uv=(float(data[k+i][uvindex]),float(data[k+i][uvindex+1]))
            vertices[realIDX]=vertex
            uv_data[realIDX]=uv
        triangles.append((tri[0],tri[1],tri[2]))
        k=k+3
        n=n+1

    mesh_data=bpy.data.meshes.new(name)
    mesh_data.from_pydata(vertices,[],triangles)
    mesh_data.update()

    print("uv_layers",len(mesh_data.uv_layers))
    uv_layer=mesh_data.uv_layers.new()
    uv_layer.name="uv0"
    for loop in mesh_data.loops:
        uv_layer.data[loop.index].uv=uv_data[loop.vertex_index]
    
    
    return mesh_data


def readcsvfile(filepath):
    f=open(filepath,'r')
    reader=csv.reader(f)
    next(reader)
    l=[]
    for line in reader:
        l.append(line)
    return l

class CSVProperties(bpy.types.PropertyGroup):
    uvindex:bpy.props.IntProperty(name="UV Index",default=13,description="uv index of csv columns")


class ImportCSVFile(Operator,ImportHelper):
    bl_idname="file.import_csv"
    bl_label="Import Csv"
    bl_options={'PRESET', 'UNDO'}

    filename_ext=".csv"
    filter_glob:StringProperty(default="*.csv",options={"HIDDEN"})


    def execute(self, context):
        print("import file: ",self.filepath)
        scene=bpy.context.scene
        data=readcsvfile(self.filepath)
        filename=os.path.basename(self.filepath)
        meshname=os.path.splitext(filename)[0]
        
        mesh_data=CreateMesh(data,scene.csv_tool.uvindex,meshname)
        obj=bpy.data.objects.new(meshname,mesh_data)

        
        scene.collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj

        return {"FINISHED"}

    

class VIEW3D_PT_CSVTOMESH(bpy.types.Panel):
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="CsvToMesh"
    bl_label="CSV_To_Mesh"
    def draw(self, context: Context):
        col=self.layout.column(align=True)
        scene=bpy.context.scene
        col.prop(scene.csv_tool,"uvindex")
        col=self.layout.column(align=True)
        props=col.operator("file.import_csv",text="import csv",icon="WORDWRAP_ON")


classes=[ImportCSVFile,VIEW3D_PT_CSVTOMESH,CSVProperties]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.csv_tool=bpy.props.PointerProperty(type=CSVProperties)
    print("Hello")
    ...

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.csv_tool
    print("Bye")
    ...

if __name__=='__main__':
    register()
