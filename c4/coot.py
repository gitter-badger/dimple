
import os
from subprocess import Popen, PIPE
import textwrap


def basic_script(pdb, mtz, center):
    text = """\
           # coot script generated by dimple
           pdb = "%s"
           mtz = "%s"

           #set_nomenclature_errors_on_read("ignore")""" % (pdb, mtz)
    if pdb: text += """
           molecule = read_pdb(pdb)"""
    if center: text += """
           set_rotation_centre(%g, %g, %g)
           set_zoom(30.)""" % center
    if mtz: text += """
           map21 = make_and_draw_map(mtz, "2FOFCWT", "PH2FOFCWT", "", 0, 0)
           map11 = make_and_draw_map(mtz, "FOFCWT", "PHFOFCWT", "", 0, 1)"""
    return textwrap.dedent(text)


def generate_r3d(scene_script, basename, cwd, render_png=False):
    M_SQRT2 = 0.5**0.5
    predefined_quaternions = [ (0., 0., 0., 1.),
                               (0., -M_SQRT2, 0., M_SQRT2),
                               (0.5, -0.5, 0.5, 0.5),
                               #(M_SQRT2, 0., 0., M_SQRT2),
                               #(0.5, 0.5, 0.5, 0.5),
                               #(0.5, -0.5, 0.5, 0.5)
                             ]
    coot_process = Popen(["coot", "--python", "--no-graphics", "--no-guano"],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
    # In coot, raster3d() creates file.r3d, make_image_raster3d() additionally
    # calls render program and opens image (convenient for testing)
    script = scene_script
    for n, quat in enumerate(predefined_quaternions):
        script += """
set_view_quaternion(%g, %g, %g, %g)""" % quat
        script += """
graphics_draw() # this is needed only for coot in --no-graphics mode
raster3d("%sv%d.r3d")""" % (basename, n+1)
    coot_process.communicate(input=script+"""
coot_real_exit(0)
""")
    if render_png:
        for n, _ in enumerate(predefined_quaternions):
            vname = "%sv%d" % (basename, n+1)
            print "rendering %s/%s.png" % (cwd, vname)
            r3d_script = open(os.path.join(cwd, vname+".r3d")).read()
            render_process = Popen(["render", "-png", vname+".png"],
                                stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
            render_process.communicate(input=r3d_script)
    #Popen(["xdg-open",  os.path.join(cwd, basename+"v1.png")]).wait()

