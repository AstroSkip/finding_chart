import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from astropy.visualization import simple_norm
import ps1getter as ps1
from astropy.table import Table
import requests
import time
from io import StringIO

def wcs_to_pixel(wcs, ra, dec):
    return wcs.all_world2pix(ra, dec, 0)

def finder_chart(target_ra, target_dec, scale_bar_length, output_file, filt, sn_name):
    # Read the FITS file
    t0 = time.time()

    table = ps1.getimages(target_ra,target_dec,filters=filt)
    print("{:.1f} s: got list of {} images for {} positions".format(time.time()-t0,len(table),len(target_ra)))
    table.sort(['projcell','subcell','filter'])

    # extract cutout for each position/filter combination
    for row in table:
        ra = row['ra']
        dec = row['dec']
        projcell = row['projcell']
        subcell = row['subcell']
        filter = row['filter']

        # create a name for the image 
        fname = "t{:08.4f}{:+07.4f}.{}.fits".format(ra,dec,filter)

        url = row["url"]
        print("%11.6f %10.6f skycell.%4.4d.%3.3d %s" % (ra, dec, projcell, subcell, fname))
        r = requests.get(url)
        open(fname,"wb").write(r.content)
    print("{:.1f} s: retrieved {} FITS files for {} positions".format(time.time()-t0,len(table),len(target_ra)))

    with fits.open(fname) as hdul:
        data = hdul[0].data
        wcs = WCS(hdul[0].header)

    # Convert target celestial coordinates to pixel coordinates
    target_position = wcs_to_pixel(wcs, target_ra, target_dec)
    print(target_position)

    # Get the dimensions of the image
    height, width = data.shape

    the_norm = simple_norm(data,'sqrt', invalid = 0,min_percent = 5, max_percent = 99)

    # Plot the image
    plt.imshow(data, cmap='Greys', origin='lower', norm = the_norm)#, extent=[0, width, 0, height])

    # Add a marker for the target position
    plt.scatter(target_position[0], target_position[1], color='red', marker='o', label=sn_name, facecolor = 'none', s = 15)

    # Add a scale bar
    scale_bar_length_pixels = scale_bar_length / 0.25#wcs.pixel_scale_matrix[0, 0]  # Convert length to pixels
    scale_bar_x =  0.7 * width
    scale_bar_y =  0.1 * height
    plt.plot([scale_bar_x, scale_bar_x + scale_bar_length_pixels], [scale_bar_y, scale_bar_y], color='white', linewidth=2)
    plt.text(scale_bar_x + 0.5 * scale_bar_length_pixels, scale_bar_y + 0.02 * height, f'{scale_bar_length} arcsec', color='white', ha='center')

    # Add arrows for North and East
    arrow_length = 0.1 * min(width, height)
    plt.arrow(0.25 * width, 0.1 * height, 0, arrow_length, color='white', width=0.002 * height, head_width=0.004 * height, head_length=0.04 * height)
    plt.arrow(0.25 * width, 0.1 * height, -arrow_length, 0, color='white', width=0.002 * height, head_width=0.004 * height, head_length=0.04 * height)

    # Add labels for North and East
    plt.text(0.25 * width, 0.21 * height + arrow_length, 'N', color='white', ha='center', va='center', fontsize=12, fontweight='bold')
    plt.text(0.2 * width - arrow_length, 0.1 * height, 'E', color='white', ha='center', va='center', fontsize=12, fontweight='bold')

    # Add labels and legend
    plt.xlabel('X-axis (pixels)')
    plt.ylabel('Y-axis (pixels)')
    plt.legend()

    # Save the finding chart
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()

