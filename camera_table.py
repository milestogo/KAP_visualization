#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CPHLewis and M Conley. Copyleft 2015. 
# Distributed under creative commons Attribution & Share alike License
#  (CC BA-SA) http://creativecommons.org/licenses/by-sa/4.0/

# Thanks mcclinto & BlakeBill91
# Also http://en.wikipedia.org/wiki/Angle_of_view

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from math import radians, degrees, tan, atan, atan2, pi, cos, sin, sqrt, hypot

s = 3.3 # meters. Diameter of example object.
hs = [3.3, 6.6, 60., 100., 150.] # Height of camera above ground. Meters.
degPhis = [0, 15., 22.5, 45.] # angle elevation above plumb of camera on rig. 0  = nadir. Degrees.


# Cameras

# Name, Width, Height, Default Lens, Diagonal Aspect
NDF = "No default"
sensors = {1:('35mm      ', 35.8, 23.8, NDF, 1.50),
           2:('APS-C/EF-s',22.3,14.9, NDF, 1.50),
           3:('Four-thirds',17.3,13., NDF, 1.33),
           4:('Ricoh GR',23.7,15.7,18.3, 1.5),
           5:('Canon S100',7.5,5.7,6., 1.3),
           6:('Gopro 3',05.76,4.49,2.77, 1.28),
           7:('Sony RX1',35.8, 5.0, NDF, 1.5),
           8:('Sony A6000', 23.5,5., NDF, 1.49),
           9:('Sony Nex5',23.4,5.0, NDF, 1.5),
           10:('Custom', 10.0,5.0,NDF, 2.00),
           }

def ask_sensor():
    print('''\t\tWidth\tHeight\tDiag. Aspect''')
    for key in sensors:
        val = sensors[key]
        print('''%s) %s\t%s\t%s\t%s'''%(key, val[0],
                                            val[1],
                                            val[2],
                                            val[4]))
    print('''Enter Sensor/Camera number:>''')
    sensor = int(raw_input())

    if sensor not in sensors.keys():
        print('Using default sensor (35mm)')
        sensor = 1
    width = sensors[sensor][1]
    height = sensors[sensor][2]

    if  sensors[sensor][3] == NDF:
       lensfl = float(raw_input("Lens focal length (mm):"))
    else:
       lensfl = float(sensors[sensor][3])
    return sensor, lensfl, width, height

def camera_subtends(height, lensfl):
    ''' angle in radians subtended by camera's field of view. (Total, not half.)'''
    return 2 * atan(height/(2*lensfl)) 

def ground_distance(h, angle, degs):
    '''Distance on ground from height h at angle (is angle in degrees?).'''
    if degs:
        return h * tan(radians(angle))
    else:
        return h * tan(angle)

def object_subtends_vert(height, near, far):
    ''' given distances to near and far edges of object, and height of camera,
    how much of the possible FoV is subtended?'''
    return atan(far/height) - atan(near/height)
    
def vert_proportion(degPhi, s, h ):
    '''Calculates proportion of field of view of camera subtended by the object
    if the object is in the middle of the camera's focus.

    Camera might Crop the object, or object may be Out of field-of-view.'''

    G =  ground_distance(h, degPhi, True)

    # Calculate proportion of image (or name edge case):
    viewrange = [h*tan(radians(degPhi) - radTheta/2), h*tan(radians(degPhi) + radTheta/2)]
    if (G + s/2) < viewrange[0] or (G - s/2 > viewrange[1]):
        label = "Out"
    elif (G - s/2) < viewrange[0] or (G + s/2 > viewrange[1]):
        label = "Crop"
    else:
        # angle subtended by target of size s 
        subt = atan((G + s/2)/h) - atan((G - s/2)/h)
        proportion = subt/radTheta
        # proportion of radTheta
        label = '%0.3f'%proportion
    return label

def horiz_proportion(degPhi, s, h):
    ''' Calculate proportion of horizontal field of view subtended by the object
    if the object is in the middle of the camera's focus.'''
    
    G = ground_distance(h, degPhi, True)
    D = hypot(G, h) #Actual distance camera-to-object
    Aw = atan2(s/2., D)
    return(Aw/(radThetaWidth/2))
    
