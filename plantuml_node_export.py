import inkex
import os
import sys
from inkex import paths
from inkex import transforms
from collections import OrderedDict


class PlantumlExport(inkex.EffectExtension):
    """Export a plantuml analog description based on the nodes in an inkscape file"""

    def add_arguments(self, pars):
        pars.add_argument("--output_filename", type=str, dest="output_filename", default="/tmp/points.csv")
        pars.add_argument("--origin", type=str, dest="origin", default="south_west_corner")
        pars.add_argument("--x_offset", type=float, dest="x_offset", default="0.0")
        pars.add_argument("--y_offset", type=float, dest="y_offset", default="0.0")

    def effect(self):
        f = open(self.options.output_filename, "w")
        x_off = self.options.x_offset
        y_off = self.options.y_offset
        # Get document height and trim the units string off the end
        # print(self.__dict__, file=sys.stderr)
        doc_h = float(self.svg.get('height'))

        node_dict = OrderedDict()

        if not self.svg.selected:
            raise inkex.AbortExtension("Please select an object.")


        for node in self.svg.selected.values():
            if node.tag == inkex.addNS("path", "svg"):
                # Make sure the path is in absolute coords
                node.apply_transform()
                path = paths.CubicSuperPath(node.get("d"))
                for sub_path in path:
                    # sub_path represents a list of all nodes in the path
                    for node in sub_path:
                        # node type is SubPath[(point_a, bezier, point_b)
                        # We dont want the control points, we only want the bezier
                        # point_a, bezier, and point_b is a list of length 2 and type float
                        x = int(round(node[1][0]))
                        y = int(round(node[1][1]))
                        x = x + x_off
                        if self.options.origin == "south_west_corner":
                            y = doc_h - y + y_off
                        else:
                            y = y + y_off
                        if x in node_dict:
                            raise inkex.AbortExtension("Duplicate entry at x = {x_coordinate}".format(x_coordinate=x))
                        else:
                            node_dict[x] = y
        previous_x = 0.0
        for x, y in node_dict.items():
            f.write("@+{x_offset}\n".format(x_offset=x-previous_x))
            previous_x = x
            f.write("out is {y_value}\n".format(y_value=y))


        f.close()


if __name__ == "__main__":
    PlantumlExport().run()