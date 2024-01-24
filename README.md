# finding_chart
handy finding chart maker 

using coordinates (in degrees), finding_chart.py will query the PS1 image cut-out service and spit out a decent enough finding chart.

(requires ps1getter.py from the cutout service)

Example:

sn_name = 'SN2005ip'
target_ra = 143.02675     
target_dec = +8.44567  
scale_bar_length = 20  # in arcseconds
output_file = sn_name + '_finding_chart.png'
filt = 'r' # choose from grizy

create_finding_chart_auto([target_ra], [target_dec], scale_bar_length, output_file, filt, sn_name)