def sketch(ax, h, degPhi, thB, thT, xB, xS, xT):
    '''Draw the nominal side-view of s centered in FoV.'''
    ax.set_aspect('equal')
    ax.locator_params(axis='both', nbins=3)
    ax.plot([xS - s/2., xS + s/2.], [0,0],'y', linewidth=10)
    ax.plot([0, xS], [h, 0], 'g')
    if thB < -pi/2:
        ax.hlines(h, ax.get_xlim()[0], 0, linestyle='dotted', color='g')
    else:
        ax.plot([0, xB], [h, 0], ':g')
    if thT > pi/2.:
        ax.hlines(h, 0, ax.get_xlim()[1], linestyle='dotted', color='g')
    else:
        ax.plot([0, xT], [h, 0], ':g')
    
def reports():
    '''Describe current shots with graphical and tabular output.'''
    lens="-%00.fmm" % lensfl

    tablename = "".join(x for x in sensors[sensor][0] if x.isalnum()) + lens

    f = open(tablename  + '.html', 'w')
    fig, axs = plt.subplots(ncols=len(degPhis), nrows=len(hs)) 
    #fig, axs = plt.subplots(ncols=len(degPhis), nrows=len(hs), sharey='row') #sharey looks tidy, crops info
    fig.set_size_inches(8.5, 11) 
    f.write('<html><body>')
    f.write('''<h3>Proportions of Field of View</h3><p>
%s sensor at %0.1fmm focal length</p>
<p>Amount of the image taken up by a centered %0.1fm object,
for varying camera altitude and elevations from plumb.</p>
<ul><li>vert: proportion of vertical image object occupies;
<li>horiz: proportion of horizontal image object occupies;
<li>bottom: ground distance from camera nadir to bottom of image;
<li>top: ground distance from nadir to top of image.</ul>'''%(sensors[sensor][0], lensfl, s ))
    f.write('<p><table border=1 frame=void rules=rows>')
    f.write(html_row(['Altitude'] + map(lambda p: str(p)+'&deg;', degPhis)))
    for row, h in enumerate(hs):
        f.write('<tr><td>%1.1fm</td>'%h)
        for col, p in enumerate(degPhis):
            
            # calculate parts
            xS = ground_distance(h, p, True)
            thB = radians(p) - radTheta/2.
            if thB <= -pi/2:
                xB = 'horizon'
            else:
                xB = ground_distance(h, thB, False)
            thT = radians(p) + radTheta/2.
            if thT >= pi/2:
                xT = 'horizon'
            else:
                xT = ground_distance(h, thT, False)
            thS = object_subtends_vert(h, xS - s/2., xS + s/2.)
            
            # plot in current ax
            sketch(axs[row, col], h, p, thB, thT, xB, xS, xT)
            if row==0:
                axs[row,col].set_title(r'${0:1.1f}^\circ$ elev.'.format(p))
            
            # write one table cell
            f.write('<td>')
            f.write('vert: {0:1.2f}</br>horiz: {1:1.2f}</br>'.format((thS/radTheta), horiz_proportion(p, s, h)))
            if type(xB) == float:
                xB = '{0:1.2f}'.format(xB)
            if type(xT) == float:
                xT = '{0:1.2f}'.format(xT)
            f.write('bottom: {0}m</br>top: {1}m'.format(xB, xT))
            f.write('</td>')
        f.write('</tr>')
    f.write('</table></p>')
    f.write('</body></html>')

    fig.suptitle('''%s,  focal length %1.2fmm, field of view %1.2f deg vertical.
    Object %1.1fm in diameter.'''%(sensors[sensor][0].rstrip(),
                                   lensfl,                                                                                                      degrees(radTheta),
                                   s))
    fig.text(0.05, .5, '''Camera height above ground, m. Constant in each row.''',
             verticalalignment='center',
             rotation=90)
    fig.text(0.5, 0.05, '''Image extent on ground, m. Green lines are bottom, center, and top of image.''',
             horizontalalignment='center')
    plt.savefig(tablename)
    print('Graphical output saved to %s.png'%tablename)
    print('Tabular output saved to %s.html'%tablename)
     
            
def html_row(cellstrings):
    '''return a html-formatted row of the elements of cellstrings'''
    return('<tr>{0}</tr>'.format(''.join(map(lambda x: '<td>{0}</td>'.format(x), cellstrings))))
    

    
if __name__ =="__main__":
    # camera constants: 
    sensor, lensfl, sensor_width, sensor_height = ask_sensor()
    radTheta = camera_subtends(sensor_height, lensfl)
    radThetaWidth = camera_subtends(sensor_width, lensfl)
    
    reports()

