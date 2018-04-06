set term pngcairo font "Helvetica,12"

set datafile separator " "

stats 'counts.dat' using 2 nooutput

set xdata time
set timefmt "%H:%M"

set boxwidth 0.125 relative
set style fill solid 0.2 transparent

set key inside top left

set ytics 1
set xlabel "Time"
set yrange [0:STATS_max+0.5]
set xrange ["7:00":"19:00"]

set title date



set output "counts.png"
plot "counts.dat" using 1:2 with filledcurves x1 lt rgb "#67a9cf" notitle, \
     '' using 1:2 with lines lt rgb "#67a9cf" lw 3 title "Eggs", \
     '' using 1:3 with boxes lt rgb "#ef8a62" lw 3 title "Hens"