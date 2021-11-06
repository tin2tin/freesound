# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.types import Panel
from . import freesound_api
from . import freesound
import datetime
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

class FREESOUND_PT_Panel(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Freesound"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type\
        in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sce = context.scene

        frame_current = sce.frame_current
        addon_data = context.scene.freesound_data
        split = layout.split(factor=0.8, align=True)
        addon_prefs =  bpy.context.preferences.addons[__package__].preferences


        if (addon_prefs.freesound_access == True):

            col = layout.column(align=True)

            split2 = col.row(align=True)
            split2.prop(
                addon_data,
                "search_item",
                text="Search"
            )
            split2.operator("freesound.search", text="", icon='VIEWZOOM')

            col.prop(addon_data, "license", text="License")
            col.prop(addon_data, "search_filter", text="Filter")
            col = col.column(align=True)
            col.prop(addon_data, "duration_from", text="Duration Minimum")
            col.prop(addon_data, "duration_to", text="Maximum")

            col = layout.box()
            col_list = col.column(align=True)
            row = col_list.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="List Page")
            row.operator("freesound.firstpage", icon='REW', text="")
            row.operator("freesound.prev10page", icon='TRIA_LEFT', text="")
            row.prop(addon_data, "current_page", text="")
            row.operator("freesound.next10page", icon='TRIA_RIGHT', text="")
            row.operator("freesound.lastpage", icon='FF', text="")

            try:
                pages = int(addon_data.sounds/len(addon_data.freesound_list))
                row.label(text="of %s" % str(pages))
            except:
                row.label(text="1 of ...")

            freesound_ptr = bpy.types.AnyType(bpy.context.scene.freesound_data)

            row = col_list.row(align=True)
            col = row.column(align=True)
            col.template_list("FREESOUND_UL_List", "", freesound_ptr, "freesound_list", freesound_ptr, "active_list_item")

            col = row.column(align=True)

            if (addon_data.sound_is_playing):
                col.operator("freesound.pause", text="", icon='PAUSE')
            else:
                col.operator("freesound.play", text="", icon='PLAY')
            col.separator()
            col.operator("freesound.add", text="", icon='NLA_PUSHDOWN')
            col.separator()
            col.prop(addon_data, "high_quality", text="", icon="EVENT_H", toggle=True)
            col.separator()
            col.operator("freesound.info", text="", icon='URL')

            row = col_list.row(align=True)
            # row.alignment = 'RIGHT'
            val = [0,1,2,3,4]
            point_star = 0
            try:
                point_star = addon_data.freesound_list[addon_data.active_list_item].avg_rating
            except:
                point_star = 0
            for l in val:
                if (l <= point_star-1):
                    val[l] = 'SOLO_ON'
                elif ((point_star % 1) > 0.5):
                        val[l] = 'SOLO_OFF'
                elif ((point_star % 1) <= 0.5 and (point_star % 1) != 0):
                        val[l] = 'SORTBYEXT'
                elif ((point_star % 1) == 0):
                        val[l] = 'SOLO_OFF'

            if (addon_data.freesound_list_loaded):
                try:
                    num_ratings = addon_data.freesound_list[addon_data.active_list_item].num_ratings
                except:
                    num_ratings = 0

                split = row.split(factor=0.4, align=True)
                split.alignment = 'RIGHT'
                split.label(text="Rating ")
                split = split.split(factor=0.2, align=True)
                split.alignment = 'RIGHT'
                split.label(text="", icon=val[0])
                split.label(text="", icon=val[1])
                split.label(text="", icon=val[2])
                split.label(text="", icon=val[3])
                split.label(text="", icon=val[4])


            try:
                duration = addon_data.freesound_list[addon_data.active_list_item].duration
            except:
                duration = 0
            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Duration")
            split = split.split(factor=0.6, align=True)
            split.alignment = 'LEFT'
            split.label(text=str(bpy.utils.smpte_from_seconds(time=float(duration))))

            try:
                author = addon_data.freesound_list[addon_data.active_list_item].author
            except:
                author = "Unknown"
            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Author")
            split = split.split(factor=0.6, align=True)
            split.alignment = 'LEFT'                
            split.label(text=author)

            try:
                license = addon_data.freesound_list[addon_data.active_list_item].license
            except:
                license = "Unknown"
            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="License")
            split = split.split(factor=0.6, align=True)
            split.alignment = 'LEFT'                
            split.label(text=license)

def draw():
    addon_data = bpy.context.scene.freesound_data
    try:
        images = addon_data.freesound_list[addon_data.active_list_item].images
        x1 = 0
        x2 = 150
        y1 = 0
        y2 = 71

        for a in bpy.context.screen.areas:
            if a.type == "SEQUENCE_EDITOR":
                for r in a.regions:
                    if r.type == "UI":
                        # print(r.type)
                        x2 = r.width - 21

        shader = gpu.shader.from_builtin('2D_IMAGE')
        batch = batch_for_shader(
            shader, 'TRI_FAN',
            {
                "pos": ((x1, y1), (x2, y1), (x2, y2), (x1, y2)),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )

        image = bpy.data.images[images]

        if image.gl_load():
            return # an exception happened

        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
        shader.bind()
        shader.uniform_int("image", 0)
        batch.draw(shader)

        image.gl_free()
    except:
        print("Failed to draw waveform.")
           
handler = bpy.types.SpaceSequenceEditor.draw_handler_add(draw,(),'UI','POST_PIXEL')

# then remove the handler with ...
#bpy.types.SpaceSequenceEditor.draw_handler_remove(handler, 'UI')


                # tex = bpy.data.images[images]
                # col = layout.box().column()
                # col.template_ID_preview(data=tex, show_buttons=False)
