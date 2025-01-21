from _det_db import _det_db
from cost import cost
import random
import math
import matplotlib.pyplot as plt
from itertools import combinations, product
import copy
import math

from shapely import Point, LineString, MultiLineString, Polygon
from shapely.ops import nearest_points, split
from shapely.affinity import translate


class gradient_descent:

    def __init__(self):

        frames, fragments = _det_db.get_data()

        
        #Format
        self.add_frames(frames)
        self.add_fragments(fragments)

        #Apply Movement To Move To Lower Cost
        for iteration in range(0):
            print(self.frames)
            self.movement(iteration)

        #Plot Final Stage
        self.plot_state()
        
    def add_frames(self, frames):
        self.frames = {}

        self.frames = {10000: [4.263319794274052, 2.8751302546047555], 10001: [3.469701945100383, 4.527431928519138], 10002: [4.142763782014817, 5.265308683032384], 10003: [2.8951874000839357, 5.55727340996113], 10004: [6.843871726435167, 3.8912057903758264], 10005: [5.995166386510797, 5.178156023785776], 10006: [4.685193513900103, 5.608802376170609], 10007: [4.386828021776087, 7.316787689542157]}
        
        
        #{10000: [13, 17], 10001: [16, 16], 10002: [18, 15], 10003: [15, 16], 10004: [16, 17], 10005: [13, 3], 10006: [13, 4], 10007: [5, 6]}
        # 
        # #{10000: [-0.03232958253066135, -0.2692513817748844], 10001: [-0.10660341413622201, -0.028528003654393005], 10002: [0.3066464702377241, 0.199615795502162], 10003: [-0.27496679086965603, -0.04937281235886525], 10004: [0.18886327620339508, 0.14330381780801782], 10005: [0.17618005129979253, 0.2289813751088452], 10006: [-0.0996937002946564, 0.07762030666182637], 10007: [0.1276007190397404, 0.3209799943108435]}
        
        
        #for frame in frames:
        #     self.frames[frame[0]] = [0,0]
            #self.frames[frame[0]] = [random.randint(0,10), random.randint(0,10)]

        # self.frames = {
        #     10000: [0,0],
        #     10001: [-2,3],
        #     10002: [-4,4],
        #     10003: [-6,6],
        #     10004: [-8,8],
        #     10005: [-10,10],
        #     10006: [-12,12],
        #     10007: [-14,14]

        # }

    def add_fragments(self, fragments):
        self.fragments = {}
        for fragment in fragments:
            #print(fragment)
            id = fragment[0]
            if id in self.fragments:
                self.fragments[id].add_fragment(fragment)
            else:
                f = gradient_descent.fragment(self, fragment)
                self.fragments[id] = f

    def plot_state(self):

        
        for fragment_id, fragment in self.fragments.items():
            n = len(fragment.line_set)

            count = 0

            item = cost(list(fragment.line_set.values()),visualize=False)

            cost_pos = item.get_cost()
            
            for index, line in fragment.line_set.items():
                count+=1
                x,y = line.xy
                plt.plot(x,y,color=fragment.color)

            if cost_pos is None:
                pass
            elif cost_pos.geom_type == "Point":
                pass
            else:
                x,y = cost_pos.xy
                plt.plot(x,y,color="black",lw=5)

        for frame, location in self.frames.items():
            plt.plot(location[0],location[1],marker="o")
            #plt.text(location[0],location[1], s=f"{frame}")


        plt.show()
      
    def movement(self, id):

        change_dict = {}
        for frame in self.frames.keys():
            change_dict[frame] = [0,0,0]

        
        total_length = 0
        total_error = 0
        total_lines = 0

        print("BEFORE CHANGE--------------------------------")
        print(self.frames)
        for fragment_id, fragment in self.fragments.items():

            if len(fragment.line_set.values()) < 2:
                continue

            lines = list(fragment.line_set.values())
            
            item = cost(lines,visualize=False)

            min_cost = item.get_cost()


            if not min_cost is None and min_cost.geom_type == "LineString":

                total_lines += len(lines)
                total_length += min_cost.length

                middle = min_cost.interpolate(min_cost.length/2)

                for index, line in fragment.line_set.items():

                    p1,p2 = nearest_points(middle, line)

                    dx = p1.x - p2.x
                    dy = p1.y - p2.y

                    total_error += math.sqrt(dx*dx + dy*dy)

                    if dx != 0:
                        change_dict[index][0] += dx  #*dx*(dx/abs(dx))
                    if dy != 0:
                        change_dict[index][1] += dy  # *dy*(dy/abs(dy))

                    change_dict[index][2] += 1

        alpha = 0.7

        print(f" {id} {total_lines} {total_length} {total_error}")

        for frame in self.frames.keys():
            if change_dict[frame][2] != 0:
                
                change_dict[frame][0] = (change_dict[frame][0]/change_dict[frame][2])*alpha
                change_dict[frame][1] = (change_dict[frame][1]/change_dict[frame][2])*alpha

                


        for fragment_id, fragment in self.fragments.items():

            for index, line in fragment.line_set.items():

                fragment.line_set[index] = translate(line, change_dict[index][0], change_dict[index][1])

        for frame_id, frame in self.frames.items():

            frame[0] += change_dict[frame_id][0]
            frame[1] += change_dict[frame_id][1]

        

        
            
            

    class fragment:

        def __init__(self, ts, fragment):
            self.ts = ts 
            self.color = f'#{random.randint(0, 0xFFFFFF):06x}'
            self.line_set = {}
            self.add_fragment(fragment)
        
        def add_fragment(self, fragment):
            start = self.ts.frames[fragment[1]]
            direction = math.radians(fragment[6])

            by = fragment[7]


            lx = fragment[8]
            ly = fragment[9]
            rx = fragment[10]
            ry = fragment[11]

            wid = min(abs(lx-rx), 360-abs(lx-rx))
            height = abs(ry - ly)

            overall_width = math.sqrt(wid*wid + height*height)


            width_degree = math.radians(overall_width/2)
            min_width = 0.1

            dist = min_width/math.sin(width_degree)

            max_dist = 50

            middle = (round(start[0]+dist*math.sin(direction),3), 
                   round(start[1]+dist*math.cos(direction),3))

            end = (round(start[0]+max_dist*math.sin(direction),3), 
                   round(start[1]+max_dist*math.cos(direction),3))

            line = LineString([middle, end])

            self.line_set[fragment[1]] = line

        
             


if __name__ == "__main__":
    gradient_descent()