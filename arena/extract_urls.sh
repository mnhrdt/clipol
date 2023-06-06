cat denoisers.txt | grep http | while read x; do
	echo $x; curl $x 2>/dev/null | grep -iE 'zip|gz' | tail -n 1 | grep -o '".*"' | sed 's/"//g'
done | paste -sd ' \n' | tr -d ' ' > urls.txt
